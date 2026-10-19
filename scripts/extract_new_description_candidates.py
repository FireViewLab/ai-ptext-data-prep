"""Stream new reviews into a deduplicated human-review candidate pool.

HIGH and MEDIUM are analyzer tiers, never SUSPICIOUS/NORMAL labels.  This
script imports the committed precision-first analyzer unchanged, reads source
CSVs without modifying them, and stores no NOT_CANDIDATE review bodies.
"""

import argparse
from collections import Counter
import csv
from dataclasses import dataclass, field
from hashlib import sha256
import json
from pathlib import Path
import sys
import time

from analyze_new_review_inventory import (
    DEFAULT_INPUTS,
    canonical_identifier,
    normalize_content,
)
from analyze_ptext_description_candidates import (
    DESCRIPTION_SIGNALS,
    HIGH,
    MEDIUM,
    analyze_text,
)
from inspect_reviews import PROJECT_ROOT, read_reviews


CANDIDATE_TIERS = (HIGH, MEDIUM)
REQUIRED_COLUMNS = ("platform", "product_id", "review_id", "content")
CSV_COLUMNS = (
    "candidate_id", "content_sha256", "tier", "platform", "product_id", "review_id", "content",
    "character_length", "description_signal_count", "description_signals",
    "description_evidence", "personal_experience_signal_count",
    "personal_experience_signals", "candidate_reason",
    "baseline_content_overlap", "human_label", "review_note",
)
TIER_ORDER = {HIGH: 0, MEDIUM: 1}


@dataclass(frozen=True)
class Candidate:
    tier: str
    platform: str | None
    product_id: str | None
    review_id: str | None
    content: str
    normalized_content: str
    content_sha256: str
    character_length: int
    description_signals: tuple[str, ...]
    description_evidence: dict[str, tuple[str, ...]]
    personal_experience_signals: tuple[str, ...]
    candidate_reason: tuple[str, ...]
    baseline_content_overlap: bool
    source_row: int

    @property
    def canonical_key(self):
        return (
            self.platform or "", self.product_id or "", self.review_id or "",
            self.content, self.source_row,
        )


@dataclass
class ExtractionState:
    scanned_by_platform: Counter = field(default_factory=Counter)
    raw_by_platform_tier: Counter = field(default_factory=Counter)
    raw_by_tier: Counter = field(default_factory=Counter)
    raw_overlap_by_tier: Counter = field(default_factory=Counter)
    raw_signal_by_tier: Counter = field(default_factory=Counter)
    raw_personal_candidate_rows: int = 0
    malformed_rows: int = 0
    candidates_by_content: dict[str, Candidate] = field(default_factory=dict)

    @property
    def scanned_rows(self):
        return sum(self.scanned_by_platform.values())


def load_baseline_contents(path):
    frame, _, _, _ = read_reviews(path)
    return {
        normalized
        for content in frame["content"]
        if (normalized := normalize_content(content)) is not None
    }


def stable_content_hash(normalized_content):
    return sha256(normalized_content.encode("utf-8")).hexdigest()


def make_candidate(row, source_row, baseline_contents):
    content = row.get("content")
    normalized = normalize_content(content)
    if normalized is None:
        return None
    analysis = analyze_text(content)
    if analysis.candidate_tier not in CANDIDATE_TIERS:
        return None
    return Candidate(
        tier=analysis.candidate_tier,
        platform=canonical_identifier(row.get("platform")),
        product_id=canonical_identifier(row.get("product_id")),
        review_id=canonical_identifier(row.get("review_id")),
        content=content,
        normalized_content=normalized,
        content_sha256=stable_content_hash(normalized),
        character_length=len(normalized),
        description_signals=analysis.description_signals,
        description_evidence={
            name: analysis.matches[name] for name in analysis.description_signals
        },
        personal_experience_signals=analysis.personal_experience_signals,
        candidate_reason=analysis.candidate_reasons,
        baseline_content_overlap=normalized in baseline_contents,
        source_row=source_row,
    )


def collect_candidate(state, candidate):
    state.raw_by_tier[candidate.tier] += 1
    state.raw_by_platform_tier[candidate.platform, candidate.tier] += 1
    state.raw_overlap_by_tier[candidate.tier, candidate.baseline_content_overlap] += 1
    for signal in candidate.description_signals:
        state.raw_signal_by_tier[candidate.tier, signal] += 1
    state.raw_personal_candidate_rows += bool(candidate.personal_experience_signals)
    current = state.candidates_by_content.get(candidate.normalized_content)
    if current is None or candidate.canonical_key < current.canonical_key:
        state.candidates_by_content[candidate.normalized_content] = candidate


