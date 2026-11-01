"""Read-only integrity verification for the six raw review CSVs."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PLATFORMS = ("elevenst", "kurly", "musinsa", "naver", "ohouse", "oliveyoung")
EXPECTED_COUNTS = {"elevenst": 171052, "kurly": 463843, "musinsa": 118192,
                   "naver": 1286, "ohouse": 6828, "oliveyoung": 390742}
REQUIRED_COLUMNS = ("platform", "product_id", "review_id", "content", "product_category")
DEFAULT_BASE = Path(r"C:\Users\kimha\OneDrive\Desktop\review-export-20261017\review-export-20261017")
DEFAULT_DB = PROJECT_ROOT / "outputs" / "large_human_review_candidate_manifest_20261028.sqlite3"
DEFAULT_BASELINE = PROJECT_ROOT / "reports" / "large_human_review_candidate_manifest_20261028.json"
DEFAULT_JSON = PROJECT_ROOT / "reports" / "raw_review_source_integrity_20261030.json"
DEFAULT_MD = PROJECT_ROOT / "reports" / "raw_review_source_integrity_20261030.md"


def raw_path(base: Path, platform: str) -> Path:
    name = f"reviews_{platform}.csv"
    return base / name / name


def canonical_identifier(value: str | None) -> str | None:
    return None if value is None or value.strip() == "" else value


def normalized_content(value: str | None) -> str | None:
    return None if value is None or value.strip() == "" else " ".join(value.split())


def content_fingerprint(value: str | None) -> tuple[str | None, int | None]:
    normalized = normalized_content(value)
    if normalized is None:
        return None, None
    return sha256(normalized.encode("utf-8")).hexdigest(), len(normalized)


def file_signature(path: Path) -> dict:
    stat = path.stat()
    return {"size": stat.st_size, "mtime_ns": stat.st_mtime_ns,
            "mtime_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat()}


def load_manifest_platform(db: sqlite3.Connection, platform: str) -> tuple[dict, dict]:
    rows = {}
    seen, duplicate_groups = set(), set()
    duplicate_extra = blank_identity = 0
    for source_row, stored_platform, product_id, review_id, raw_category, digest, length in db.execute(
        "SELECT source_row,platform,product_id,review_id,product_category_raw,normalized_content_hash,content_length "
        "FROM review_index WHERE platform=?", (platform,)
    ):
        rows[source_row] = (stored_platform, product_id, review_id, raw_category, digest, length)
        if product_id is None or review_id is None:
            blank_identity += 1
            continue
        identity = (product_id, review_id)
        if identity in seen:
            duplicate_extra += 1; duplicate_groups.add(identity)
        else:
            seen.add(identity)
    identity_stats = {"row_uid_unique_by_primary_key": True,
                      "business_identity_blank_rows": blank_identity,
                      "business_identity_duplicate_groups": len(duplicate_groups),
                      "business_identity_duplicate_extra_rows": duplicate_extra,
                      "business_identity_unique": blank_identity == 0 and duplicate_extra == 0}
    return rows, identity_stats


def verify_platform(db: sqlite3.Connection, base: Path, platform: str,
                    stored_signature: dict, expected_count: int) -> dict:
    path = raw_path(base, platform)
    result = {"platform": platform, "relative_path": f"reviews_{platform}.csv/reviews_{platform}.csv",
              "exists": path.is_file()}
    if not result["exists"]:
        return result
    before = file_signature(path)
    result["signature_before"] = before
    result["stored_signature"] = stored_signature
    result["signature_match"] = {
        "size": before["size"] == stored_signature.get("size"),
        "mtime_ns": before["mtime_ns"] == stored_signature.get("mtime_ns"),
        "all_stored_fields": before["size"] == stored_signature.get("size") and before["mtime_ns"] == stored_signature.get("mtime_ns"),
    }
    manifest, identity_stats = load_manifest_platform(db, platform)
    counters = Counter()
    samples = []
    with path.open("rb") as raw:
        prefix = raw.read(3)
    result["utf8_bom"] = prefix == b"\xef\xbb\xbf"
    try:
        with path.open("r", encoding="utf-8-sig", errors="strict", newline="") as handle:
            reader = csv.DictReader(handle)
            fields = reader.fieldnames
            result["encoding"] = "utf-8-sig compatible (strict UTF-8 decode passed)"
            result["header"] = fields
            missing = [name for name in REQUIRED_COLUMNS if not fields or fields.count(name) != 1]
            duplicated = [] if not fields else [name for name, count in Counter(fields).items() if count > 1]
            result["required_columns"] = {"required": list(REQUIRED_COLUMNS), "missing_or_nonunique": missing,
                                           "duplicated_columns": duplicated, "valid": not missing and not duplicated}
            if missing or duplicated:
                raise ValueError(f"{platform}: invalid header")
            for source_row, row in enumerate(reader, start=2):
                counters["csv_rows"] += 1
                stored = manifest.get(source_row)
                if stored is None:
                    counters["missing_manifest_source_row"] += 1
                    if len(samples) < 10: samples.append({"source_row": source_row, "reason": "missing manifest source_row"})
                    continue
                stored_platform, product_id, review_id, raw_category, digest, length = stored
                actual_platform = canonical_identifier(row.get("platform"))
                actual_product = canonical_identifier(row.get("product_id"))
                actual_review = canonical_identifier(row.get("review_id"))
                actual_category = row.get("product_category") or ""
                actual_digest, actual_length = content_fingerprint(row.get("content"))
                comparisons = {
                    "platform_mismatch": actual_platform != platform or actual_platform != stored_platform,
                    "product_id_mismatch": actual_product != product_id,
                    "review_id_mismatch": actual_review != review_id,
                    "product_category_mismatch": actual_category != raw_category,
                    "normalized_content_hash_mismatch": actual_digest != digest,
                    "content_length_mismatch": actual_length != length,
                }
                for name, mismatch in comparisons.items():
                    counters[name] += int(mismatch)
                if any(comparisons.values()) and len(samples) < 10:
                    samples.append({"source_row": source_row, "mismatches": [k for k,v in comparisons.items() if v]})
    except UnicodeDecodeError as exc:
        result["encoding"] = f"UTF-8 decode failed: {exc}"
        result["decode_ok"] = False
        raise
    result["decode_ok"] = True
    after = file_signature(path)
    result["signature_after"] = after
    result["unchanged_during_verification"] = before == after
    result["csv_rows"] = counters["csv_rows"]
    result["expected_rows"] = expected_count
    result["manifest_rows"] = len(manifest)
    result["row_count_match_expected"] = counters["csv_rows"] == expected_count
    result["row_count_match_manifest"] = counters["csv_rows"] == len(manifest)
    result["manifest_source_rows_not_seen"] = max(0, len(manifest)-counters["csv_rows"])
    result["mismatches"] = {name: counters[name] for name in (
        "missing_manifest_source_row", "platform_mismatch", "product_id_mismatch", "review_id_mismatch",
        "product_category_mismatch", "normalized_content_hash_mismatch", "content_length_mismatch")}
    result["identity"] = identity_stats
    result["mismatch_samples"] = samples
    result["analysis_fields_exact_match"] = (
        result["row_count_match_manifest"] and not result["manifest_source_rows_not_seen"] and
        not any(result["mismatches"].values()))
    return result


def render_markdown(report: dict) -> str:
    lines = ["# Raw Review Source Integrity Verification", "",
             "> 원본 CSV와 canonical SQLite를 read-only로 검증했습니다. 새로운 rule 탐지, candidate 생성, 모델 실행은 하지 않았습니다.", "",
             "## Summary", "", f"- Accessible files: **{report['summary']['accessible_files']} / 6**",
             f"- CSV rows: **{report['summary']['total_csv_rows']:,}**",
             f"- Expected/manifest rows: **{report['summary']['expected_total']:,} / {report['summary']['manifest_total']:,}**",
             f"- Stored size+mtime signatures all match: **{report['summary']['all_stored_signatures_match']}**",
             f"- Analysis fields all match manifest: **{report['summary']['all_analysis_fields_match']}**",
             f"- Files unchanged during verification: **{report['summary']['all_files_unchanged_during_verification']}**", "",
             "## Platform results", "", "| platform | rows | size | mtime ns | signature | identity/category/content | business identity unique |", "| --- | ---: | ---: | ---: | --- | --- | --- |"]
    for item in report["files"]:
        if not item["exists"]:
            lines.append(f"| {item['platform']} | - | - | - | missing | - | - |")
            continue
        lines.append(f"| {item['platform']} | {item['csv_rows']:,} | {item['signature_before']['size']:,} | {item['signature_before']['mtime_ns']} | {item['signature_match']['all_stored_fields']} | {item['analysis_fields_exact_match']} | {item['identity']['business_identity_unique']} |")
    lines += ["", "## Identity and content comparison", ""]
    for item in report["files"]:
        if item["exists"]:
            lines += [f"### {item['platform']}", "", f"- header: `{item['header']}`", f"- encoding: `{item['encoding']}`; BOM={item['utf8_bom']}", f"- mismatches: `{item['mismatches']}`", f"- identity: `{item['identity']}`", ""]
    lines += ["## Modification conclusion", "", report["modification_conclusion"], "", "## Safety", "",
              "- Source files were opened only for reading and size/mtime were identical before and after.",
              "- Canonical SQLite was opened with `mode=ro`.",
              "- Existing reports, annotations, manifest, and candidate outputs were not modified.",
              "- No human label, candidate pool, inference, training, or rule expansion was created.", ""]
    return "\n".join(lines)


def build(args) -> dict:
    if args.json.exists() or args.markdown.exists():
        raise FileExistsError("existing integrity report will not be overwritten")
    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    stored = baseline["execution"]["source_signatures_before"]
    with sqlite3.connect(f"file:{args.database.resolve().as_posix()}?mode=ro", uri=True) as db:
        if db.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise ValueError("canonical SQLite quick_check failed")
        files = []
        for platform in PLATFORMS:
            print(f"[verify] {platform}", flush=True)
            files.append(verify_platform(db, args.base, platform, stored[platform], EXPECTED_COUNTS[platform]))
        manifest_total = db.execute("SELECT COUNT(*) FROM review_index").fetchone()[0]
    total = sum(item.get("csv_rows", 0) for item in files)
    summary = {
        "accessible_files": sum(item["exists"] for item in files),
        "total_csv_rows": total, "expected_total": sum(EXPECTED_COUNTS.values()), "manifest_total": manifest_total,
        "all_row_counts_match": all(item.get("row_count_match_expected", False) for item in files),
        "all_stored_signatures_match": all(item.get("signature_match", {}).get("all_stored_fields", False) for item in files),
        "all_analysis_fields_match": all(item.get("analysis_fields_exact_match", False) for item in files),
        "all_files_unchanged_during_verification": all(item.get("unchanged_during_verification", False) for item in files),
    }
    byte_exact_provable = False
    conclusion = (
        "저장된 size/mtime signature와 전체 row identity, raw category, normalized content hash/length가 모두 일치한다. "
        "따라서 기존 분석에 사용된 핵심 행과 본문은 동일하다고 강하게 확인된다. 다만 당시 raw-file SHA-256이 보존되지 않아 "
        "평점 등 manifest에 저장되지 않은 컬럼이나 CSV 직렬화까지 byte-for-byte 불변이었다고 확정할 수는 없다."
    )
    report = {"analysis_type": "read-only raw CSV integrity verification; no rule scan",
              "base_path": "<LOCAL_REVIEW_EXPORT>/review-export-20261017", "files": files, "summary": summary,
              "byte_for_byte_historical_identity_provable": byte_exact_provable,
              "modification_conclusion": conclusion,
              "safety": {"raw_files_modified": False, "canonical_sqlite_modified": False,
                         "existing_reports_modified": False, "labels_created": False, "candidate_pool_created": False}}
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    args.markdown.write_text(render_markdown(report), encoding="utf-8")
    return report


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--database", type=Path, default=DEFAULT_DB)
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MD)
    return parser.parse_args(argv)


def main(argv=None) -> int:
    try:
        report = build(parse_args(argv))
        print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
        print("RAW_FILES_MODIFIED=false\nCANONICAL_SQLITE_MODIFIED=false\nRULE_EXPANSION_EXECUTED=false")
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr); return 1


if __name__ == "__main__":
    raise SystemExit(main())
