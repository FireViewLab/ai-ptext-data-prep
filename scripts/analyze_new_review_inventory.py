"""Stream read-only CSV inventory and exact-overlap analysis.

This tool never edits source reviews, merges datasets, assigns labels, performs
fuzzy matching, or runs a model.  A temporary SQLite database keeps the scan
memory-bounded; only aggregate Markdown/JSON reports are published.
"""

import argparse
from collections import Counter
import csv
from dataclasses import dataclass, field
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import sqlite3
import sys
import tempfile

from inspect_reviews import COLUMNS as BASE_COLUMNS
from inspect_reviews import PROJECT_ROOT, is_blank, read_reviews


DEFAULT_INPUT_ROOT = Path(
    os.environ.get(
        "PTEXT_REVIEW_EXPORT_ROOT",
        str(PROJECT_ROOT / "data" / "review-export"),
    )
)
DEFAULT_INPUTS = {
    source: DEFAULT_INPUT_ROOT / f"reviews_{source}.csv"
    for source in ("elevenst", "kurly", "musinsa", "naver", "ohouse", "oliveyoung")
}
REQUIRED_COLUMNS = ("platform", "product_id", "review_id", "content", "rating")


def portable_report_path(path, external_placeholder=None):
    """Represent local paths without publishing a user-specific absolute path."""
    resolved = Path(path).expanduser().resolve()
    try:
        return resolved.relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError:
        prefix = external_placeholder or "<LOCAL_PATH>"
        return f"{prefix}/{resolved.name}"


def normalize_content(value):
    """Conservative comparison copy: stringify, strip, collapse whitespace."""
    if is_blank(value):
        return None
    return " ".join(str(value).split())


def canonical_identifier(value):
    """Follow the repo's identifier diagnostic representation policy.

    Strings are preserved exactly, including leading zeroes and a literal
    ``.0``.  Numeric integral floats become integer decimal text, preventing
    Excel's numeric 12345.0 from becoming the comparison key ``12345.0``.
    """
    if is_blank(value):
        return None
    if type(value) is str:
        return value
    if type(value) is int:
        return str(value)
    if type(value) is float:
        return str(int(value)) if math.isfinite(value) and value.is_integer() else str(value)
    return str(value)