def process_rows(state, source, fieldnames, rows, baseline_contents, limit=None):
    missing = [name for name in REQUIRED_COLUMNS if fieldnames.count(name) != 1]
    if missing:
        raise ValueError(f"{source}: 필수 컬럼이 없거나 중복입니다: {', '.join(missing)}")
    if len(set(fieldnames)) != len(fieldnames):
        raise ValueError(f"{source}: 중복된 컬럼명이 있습니다.")
    for source_row, row in enumerate(rows, start=2):
        if limit is not None and state.scanned_by_platform[source] >= limit:
            break
        state.scanned_by_platform[source] += 1
        if None in row or any(row.get(name) is None for name in fieldnames):
            state.malformed_rows += 1
        candidate = make_candidate(row, source_row, baseline_contents)
        if candidate is not None:
            collect_candidate(state, candidate)


def scan_csvs(paths, baseline_contents, limit_per_platform=None, progress=False):
    state = ExtractionState()
    for source, path in paths.items():
        if not path.is_file():
            raise ValueError(f"입력 CSV가 없습니다: {path}")
        if progress:
            print(f"[read-only] {source} scan 시작: {path}", flush=True)
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames is None:
                raise ValueError(f"{source}: CSV header가 없습니다.")
            process_rows(
                state, source, reader.fieldnames, reader, baseline_contents,
                limit=limit_per_platform,
            )
        if progress:
            print(
                f"[완료] {source}: {state.scanned_by_platform[source]:,}행, "
                f"HIGH {state.raw_by_platform_tier[source, HIGH]:,}, "
                f"MEDIUM {state.raw_by_platform_tier[source, MEDIUM]:,}",
                flush=True,
            )
    return state


def ordered_candidates(state):
    return sorted(
        state.candidates_by_content.values(),
        key=lambda candidate: (
            TIER_ORDER[candidate.tier], candidate.platform or "",
            candidate.content_sha256, candidate.product_id or "",
            candidate.review_id or "",
        ),
    )


def candidate_records(state):
    records = []
    for number, candidate in enumerate(ordered_candidates(state), start=1):
        records.append({
            "candidate_id": f"NEW-DESC-{number:06d}",
            "content_sha256": candidate.content_sha256,
            "tier": candidate.tier,
            "platform": candidate.platform,
            "product_id": candidate.product_id,
            "review_id": candidate.review_id,
            "content": candidate.content,
            "character_length": candidate.character_length,
            "description_signal_count": len(candidate.description_signals),
            "description_signals": "|".join(candidate.description_signals),
            "description_evidence": json.dumps(
                candidate.description_evidence, ensure_ascii=False,
                separators=(",", ":"),
            ),
            "personal_experience_signal_count": len(candidate.personal_experience_signals),
            "personal_experience_signals": "|".join(candidate.personal_experience_signals),
            "candidate_reason": "|".join(candidate.candidate_reason),
            "baseline_content_overlap": candidate.baseline_content_overlap,
            "human_label": "",
            "review_note": "",
        })
    return records


def deterministic_sample(candidates, tier, limit=100):
    members = [candidate for candidate in candidates if candidate.tier == tier]
    return sorted(members, key=lambda item: item.content_sha256)[:limit]


