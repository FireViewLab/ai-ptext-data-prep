"""Build a V2 description-candidate CSV for human review only.

The source candidate CSV is read-only.  HIGH/MEDIUM are analyzer tiers, not
SUSPICIOUS/NORMAL labels, and every human-review field is intentionally blank.
"""

import argparse
from collections import Counter
import csv
from hashlib import sha256
import json
from pathlib import Path
import sys

from analyze_new_review_inventory import normalize_content
from analyze_ptext_description_candidates import HIGH, MEDIUM, NOT_CANDIDATE, analyze_text
from inspect_reviews import PROJECT_ROOT


SOURCE_REQUIRED_COLUMNS = (
    "candidate_id", "content_sha256", "tier", "platform", "product_id",
    "review_id", "content", "baseline_content_overlap",
)
CSV_COLUMNS = (
    "candidate_id", "v1_tier", "v2_tier", "content_sha256", "platform",
    "product_id", "review_id", "content", "character_length",
    "description_signal_count", "description_signals", "description_evidence",
    "personal_experience_signal_count", "personal_experience_signals",
    "candidate_reason", "baseline_content_overlap", "human_label",
    "pattern_type", "review_note",
)
CANDIDATE_TIERS = (HIGH, MEDIUM)
TIER_ORDER = {HIGH: 0, MEDIUM: 1}
PLATFORM_ORDER = ("elevenst", "kurly", "musinsa", "naver", "ohouse", "oliveyoung")
KNOWN_REMOVED_REGRESSIONS = (
    "NEW-DESC-000005", "NEW-DESC-000026", "NEW-DESC-000047",
)