def row_digest(fieldnames, row):
    serialized = json.dumps(
        [row.get(name) for name in fieldnames] + [row.get(None)], ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256(serialized).digest()


def increment(connection, table, columns, values):
    names = ", ".join(columns)
    placeholders = ", ".join("?" for _ in values)
    conflict = ", ".join(columns)
    connection.execute(
        f"INSERT INTO {table} ({names}, row_count) VALUES ({placeholders}, 1) "
        f"ON CONFLICT ({conflict}) DO UPDATE SET row_count = row_count + 1",
        values,
    )


def create_schema(connection):
    connection.executescript(
        """
        PRAGMA journal_mode=OFF;
        PRAGMA synchronous=OFF;
        PRAGMA temp_store=FILE;
        CREATE TABLE base_identity (
            platform TEXT NOT NULL, product_id TEXT NOT NULL,
            review_id TEXT NOT NULL, PRIMARY KEY (platform, product_id, review_id)
        ) WITHOUT ROWID;
        CREATE TABLE base_review_id (
            platform TEXT NOT NULL, review_id TEXT NOT NULL,
            PRIMARY KEY (platform, review_id)
        ) WITHOUT ROWID;
        CREATE TABLE base_content (content TEXT PRIMARY KEY) WITHOUT ROWID;
        CREATE TABLE products (
            source TEXT NOT NULL, product_id TEXT NOT NULL,
            PRIMARY KEY (source, product_id)
        ) WITHOUT ROWID;
        CREATE TABLE review_ids (
            source TEXT NOT NULL, platform TEXT NOT NULL, review_id TEXT NOT NULL,
            row_count INTEGER NOT NULL,
            PRIMARY KEY (source, platform, review_id)
        ) WITHOUT ROWID;
        CREATE TABLE review_id_products (
            source TEXT NOT NULL, platform TEXT NOT NULL, review_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            PRIMARY KEY (source, platform, review_id, product_id)
        ) WITHOUT ROWID;
        CREATE TABLE identities (
            source TEXT NOT NULL, platform TEXT NOT NULL, product_id TEXT NOT NULL,
            review_id TEXT NOT NULL, row_count INTEGER NOT NULL,
            PRIMARY KEY (source, platform, product_id, review_id)
        ) WITHOUT ROWID;
        CREATE TABLE contents (
            source TEXT NOT NULL, content TEXT NOT NULL, row_count INTEGER NOT NULL,
            PRIMARY KEY (source, content)
        ) WITHOUT ROWID;
        CREATE TABLE product_contents (
            source TEXT NOT NULL, product_id TEXT NOT NULL, content TEXT NOT NULL,
            row_count INTEGER NOT NULL,
            PRIMARY KEY (source, product_id, content)
        ) WITHOUT ROWID;
        CREATE TABLE full_rows (
            source TEXT NOT NULL, digest BLOB NOT NULL, row_count INTEGER NOT NULL,
            PRIMARY KEY (source, digest)
        ) WITHOUT ROWID;
        """
    )


@dataclass
class SourceScan:
    source: str
    path: str
    columns: list[str]
    total_rows: int = 0
    blank_content: int = 0
    blank_rating: int = 0
    short_content: int = 0
    incomplete_identity: int = 0
    malformed_rows: int = 0
    length_sum: int = 0
    length_min: int | None = None
    length_max: int | None = None
    length_histogram: Counter = field(default_factory=Counter)
    platform_values: Counter = field(default_factory=Counter)


def load_baseline(connection, path):
    frame, header_row, header_count, skipped = read_reviews(path)
    platform_counts = Counter()
    id_types = {"product_id": Counter(), "review_id": Counter()}
    for row in frame.itertuples(index=False):
        values = dict(zip(frame.columns, row))
        platform = canonical_identifier(values["platform"])
        product_id = canonical_identifier(values["product_id"])
        review_id = canonical_identifier(values["review_id"])
        platform_counts[values["platform"]] += 1
        id_types["product_id"][type(values["product_id"]).__name__] += 1
        id_types["review_id"][type(values["review_id"]).__name__] += 1
        if platform is not None and product_id is not None and review_id is not None:
            connection.execute(
                "INSERT OR IGNORE INTO base_identity VALUES (?, ?, ?)",
                (platform, product_id, review_id),
            )
        if platform is not None and review_id is not None:
            connection.execute(
                "INSERT OR IGNORE INTO base_review_id VALUES (?, ?)",
                (platform, review_id),
            )
        content = normalize_content(values["content"])
        if content is not None:
            connection.execute("INSERT OR IGNORE INTO base_content VALUES (?)", (content,))
    connection.commit()
    return {
        "path": portable_report_path(path), "sheet": "Reviews", "rows": len(frame),
        "header_row": header_row, "header_count": header_count,
        "skipped_empty_rows": skipped,
        "platform_counts": dict(platform_counts),
        "identifier_types": {name: dict(counts) for name, counts in id_types.items()},
    }


def process_rows(connection, source, path, fieldnames, rows):
    missing = [name for name in REQUIRED_COLUMNS if fieldnames.count(name) != 1]
    if missing:
        raise ValueError(f"{source}: 필수 컬럼이 없거나 중복입니다: {', '.join(missing)}")
    if len(set(fieldnames)) != len(fieldnames):
        raise ValueError(f"{source}: 중복된 컬럼명이 있습니다.")
    scan = SourceScan(
        source=source,
        path=portable_report_path(path, "<LOCAL_REVIEW_EXPORT>"),
        columns=list(fieldnames),
    )
    for row in rows:
        scan.total_rows += 1
        if None in row or any(row.get(name) is None for name in fieldnames):
            scan.malformed_rows += 1
        platform = canonical_identifier(row.get("platform"))
        product_id = canonical_identifier(row.get("product_id"))
        review_id = canonical_identifier(row.get("review_id"))
        if platform is not None:
            scan.platform_values[platform] += 1
        if product_id is not None:
            connection.execute("INSERT OR IGNORE INTO products VALUES (?, ?)", (source, product_id))
        if platform is not None and review_id is not None:
            increment(
                connection, "review_ids", ("source", "platform", "review_id"),
                (source, platform, review_id),
            )
        if platform is not None and product_id is not None and review_id is not None:
            connection.execute(
                "INSERT OR IGNORE INTO review_id_products VALUES (?, ?, ?, ?)",
                (source, platform, review_id, product_id),
            )
        if None not in (platform, product_id, review_id):
            increment(
                connection, "identities",
                ("source", "platform", "product_id", "review_id"),
                (source, platform, product_id, review_id),
            )
        else:
            scan.incomplete_identity += 1

        content = normalize_content(row.get("content"))
        if content is None:
            scan.blank_content += 1
        else:
            length = len(content)
            scan.length_sum += length
            scan.length_min = length if scan.length_min is None else min(scan.length_min, length)
            scan.length_max = length if scan.length_max is None else max(scan.length_max, length)
            scan.length_histogram[length] += 1
            scan.short_content += length < 20
            increment(connection, "contents", ("source", "content"), (source, content))
            if product_id is not None:
                increment(
                    connection, "product_contents",
                    ("source", "product_id", "content"),
                    (source, product_id, content),
                )
        scan.blank_rating += is_blank(row.get("rating"))
        increment(
            connection, "full_rows", ("source", "digest"),
            (source, row_digest(fieldnames, row)),
        )
    connection.commit()
    return scan


def process_csv(connection, source, path):
    if not path.is_file():
        raise ValueError(f"입력 CSV가 없습니다: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None:
            raise ValueError(f"CSV header가 없습니다: {path}")
        return process_rows(connection, source, path, reader.fieldnames, reader)


def scalar(connection, sql, values=()):
    return connection.execute(sql, values).fetchone()[0]


def median_from_histogram(histogram):
    count = sum(histogram.values())
    if not count:
        return None
    targets = ((count - 1) // 2, count // 2)
    found = []
    cumulative = 0
    for length, frequency in sorted(histogram.items()):
        previous = cumulative
        cumulative += frequency
        for target in targets[len(found):]:
            if previous <= target < cumulative:
                found.append(length)
            else:
                break
        if len(found) == 2:
            break
    return sum(found) / 2


def duplicate_metrics(connection, table, source):
    groups, participating, extras = connection.execute(
        f"SELECT COUNT(*), COALESCE(SUM(row_count), 0), "
        f"COALESCE(SUM(row_count - 1), 0) FROM {table} "
        "WHERE source = ? AND row_count > 1",
        (source,),
    ).fetchone()
    return {"groups": groups, "participating_rows": participating, "extra_rows": extras}


def source_metrics(connection, scan):
    source = scan.source
    valid_content = scan.total_rows - scan.blank_content
    unique_products = scalar(connection, "SELECT COUNT(*) FROM products WHERE source = ?", (source,))
    unique_review_ids = scalar(
        connection, "SELECT COUNT(DISTINCT review_id) FROM review_ids WHERE source = ?", (source,)
    )
    unique_identities = scalar(connection, "SELECT COUNT(*) FROM identities WHERE source = ?", (source,))
    content_duplicates = duplicate_metrics(connection, "contents", source)
    result = {
        "path": scan.path,
        "columns": scan.columns,
        "platform_values": dict(scan.platform_values),
        "platform_matches_expected": (
            set(scan.platform_values) == {source}
            and sum(scan.platform_values.values()) == scan.total_rows
        ),
        "total_rows": scan.total_rows,
        "unique_product_id": unique_products,
        "unique_review_id": unique_review_ids,
        "unique_product_id_review_id": unique_identities,
        "blank_content": scan.blank_content,
        "blank_rating": scan.blank_rating,
        "malformed_rows": scan.malformed_rows,
        "incomplete_identity_rows": scan.incomplete_identity,
        "exact_duplicate_full_rows": duplicate_metrics(connection, "full_rows", source),
        "duplicate_review_id": duplicate_metrics(connection, "review_ids", source),
        "review_ids_across_multiple_products": scalar(
            connection,
            "SELECT COUNT(*) FROM (SELECT platform, review_id FROM review_id_products "
            "WHERE source = ? GROUP BY platform, review_id HAVING COUNT(*) > 1)",
            (source,),
        ),
        "normalized_content_duplicates": content_duplicates,
        "same_product_normalized_content_duplicates": duplicate_metrics(
            connection, "product_contents", source
        ),
        "content_length": {
            "basis": "normalized nonblank content characters",
            "min": scan.length_min,
            "median": median_from_histogram(scan.length_histogram),
            "mean": scan.length_sum / valid_content if valid_content else None,
            "max": scan.length_max,
        },
        "under_20_chars": scan.short_content,
        "under_20_ratio": scan.short_content / valid_content if valid_content else 0.0,
    }
    result["identity_overlap_rows"] = scalar(
        connection,
        "SELECT COALESCE(SUM(i.row_count), 0) FROM identities i JOIN base_identity b "
        "ON b.platform=i.platform AND b.product_id=i.product_id AND b.review_id=i.review_id "
        "WHERE i.source=?", (source,),
    )
    result["review_id_overlap_rows"] = scalar(
        connection,
        "SELECT COALESCE(SUM(r.row_count), 0) FROM review_ids r "
        "JOIN base_review_id b ON b.platform=r.platform AND b.review_id=r.review_id "
        "WHERE r.source=?", (source,),
    )
    result["content_overlap_rows"] = scalar(
        connection,
        "SELECT COALESCE(SUM(c.row_count), 0) FROM contents c "
        "JOIN base_content b ON b.content=c.content WHERE c.source=?", (source,),
    )
    result["new_identity_rows"] = scalar(
        connection,
        "SELECT COALESCE(SUM(i.row_count), 0) FROM identities i "
        "WHERE i.source=? AND NOT EXISTS (SELECT 1 FROM base_identity b WHERE "
        "b.platform=i.platform AND b.product_id=i.product_id AND b.review_id=i.review_id)",
        (source,),
    )
    result["incoming_unique_normalized_contents"] = scalar(
        connection, "SELECT COUNT(*) FROM contents WHERE source=?", (source,)
    )
    result["new_unique_normalized_contents"] = scalar(
        connection,
        "SELECT COUNT(*) FROM contents c WHERE c.source=? AND NOT EXISTS "
        "(SELECT 1 FROM base_content b WHERE b.content=c.content)", (source,),
    )
    return result


def combined_metrics(connection, per_source):
    cross_platform = connection.execute(
        "SELECT COUNT(*), COALESCE(SUM(rows), 0) FROM ("
        "SELECT content, SUM(row_count) AS rows FROM contents "
        "GROUP BY content HAVING COUNT(*) > 1)"
    ).fetchone()
    return {
        "raw_incoming_rows": sum(item["total_rows"] for item in per_source.values()),
        "identity_overlap_rows": sum(item["identity_overlap_rows"] for item in per_source.values()),
        "content_overlap_rows": sum(item["content_overlap_rows"] for item in per_source.values()),
        "new_identity_rows": sum(item["new_identity_rows"] for item in per_source.values()),
        "identity_unclassifiable_rows": sum(item["incomplete_identity_rows"] for item in per_source.values()),
        "incoming_unique_normalized_contents": scalar(
            connection, "SELECT COUNT(DISTINCT content) FROM contents"
        ),
        "new_unique_normalized_contents": scalar(
            connection,
            "SELECT COUNT(DISTINCT c.content) FROM contents c WHERE NOT EXISTS "
            "(SELECT 1 FROM base_content b WHERE b.content=c.content)"
        ),
        "cross_platform_normalized_content_duplicate_groups": cross_platform[0],
        "cross_platform_normalized_content_participating_rows": cross_platform[1],
    }


def compatibility(per_source):
    column_sets = {tuple(item["columns"]) for item in per_source.values()}
    incoming_columns = next(iter(column_sets)) if len(column_sets) == 1 else None
    return {
        "all_incoming_columns_identical": len(column_sets) == 1,
        "incoming_columns": list(incoming_columns) if incoming_columns else None,
        "shared_with_baseline": [name for name in BASE_COLUMNS if incoming_columns and name in incoming_columns],
        "baseline_only": [name for name in BASE_COLUMNS if not incoming_columns or name not in incoming_columns],
        "incoming_only": [name for name in incoming_columns or () if name not in BASE_COLUMNS],
    }


def build_result(baseline, per_source, connection):
    return {
        "analysis_type": "read-only inventory and exact overlap; no labels or merge",
        "baseline": baseline,
        "normalization": {
            "content": "str(value), strip, collapse consecutive whitespace; preserve case, punctuation, Korean, English, and numbers",
            "identifiers": "strings unchanged; int to decimal text; integral float to integer decimal text; preserve string leading zero and literal .0",
        },
        "platform_mapping": {
            source: {
                "expected_from_filename": source,
                "observed_values": item["platform_values"],
                "exact_match": item["platform_matches_expected"],
            }
            for source, item in per_source.items()
        },
        "schema_compatibility": compatibility(per_source),
        "platforms": per_source,
        "combined": combined_metrics(connection, per_source),
    }


def fmt(value):
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:.2f}"
    return f"{value:,}" if isinstance(value, int) else str(value)


def render_markdown(result):
    baseline = result["baseline"]
    combined = result["combined"]
    lines = [
        "# 신규 리뷰 데이터 Inventory", "",
        "이 보고서는 READ-ONLY inventory와 exact overlap 진단입니다. 데이터 병합, 삭제, "
        "라벨링, fuzzy similarity, embedding, 모델 추론 또는 모델 학습을 수행하지 않았습니다.", "",
        "## 기준 데이터와 비교 정책", "",
        f"- 기준 파일: `{baseline['path']}` / 시트: `Reviews` / {baseline['rows']:,}행",
        f"- 기준 platform 값: `{baseline['platform_counts']}`",
        "- platform은 CSV 실제 값을 사용하며 파일명 기준 예상값으로 임의 치환하지 않습니다.",
        "- identity는 platform + product_id + review_id 세 값이 모두 있을 때만 비교합니다.",
        "- ID 문자열은 leading zero와 문자열 `.0`을 포함해 그대로 유지합니다. 숫자형 정수와 "
        "정수형 float만 기존 식별자 진단 정책에 따라 정수 십진 문자열로 비교합니다.",
        "- normalized content는 비어 있지 않은 값을 문자열화하고 양끝/연속 whitespace만 정리합니다. "
        "대소문자, 문장부호, 한글, 영문, 숫자는 제거하지 않습니다.", "",
        "## Platform 매핑 확인", "",
        "| 입력 파일 기준 | CSV 실제 platform 값과 행 수 | 정확히 일치 |",
        "| --- | --- | --- |",
    ]
    for source, mapping in result["platform_mapping"].items():
        lines.append(
            f"| {source} | `{mapping['observed_values']}` | {'예' if mapping['exact_match'] else '아니요'} |"
        )
    schema = result["schema_compatibility"]
    lines += [
        "", "## 구조 호환성", "",
        f"- 6개 신규 CSV 컬럼 순서/목록 동일: {'예' if schema['all_incoming_columns_identical'] else '아니요'}",
        f"- 신규 CSV 컬럼: `{schema['incoming_columns']}`",
        f"- 기준과 공통: `{schema['shared_with_baseline']}`",
        f"- 기준에만 존재: `{schema['baseline_only']}`",
        f"- 신규 CSV에만 존재: `{schema['incoming_only']}`",
        "- 핵심 platform/product_id/review_id/content/rating은 호환되지만 전체 스키마는 동일하지 않습니다. "
        "이번 분석에서는 병합하거나 컬럼을 변환하지 않았습니다.", "",
        "## 플랫폼별 Inventory", "",
        "| platform | rows | unique product | unique review | unique product+review | blank content | full-row dup extras | review-id dup extras | normalized-content dup extras | same-product content dup extras | <20 chars | rating blank |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for source, item in result["platforms"].items():
        lines.append(
            f"| {source} | {fmt(item['total_rows'])} | {fmt(item['unique_product_id'])} | "
            f"{fmt(item['unique_review_id'])} | {fmt(item['unique_product_id_review_id'])} | "
            f"{fmt(item['blank_content'])} | {fmt(item['exact_duplicate_full_rows']['extra_rows'])} | "
            f"{fmt(item['duplicate_review_id']['extra_rows'])} | "
            f"{fmt(item['normalized_content_duplicates']['extra_rows'])} | "
            f"{fmt(item['same_product_normalized_content_duplicates']['extra_rows'])} | "
            f"{fmt(item['under_20_chars'])} ({item['under_20_ratio']:.2%}) | {fmt(item['blank_rating'])} |"
        )
    lines += ["", "## Content 길이", "", "normalized nonblank content 문자 수 기준입니다.", "",
              "| platform | min | median | mean | max |", "| --- | ---: | ---: | ---: | ---: |"]
    for source, item in result["platforms"].items():
        length = item["content_length"]
        lines.append(
            f"| {source} | {fmt(length['min'])} | {fmt(length['median'])} | "
            f"{fmt(length['mean'])} | {fmt(length['max'])} |"
        )
    lines += [
        "", "## 기존 8,965건과 Exact overlap", "",
        "| platform | identity overlap rows | same-platform review_id overlap rows | normalized content overlap rows | new identity rows | new unique normalized contents |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for source, item in result["platforms"].items():
        lines.append(
            f"| {source} | {fmt(item['identity_overlap_rows'])} | "
            f"{fmt(item['review_id_overlap_rows'])} | {fmt(item['content_overlap_rows'])} | "
            f"{fmt(item['new_identity_rows'])} | {fmt(item['new_unique_normalized_contents'])} |"
        )
    lines += [
        "", "## 핵심 답변", "",
        f"1. 새 원본은 총 **{combined['raw_incoming_rows']:,}행**입니다.",
        "2. 플랫폼별 규모는 위 Inventory 표와 같습니다.",
        f"3. 신규 CSV끼리는 구조가 {'동일' if schema['all_incoming_columns_identical'] else '서로 다릅니다'}. "
        "기준 Excel과는 핵심 5개 필드는 호환되지만 전체 컬럼은 다릅니다.",
        "4. 즉시 확인할 품질 이슈는 아래 주의사항에 정리했습니다.",
        f"5. 기존 데이터와 identity가 겹치는 incoming row는 **{combined['identity_overlap_rows']:,}행**, "
        f"normalized content가 겹치는 incoming row는 **{combined['content_overlap_rows']:,}행**입니다.",
        f"6. 완전한 identity 중 기존과 겹치지 않는 incoming row는 **{combined['new_identity_rows']:,}행**입니다. "
        f"identity 판정 불가 행은 {combined['identity_unclassifiable_rows']:,}행입니다.",
        f"7. incoming 전체 normalized unique content는 **{combined['incoming_unique_normalized_contents']:,}개**, "
        f"기존에 없는 신규 normalized unique content는 **{combined['new_unique_normalized_contents']:,}개**입니다.",
        "8. candidate extraction 입력으로 활용할 수 있지만, blank/short content와 exact duplicate를 정책에 따라 "
        "별도 처리하고 스키마 매핑을 먼저 확정해야 합니다. 이번 단계에서는 처리하지 않았습니다.",
        "9. 플랫폼별 중복·결측과 구조 차이는 위 표 및 아래 주의사항을 따라야 합니다.", "",
        "## 신규 데이터 내부 플랫폼 간 exact content", "",
        f"- 2개 이상 입력 플랫폼에 등장한 normalized content 그룹: "
        f"{combined['cross_platform_normalized_content_duplicate_groups']:,}개",
        f"- 해당 그룹 참여 incoming row: "
        f"{combined['cross_platform_normalized_content_participating_rows']:,}행",
        "- 플랫폼 간 동일 문장은 삭제 또는 이상 판정 근거가 아닙니다.", "",
        "## 품질 및 사용 주의사항", "",
    ]
    for source, item in result["platforms"].items():
        lines.append(
            f"- {source}: blank content {item['blank_content']:,}, identity 불완전 "
            f"{item['incomplete_identity_rows']:,}, malformed row {item['malformed_rows']:,}, "
            f"여러 product_id에 걸친 동일 review_id {item['review_ids_across_multiple_products']:,}개."
        )
    lines += [
        "- Full-row duplicate는 CSV header 순서의 모든 파싱 문자열을 SHA-256으로 직렬화해 계산했습니다.",
        "- identity overlap과 content overlap은 서로 겹칠 수 있으므로 합산해 제거 건수로 해석하면 안 됩니다.",
        "- `new identity rows`는 identity가 완전한 행만 포함합니다. 결측 identity 행을 신규라고 임의 분류하지 않습니다.",
        "- 원문 content, 사용자 식별 정보, 전체 ID 목록은 보고서에 포함하지 않았습니다.", "",
    ]
    return "\n".join(lines)


def write_reports(result, markdown_path, json_path):
    for path in (markdown_path, json_path):
        if path.exists():
            raise ValueError(f"기존 보고서를 덮어쓰지 않습니다: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(render_markdown(result), encoding="utf-8")
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="신규 리뷰 CSV의 read-only inventory/exact overlap 분석")
    parser.add_argument("--baseline", type=Path, default=PROJECT_ROOT / "outputs" / "merged_reviews.xlsx")
    parser.add_argument("--report", type=Path, default=PROJECT_ROOT / "reports" / "new_review_inventory_20261018.md")
    parser.add_argument("--json", type=Path, default=PROJECT_ROOT / "reports" / "new_review_inventory_20261018.json")
    for source, path in DEFAULT_INPUTS.items():
        parser.add_argument(
            f"--{source}", type=Path, default=path,
            help=(
                f"{source} CSV (기본 root: PTEXT_REVIEW_EXPORT_ROOT 또는 "
                "data/review-export)"
            ),
        )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    report_path = args.report.expanduser().resolve()
    json_path = args.json.expanduser().resolve()
    try:
        if report_path.exists() or json_path.exists():
            raise ValueError("기존 inventory 보고서를 덮어쓰지 않습니다.")
        with tempfile.TemporaryDirectory(prefix="review_inventory_") as temporary:
            connection = sqlite3.connect(Path(temporary) / "inventory.sqlite")
            try:
                create_schema(connection)
                baseline = load_baseline(connection, args.baseline.expanduser().resolve())
                scans = {}
                for source in DEFAULT_INPUTS:
                    path = getattr(args, source).expanduser().resolve()
                    print(f"[read-only] {source} CSV 분석 중: {path}", flush=True)
                    scans[source] = process_csv(connection, source, path)
                    print(f"[완료] {source}: {scans[source].total_rows:,}행", flush=True)
                per_source = {source: source_metrics(connection, scan) for source, scan in scans.items()}
                result = build_result(baseline, per_source, connection)
            finally:
                connection.close()
        write_reports(result, report_path, json_path)
        print(render_markdown(result))
        print(f"\nMarkdown 보고서: {report_path}\nJSON 보고서: {json_path}")
    except Exception as exc:
        print(f"오류: inventory 분석을 완료하지 못했습니다. {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