def build_summary(state, pilot, baseline_path, source_paths, elapsed_seconds, records):
    candidates = ordered_candidates(state)
    unique_by_tier = Counter(candidate.tier for candidate in candidates)
    unique_overlap = Counter(
        (candidate.tier, candidate.baseline_content_overlap) for candidate in candidates
    )
    unique_signal = Counter(
        (candidate.tier, signal)
        for candidate in candidates
        for signal in candidate.description_signals
    )
    personal_unique = sum(bool(candidate.personal_experience_signals) for candidate in candidates)
    ids_by_hash = {record["content_sha256"]: record["candidate_id"] for record in records}
    samples = {}
    for tier in CANDIDATE_TIERS:
        samples[tier] = [
            {
                "tier": candidate.tier,
                "candidate_id": ids_by_hash[candidate.content_sha256],
                "platform": candidate.platform,
                "product_id": candidate.product_id,
                "review_id": candidate.review_id,
                "content_sha256": candidate.content_sha256,
                "content_snippet": candidate.normalized_content[:240],
                "description_signals": list(candidate.description_signals),
                "description_evidence": {
                    name: list(values)
                    for name, values in candidate.description_evidence.items()
                },
                "personal_experience_signals": list(candidate.personal_experience_signals),
            }
            for candidate in deterministic_sample(candidates, tier)
        ]
    platforms = {}
    for source in source_paths:
        total = state.scanned_by_platform[source]
        high = state.raw_by_platform_tier[source, HIGH]
        medium = state.raw_by_platform_tier[source, MEDIUM]
        platforms[source] = {
            "raw_rows": total,
            "high_raw_rows": high,
            "medium_raw_rows": medium,
            "high_ratio": high / total if total else 0.0,
            "medium_ratio": medium / total if total else 0.0,
        }
    return {
        "analysis_type": "human-review candidate discovery; HIGH/MEDIUM are not labels",
        "baseline": {"path": str(baseline_path), "normalized_content_count": len(load_baseline_contents(baseline_path))},
        "sources": {name: str(path) for name, path in source_paths.items()},
        "execution": {
            "pilot_limit_per_platform": pilot["limit_per_platform"],
            "pilot_rows": pilot["scanned_rows"],
            "pilot_high_raw_rows": pilot["high_raw_rows"],
            "pilot_medium_raw_rows": pilot["medium_raw_rows"],
            "pilot_success": True,
            "full_scanned_rows": state.scanned_rows,
            "elapsed_seconds": elapsed_seconds,
            "malformed_rows": state.malformed_rows,
        },
        "counts": {
            "high_raw_rows": state.raw_by_tier[HIGH],
            "medium_raw_rows": state.raw_by_tier[MEDIUM],
            "not_candidate_rows": state.scanned_rows - sum(state.raw_by_tier.values()),
            "high_unique_normalized_contents": unique_by_tier[HIGH],
            "medium_unique_normalized_contents": unique_by_tier[MEDIUM],
            "unique_candidate_pool": len(candidates),
        },
        "platforms": platforms,
        "baseline_overlap": {
            tier: {
                "raw_overlap_rows": state.raw_overlap_by_tier[tier, True],
                "raw_new_content_rows": state.raw_overlap_by_tier[tier, False],
                "unique_overlap_contents": unique_overlap[tier, True],
                "unique_new_contents": unique_overlap[tier, False],
            }
            for tier in CANDIDATE_TIERS
        },
        "description_signal_distribution": {
            tier: {
                signal: {
                    "raw_rows": state.raw_signal_by_tier[tier, signal],
                    "unique_contents": unique_signal[tier, signal],
                }
                for signal in DESCRIPTION_SIGNALS
            }
            for tier in CANDIDATE_TIERS
        },
        "personal_experience_sanity": {
            "raw_candidate_rows_with_personal_signal": state.raw_personal_candidate_rows,
            "unique_candidates_with_personal_signal": personal_unique,
        },
        "candidate_manifest": [
            {
                "candidate_id": record["candidate_id"],
                "content_sha256": record["content_sha256"],
                "tier": record["tier"],
                "platform": record["platform"],
            }
            for record in records
        ],
        "diagnostic_samples": samples,
    }


def percent(value):
    return f"{value:.6%}"