def file_sha256(path):
    digest = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_source(path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None:
            raise ValueError("source CSV header가 없습니다.")
        if len(set(reader.fieldnames)) != len(reader.fieldnames):
            raise ValueError("source CSV에 중복된 컬럼명이 있습니다.")
        missing = [name for name in SOURCE_REQUIRED_COLUMNS if name not in reader.fieldnames]
        if missing:
            raise ValueError(f"source CSV 필수 컬럼이 없습니다: {', '.join(missing)}")
        return list(reader)


def evaluate_rows(source_rows):
    records = []
    evaluations = {}
    seen_ids = set()
    for source_row, row in enumerate(source_rows, start=2):
        candidate_id = row["candidate_id"]
        if not candidate_id:
            raise ValueError(f"source row {source_row}: candidate_id가 비어 있습니다.")
        if candidate_id in seen_ids:
            raise ValueError(f"중복 candidate_id: {candidate_id}")
        seen_ids.add(candidate_id)
        normalized = normalize_content(row["content"])
        if normalized is None:
            raise ValueError(f"{candidate_id}: content가 비어 있습니다.")
        analysis = analyze_text(row["content"])
        evaluations[candidate_id] = {
            "v1_tier": row["tier"],
            "v2_tier": analysis.candidate_tier,
            "personal_experience_signals": list(analysis.personal_experience_signals),
        }
        if analysis.candidate_tier not in CANDIDATE_TIERS:
            continue
        records.append({
            "candidate_id": candidate_id,
            "v1_tier": row["tier"],
            "v2_tier": analysis.candidate_tier,
            "content_sha256": row["content_sha256"],
            "platform": row["platform"],
            "product_id": row["product_id"],
            "review_id": row["review_id"],
            "content": row["content"],
            "character_length": len(normalized),
            "description_signal_count": analysis.description_signal_count,
            "description_signals": "|".join(analysis.description_signals),
            "description_evidence": json.dumps(
                {
                    name: analysis.matches[name]
                    for name in analysis.description_signals
                },
                ensure_ascii=False,
                separators=(",", ":"),
            ),
            "personal_experience_signal_count": analysis.personal_experience_signal_count,
            "personal_experience_signals": "|".join(analysis.personal_experience_signals),
            "candidate_reason": "|".join(analysis.candidate_reasons),
            "baseline_content_overlap": row["baseline_content_overlap"],
            "human_label": "",
            "pattern_type": "",
            "review_note": "",
            "_normalized_content": normalized,
        })
    records.sort(key=lambda item: (TIER_ORDER[item["v2_tier"]], item["candidate_id"]))
    return records, evaluations


def public_records(records):
    return [{name: record[name] for name in CSV_COLUMNS} for record in records]


def build_summary(source_path, source_digest, source_rows, records, evaluations):
    tier_counts = Counter(record["v2_tier"] for record in records)
    platform_counts = Counter(
        (record["platform"], record["v2_tier"]) for record in records
    )
    source_platforms = {row["platform"] for row in source_rows}
    platforms = [*PLATFORM_ORDER]
    platforms.extend(sorted(source_platforms - set(platforms)))
    v1_total = len(source_rows)
    survivor_total = len(records)
    excluded = v1_total - survivor_total
    normalized_contents = [record["_normalized_content"] for record in records]
    ids = [record["candidate_id"] for record in records]
    return {
        "analysis_type": "V2 HIGH/MEDIUM human-review pool; analyzer tiers are not labels",
        "source": {
            "path": str(source_path),
            "sha256": source_digest,
            "v1_candidate_rows": v1_total,
        },
        "counts": {
            "v1_total": v1_total,
            "v2_high": tier_counts[HIGH],
            "v2_medium": tier_counts[MEDIUM],
            "v2_not_candidate": excluded,
            "v2_survivor_total": survivor_total,
            "reduction_count": excluded,
            "reduction_percentage": excluded / v1_total if v1_total else 0.0,
        },
        "platform_distribution": {
            platform: {
                "HIGH": platform_counts[platform, HIGH],
                "MEDIUM": platform_counts[platform, MEDIUM],
                "TOTAL": platform_counts[platform, HIGH] + platform_counts[platform, MEDIUM],
            }
            for platform in platforms
        },
        "integrity": {
            "candidate_id_duplicates": len(ids) - len(set(ids)),
            "normalized_content_duplicates": len(normalized_contents) - len(set(normalized_contents)),
            "blank_human_label": sum(not record["human_label"] for record in records),
            "blank_pattern_type": sum(not record["pattern_type"] for record in records),
            "blank_review_note": sum(not record["review_note"] for record in records),
            "high_rows_are_contiguous_first": all(
                record["v2_tier"] == HIGH
                for record in records[:tier_counts[HIGH]]
            ),
        },
        "regression_sanity": {
            candidate_id: {
                "v1_tier": evaluations.get(candidate_id, {}).get("v1_tier"),
                "v2_tier": evaluations.get(candidate_id, {}).get("v2_tier"),
                "excluded_from_review_pool": candidate_id not in set(ids),
            }
            for candidate_id in KNOWN_REMOVED_REGRESSIONS
        },
        "human_review_guidance": {
            "human_label_allowed": ["SUSPICIOUS", "NORMAL", "UNCERTAIN"],
            "pattern_type_examples": [
                "PRODUCT_DESCRIPTION_REPLACEMENT", "OTHER", "UNKNOWN",
            ],
            "fields_are_automatically_filled": False,
        },
        "candidate_manifest": [
            {
                "candidate_id": record["candidate_id"],
                "v2_tier": record["v2_tier"],
                "platform": record["platform"],
                "content_sha256": record["content_sha256"],
            }
            for record in records
        ],
    }


def validate_consistency(source_rows, records, summary):
    counts = summary["counts"]
    ids = [record["candidate_id"] for record in records]
    normalized = [record["_normalized_content"] for record in records]
    assert counts["v1_total"] == len(source_rows)
    assert counts["v2_survivor_total"] == len(records)
    assert counts["v2_not_candidate"] + len(records) == len(source_rows)
    assert counts["v2_high"] == sum(record["v2_tier"] == HIGH for record in records)
    assert counts["v2_medium"] == sum(record["v2_tier"] == MEDIUM for record in records)
    assert len(ids) == len(set(ids))
    assert len(normalized) == len(set(normalized))
    assert records == sorted(
        records, key=lambda item: (TIER_ORDER[item["v2_tier"]], item["candidate_id"])
    )
    assert all(not record["human_label"] for record in records)
    assert all(not record["pattern_type"] for record in records)
    assert all(not record["review_note"] for record in records)
    assert all(record["personal_experience_signal_count"] == 0 for record in records)
    assert sum(item["TOTAL"] for item in summary["platform_distribution"].values()) == len(records)
    assert [item["candidate_id"] for item in summary["candidate_manifest"]] == ids


def render_markdown(summary):
    counts = summary["counts"]
    integrity = summary["integrity"]
    lines = [
        "# P_text Description Candidate — V2 Human Review Pool", "",
        "이 결과는 사람이 직접 검토할 HIGH/MEDIUM 후보입니다. HIGH/MEDIUM은 ",
        "SUSPICIOUS/NORMAL 라벨이 아니며 자동 라벨링을 수행하지 않았습니다.", "",
        "## Counts", "",
        "| metric | count |", "| --- | ---: |",
        f"| V1 candidate pool | {counts['v1_total']:,} |",
        f"| V2 HIGH | {counts['v2_high']:,} |",
        f"| V2 MEDIUM | {counts['v2_medium']:,} |",
        f"| V2 NOT_CANDIDATE | {counts['v2_not_candidate']:,} |",
        f"| V2 survivor total | {counts['v2_survivor_total']:,} |",
        f"| Reduction | {counts['reduction_count']:,} ({counts['reduction_percentage']:.2%}) |",
        "", "## Platform distribution", "",
        "| platform | HIGH | MEDIUM | TOTAL |", "| --- | ---: | ---: | ---: |",
    ]
    for platform, item in summary["platform_distribution"].items():
        lines.append(
            f"| {platform} | {item['HIGH']:,} | {item['MEDIUM']:,} | {item['TOTAL']:,} |"
        )
    lines += [
        "", "플랫폼 분포는 suspicious prevalence가 아니라 후보 pool의 구성입니다.",
        "", "## Integrity", "",
        f"- candidate_id duplicates: {integrity['candidate_id_duplicates']:,}",
        f"- normalized-content duplicates: {integrity['normalized_content_duplicates']:,}",
        f"- blank human_label: {integrity['blank_human_label']:,}",
        f"- blank pattern_type: {integrity['blank_pattern_type']:,}",
        f"- blank review_note: {integrity['blank_review_note']:,}",
        f"- HIGH rows contiguous first: {integrity['high_rows_are_contiguous_first']}",
        "", "## Human review guidance", "",
        "사람이 `human_label`에 입력할 수 있는 값:", "",
        "- `SUSPICIOUS`", "- `NORMAL`", "- `UNCERTAIN`", "",
        "`pattern_type` 예시:", "",
        "- `PRODUCT_DESCRIPTION_REPLACEMENT`", "- `OTHER`", "- `UNKNOWN`", "",
        "CSV의 `human_label`, `pattern_type`, `review_note`는 모두 빈 칸입니다.",
        "", "## Regression sanity", "",
        "| candidate_id | V1 | V2 | excluded |", "| --- | --- | --- | --- |",
    ]
    for candidate_id, item in summary["regression_sanity"].items():
        lines.append(
            f"| {candidate_id} | {item['v1_tier']} | {item['v2_tier']} | "
            f"{item['excluded_from_review_pool']} |"
        )
    lines += [
        "", "## Safety", "",
        "- 입력 574건 CSV를 read-only로 재평가했습니다.",
        "- 1.15M raw review를 재스캔하지 않았습니다.",
        "- 모델 inference, training, embedding, fuzzy matching, LLM labeling을 수행하지 않았습니다.",
        "- 이 CSV는 training dataset이 아니라 human-review candidate pool입니다.", "",
    ]
    return "\n".join(lines)


def write_outputs(records, summary, csv_path, json_path, markdown_path):
    for path in (csv_path, json_path, markdown_path):
        if path.exists():
            raise ValueError(f"기존 결과를 덮어쓰지 않습니다: {path}")
    for path in (csv_path, json_path, markdown_path):
        path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("x", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_COLUMNS, extrasaction="raise")
        writer.writeheader()
        writer.writerows(public_records(records))
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    markdown_path.write_text(render_markdown(summary), encoding="utf-8")


def validate_written_outputs(csv_path, json_path, markdown_path, summary):
    with csv_path.open("r", encoding="utf-8-sig", newline="") as stream:
        written_rows = list(csv.DictReader(stream))
    written_summary = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    counts = summary["counts"]
    assert len(written_rows) == counts["v2_survivor_total"]
    assert written_summary["counts"] == counts
    assert Counter(row["v2_tier"] for row in written_rows)[HIGH] == counts["v2_high"]
    assert Counter(row["v2_tier"] for row in written_rows)[MEDIUM] == counts["v2_medium"]
    assert written_summary["platform_distribution"] == summary["platform_distribution"]
    assert [row["candidate_id"] for row in written_rows] == [
        item["candidate_id"] for item in written_summary["candidate_manifest"]
    ]
    assert f"| V2 survivor total | {counts['v2_survivor_total']:,} |" in markdown


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="현재 V2 analyzer로 기존 후보를 재평가해 사람 검토 CSV를 생성"
    )
    parser.add_argument(
        "--source", type=Path,
        default=PROJECT_ROOT / "outputs" / "new_description_candidates_20261018.csv",
    )
    parser.add_argument(
        "--csv", type=Path,
        default=PROJECT_ROOT / "outputs" / "description_human_review_pool_v2_20261021.csv",
    )
    parser.add_argument(
        "--json", type=Path,
        default=PROJECT_ROOT / "reports" / "description_human_review_pool_v2_20261021.json",
    )
    parser.add_argument(
        "--report", type=Path,
        default=PROJECT_ROOT / "reports" / "description_human_review_pool_v2_20261021.md",
    )
    return parser.parse_args(argv)


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")
    args = parse_args(argv)
    source_path = args.source.expanduser().resolve()
    csv_path = args.csv.expanduser().resolve()
    json_path = args.json.expanduser().resolve()
    markdown_path = args.report.expanduser().resolve()
    try:
        if not source_path.is_file():
            raise ValueError(f"source CSV가 없습니다: {source_path}")
        if source_path in (csv_path, json_path, markdown_path):
            raise ValueError("source CSV를 output으로 덮어쓸 수 없습니다.")
        before_digest = file_sha256(source_path)
        source_rows = read_source(source_path)
        records, evaluations = evaluate_rows(source_rows)
        summary = build_summary(
            source_path, before_digest, source_rows, records, evaluations
        )
        validate_consistency(source_rows, records, summary)
        if file_sha256(source_path) != before_digest:
            raise ValueError("read-only source CSV digest가 변경되었습니다.")
        write_outputs(records, summary, csv_path, json_path, markdown_path)
        validate_written_outputs(csv_path, json_path, markdown_path, summary)
        print(render_markdown(summary))
        print("\nREPORT_VALIDATION_OK")
        print(f"CSV: {csv_path}\nJSON: {json_path}\nMarkdown: {markdown_path}")
    except Exception as exc:
        print(f"오류: V2 human-review pool을 생성하지 못했습니다. {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