def render_markdown(summary):
    execution = summary["execution"]
    counts = summary["counts"]
    lines = [
        "# New review product-description candidates", "",
        "이 결과는 사람이 검토할 HIGH/MEDIUM 후보 pool입니다. HIGH/MEDIUM은 "
        "SUSPICIOUS/NORMAL 라벨이 아니며 자동 라벨링을 수행하지 않았습니다.", "",
        "## Execution", "",
        f"- Pilot: 플랫폼당 최대 {execution['pilot_limit_per_platform']:,}행, "
        f"총 {execution['pilot_rows']:,}행, 성공",
        f"- Full scan: {execution['full_scanned_rows']:,}행",
        f"- 실행시간: {execution['elapsed_seconds']:.2f}초",
        f"- malformed rows: {execution['malformed_rows']:,}",
        "- CSV streaming 방식이며 NOT_CANDIDATE 본문은 보관하지 않았습니다.", "",
        "## Candidate counts", "",
        "| tier | raw rows | unique normalized contents |",
        "| --- | ---: | ---: |",
        f"| HIGH | {counts['high_raw_rows']:,} | {counts['high_unique_normalized_contents']:,} |",
        f"| MEDIUM | {counts['medium_raw_rows']:,} | {counts['medium_unique_normalized_contents']:,} |",
        f"| NOT_CANDIDATE | {counts['not_candidate_rows']:,} | 저장하지 않음 |", "",
        f"최종 human-review pool은 normalized content 기준 {counts['unique_candidate_pool']:,}건입니다.", "",
        "## Platform distribution", "",
        "| platform | raw rows | HIGH | HIGH ratio | MEDIUM | MEDIUM ratio |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for platform, item in summary["platforms"].items():
        lines.append(
            f"| {platform} | {item['raw_rows']:,} | {item['high_raw_rows']:,} | "
            f"{percent(item['high_ratio'])} | {item['medium_raw_rows']:,} | "
            f"{percent(item['medium_ratio'])} |"
        )
    lines += ["", "후보 비율은 플랫폼 문체와 상품군의 영향을 받을 수 있으며 suspicious prevalence가 아닙니다.", "",
              "## Baseline normalized-content overlap", "",
              "| tier | raw overlap rows | raw new-content rows | unique overlap | unique new content |",
              "| --- | ---: | ---: | ---: | ---: |"]
    for tier in CANDIDATE_TIERS:
        item = summary["baseline_overlap"][tier]
        lines.append(
            f"| {tier} | {item['raw_overlap_rows']:,} | {item['raw_new_content_rows']:,} | "
            f"{item['unique_overlap_contents']:,} | {item['unique_new_contents']:,} |"
        )
    lines += ["", "Baseline overlap은 diagnostic이며 후보에서 제거하지 않았습니다.", "",
              "## Description evidence distribution", "",
              "| tier | signal | raw rows | unique contents |", "| --- | --- | ---: | ---: |"]
    for tier in CANDIDATE_TIERS:
        for signal, item in summary["description_signal_distribution"][tier].items():
            lines.append(
                f"| {tier} | {signal} | {item['raw_rows']:,} | {item['unique_contents']:,} |"
            )
    sanity = summary["personal_experience_sanity"]
    lines += ["", "## Personal-experience sanity check", "",
              f"- HIGH/MEDIUM raw rows with personal signal: {sanity['raw_candidate_rows_with_personal_signal']:,}",
              f"- Unique candidates with personal signal: {sanity['unique_candidates_with_personal_signal']:,}",
              "- 현재 analyzer 정책상 명시적 personal evidence가 있으면 NOT_CANDIDATE입니다.", "",
              "## Deterministic diagnostic samples", "",
              "Stable content SHA-256 순으로 tier별 최대 100건입니다. 이는 human label이나 정식 precision 측정이 아닙니다.", ""]
    for tier in CANDIDATE_TIERS:
        samples = summary["diagnostic_samples"][tier]
        lines += [f"### {tier} — {len(samples)}건", ""]
        if not samples:
            lines += ["- 없음", ""]
        for sample in samples:
            snippet = sample["content_snippet"].replace("\n", " ").replace("|", "&#124;")
            lines += [
                f"- `{sample['candidate_id']}` / hash `{sample['content_sha256'][:16]}` / {sample['platform']} / "
                f"product `{sample['product_id']}` / review `{sample['review_id']}`",
                f"  - signals: {', '.join(sample['description_signals'])}",
                f"  - snippet: {snippet}",
            ]
        lines.append("")
    lines += [
        "## Interpretation and safety", "",
        "- 후보 수나 플랫폼 비율을 실제 suspicious 비율로 해석하지 않습니다.",
        "- 리뷰 길이는 metadata일 뿐 tier 판정에 사용하지 않았습니다.",
        "- 동일 normalized content는 identity와 무관하게 한 행만 deterministic하게 선택했습니다.",
        "- candidate ID는 tier, platform, stable content SHA-256 정렬 후 부여했습니다.",
        "- human_label과 review_note는 빈 칸이며 자동 SUSPICIOUS/NORMAL/UNCERTAIN 값을 넣지 않았습니다.",
        "- 모델, embedding, fuzzy similarity, LLM labeling 또는 training을 실행하지 않았습니다.", "",
    ]
    return "\n".join(lines)


def write_outputs(records, summary, csv_path, json_path, markdown_path):
    for path in (csv_path, json_path, markdown_path):
        if path.exists():
            raise ValueError(f"기존 결과를 덮어쓰지 않습니다: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("x", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_COLUMNS, extrasaction="raise")
        writer.writeheader()
        writer.writerows(records)
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    markdown_path.write_text(render_markdown(summary), encoding="utf-8")


def validate_consistency(records, summary):
    counts = summary["counts"]
    record_tiers = Counter(record["tier"] for record in records)
    assert len(records) == counts["unique_candidate_pool"]
    assert record_tiers[HIGH] == counts["high_unique_normalized_contents"]
    assert record_tiers[MEDIUM] == counts["medium_unique_normalized_contents"]
    assert len({record["candidate_id"] for record in records}) == len(records)
    assert [record["candidate_id"] for record in records] == [
        f"NEW-DESC-{number:06d}" for number in range(1, len(records) + 1)
    ]
    assert [record["candidate_id"] for record in records] == [
        item["candidate_id"] for item in summary["candidate_manifest"]
    ]
    assert all(not record["human_label"] and not record["review_note"] for record in records)
    assert all(record["personal_experience_signal_count"] == 0 for record in records)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="신규 리뷰의 HIGH/MEDIUM 설명문 후보를 streaming 추출")
    parser.add_argument("--baseline", type=Path, default=PROJECT_ROOT / "outputs" / "merged_reviews.xlsx")
    parser.add_argument("--pilot-limit", type=int, default=5000)
    parser.add_argument("--csv", type=Path, default=PROJECT_ROOT / "outputs" / "new_description_candidates_20261018.csv")
    parser.add_argument("--json", type=Path, default=PROJECT_ROOT / "reports" / "new_description_candidates_20261018.json")
    parser.add_argument("--report", type=Path, default=PROJECT_ROOT / "reports" / "new_description_candidates_20261018.md")
    for source, path in DEFAULT_INPUTS.items():
        parser.add_argument(f"--{source}", type=Path, default=path)
    args = parser.parse_args(argv)
    if args.pilot_limit < 1:
        parser.error("--pilot-limit은 1 이상이어야 합니다.")
    return args


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")
    args = parse_args(argv)
    baseline_path = args.baseline.expanduser().resolve()
    paths = {source: getattr(args, source).expanduser().resolve() for source in DEFAULT_INPUTS}
    csv_path = args.csv.expanduser().resolve()
    json_path = args.json.expanduser().resolve()
    report_path = args.report.expanduser().resolve()
    try:
        for path in (csv_path, json_path, report_path):
            if path.exists():
                raise ValueError(f"기존 결과를 덮어쓰지 않습니다: {path}")
        baseline_contents = load_baseline_contents(baseline_path)
        print(f"[pilot] 플랫폼당 최대 {args.pilot_limit:,}행", flush=True)
        pilot_started = time.perf_counter()
        pilot_state = scan_csvs(
            paths, baseline_contents, limit_per_platform=args.pilot_limit, progress=True
        )
        pilot = {
            "limit_per_platform": args.pilot_limit,
            "scanned_rows": pilot_state.scanned_rows,
            "high_raw_rows": pilot_state.raw_by_tier[HIGH],
            "medium_raw_rows": pilot_state.raw_by_tier[MEDIUM],
            "elapsed_seconds": time.perf_counter() - pilot_started,
        }
        pilot_records = candidate_records(pilot_state)
        if any(tuple(record) != CSV_COLUMNS for record in pilot_records):
            raise ValueError("pilot candidate output schema가 예상과 다릅니다.")
        if any(record["personal_experience_signal_count"] for record in pilot_records):
            raise ValueError("pilot HIGH/MEDIUM 후보에 personal-experience 신호가 남았습니다.")
        if pilot_state.malformed_rows:
            raise ValueError(f"pilot malformed rows: {pilot_state.malformed_rows}")
        print(
            f"[pilot 성공] {pilot['scanned_rows']:,}행 / HIGH {pilot['high_raw_rows']:,} / "
            f"MEDIUM {pilot['medium_raw_rows']:,}", flush=True,
        )
        print("[full] pilot 결과를 섞지 않고 전체 streaming scan 시작", flush=True)
        full_started = time.perf_counter()
        state = scan_csvs(paths, baseline_contents, progress=True)
        elapsed = time.perf_counter() - full_started
        records = candidate_records(state)
        summary = build_summary(state, pilot, baseline_path, paths, elapsed, records)
        validate_consistency(records, summary)
        write_outputs(records, summary, csv_path, json_path, report_path)
        print(render_markdown(summary))
        print(f"\nCandidate CSV: {csv_path}\nJSON: {json_path}\nMarkdown: {report_path}")
    except Exception as exc:
        print(f"오류: 신규 description candidate 추출을 완료하지 못했습니다. {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
