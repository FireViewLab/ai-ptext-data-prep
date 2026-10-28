"""Build a text-only, human-review candidate-source manifest.

This is discovery infrastructure, not a classifier.  It never writes a human
label, samples the final 10K pool, runs a model, or modifies source reviews.
The output is SQLite so weak/high-volume sources and duplicate membership can
be retained without copying every review body into a giant CSV.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from hashlib import sha256
import json
from pathlib import Path
import re
import sqlite3
import sys
import time

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from analyze_new_review_inventory import (  # noqa: E402
    DEFAULT_INPUTS, PROJECT_ROOT, canonical_identifier, normalize_content,
    portable_report_path,
)
from analyze_ptext_description_candidates import analyze_text  # noqa: E402
from analyze_review_category_strategy import (  # noqa: E402
    NORMALIZED_CATEGORIES, normalize_category, sqrt_platform_targets,
)


PRODUCT_DESCRIPTION = "PRODUCT_DESCRIPTION_REPLACEMENT"
EXTREME_RESULT = "EXTREME_RESULT_CLAIM"
IMMEDIATE_EFFECT = "IMMEDIATE_EFFECT_CLAIM"
PROMOTIONAL_TEMPLATE = "PROMOTIONAL_TEMPLATE"
LOW_INFORMATION = "LOW_INFORMATION_PRAISE"
REPEATED_SHORT = "REPEATED_SHORT_TEMPLATE"
EXACT_DUPLICATE = "EXACT_DUPLICATE_CLUSTER"
HARD_NEGATIVE = "HARD_NEGATIVE_CANDIDATE"
RANDOM_ELIGIBLE = "RANDOM_CONTROL_ELIGIBLE"

SOURCES = (
    PRODUCT_DESCRIPTION, EXTREME_RESULT, IMMEDIATE_EFFECT,
    PROMOTIONAL_TEMPLATE, LOW_INFORMATION, REPEATED_SHORT,
    EXACT_DUPLICATE, HARD_NEGATIVE,
)
SUSPICIOUS_FOCUSED = set(SOURCES) - {HARD_NEGATIVE}
REQUIRED_COLUMNS = ("platform", "product_id", "review_id", "content", "product_category")
DEFAULT_DESCRIPTION = PROJECT_ROOT / "outputs" / "new_description_candidates_20261018.csv"
DEFAULT_V2 = PROJECT_ROOT / "outputs" / "description_human_review_pool_v2_20261021.csv"
DEFAULT_DB = PROJECT_ROOT / "outputs" / "large_human_review_candidate_manifest_20261028.sqlite3"
DEFAULT_JSON = PROJECT_ROOT / "reports" / "large_human_review_candidate_manifest_20261028.json"
DEFAULT_MD = PROJECT_ROOT / "reports" / "large_human_review_candidate_manifest_20261028.md"


def _compile(pattern: str) -> re.Pattern[str]:
    return re.compile(pattern, re.IGNORECASE)


DURATION = r"(?:하루|이틀|사흘|며칠|일주일|한\s*달|\d+\s*(?:일|주|개월|달))"
OUTCOME = r"(?:빠졌|빠지|감량|줄었|감소|사라졌|없어졌|개선|좋아졌|나아졌|회복|변했|바뀌었)"
HEALTH_OUTCOME = r"(?:체중|살이|통증|염증|여드름|트러블|탈모|붓기|변비|혈당|콜레스테롤|피로|가려움).{0,24}" + OUTCOME

EXTREME_PATTERNS = (
    _compile(DURATION + r".{0,35}\d+(?:\.\d+)?\s*kg.{0,24}(?:빠졌|감량|줄었|뺐)"),
    _compile(DURATION + r".{0,40}(?:완전히|싹|기적(?:적으로)?|드라마틱하게|몰라보게).{0,30}" + OUTCOME),
    _compile(r"(?:완전히|싹|기적(?:적으로)?|드라마틱하게|몰라보게).{0,30}" + OUTCOME + r".{0,40}" + DURATION),
)
IMMEDIATE_PATTERNS = (
    _compile(r"(?:먹|복용|섭취)\s*(?:하자마자|자마자)|(?:한\s*번|1회)\s*(?:먹|복용|섭취)(?:고|하자마자)|하루\s*만에"),
    _compile(r"(?:바르|사용|쓰)\s*(?:자마자|고\s*바로)|첫\s*(?:사용|복용|섭취).{0,12}바로"),
)
PROMO_STRUCTURAL = (
    _compile(r"(?:^|[\n\r]|[.!?]\s*)(?:\[?\s*)?(제품\s*(?:특징|특장점|소개)|장점|단점|추천\s*대상|총평|주요\s*성분|효능|사용\s*방법)(?:\s*\]?\s*)[:：-]"),
    _compile(r"(?:^|\n)\s*(?:[-*•▶✓✔]|\d+[.)])\s*\S+"),
)
PROMO_PHRASES = (
    _compile(r"(?:탁월한|완벽한|최적의)\s*\S{0,12}(?:제품|선택|솔루션)"),
    _compile(r"(?:선사합니다|자랑합니다|추천드립니다|도움을\s*줍니다|권장합니다)"),
    _compile(r"(?:~|♡|♥|★){2,}"),
)
PRAISE_PATTERNS = (
    _compile(r"^(?:정말|진짜|너무|아주|완전|역시)?\s*(?:좋아요|좋습니다|최고예요|최고입니다|만족해요|만족합니다|강추합니다|추천해요|재구매할게요)[\s.!~ㅋㅎ♡♥👍]*$"),
    _compile(r"^(?:굿|good|best|최고|대만족|강추)[\s.!~ㅋㅎ♡♥👍]*$"),
)
SPECIFIC_EXPERIENCE = _compile(
    r"(?:제가|저는|내가|저한테|제\s*(?:피부|몸|두피)|우리\s*집|"
    + DURATION + r"\s*(?:동안|째)?|구매|주문|배송|도착|직접|실사용|"
    r"(?:먹|복용|섭취|사용|착용|바르|입|신)(?:었|았|했|해\s*보|어\s*보))"
)


def content_hash(normalized: str) -> str:
    return sha256(normalized.encode("utf-8")).hexdigest()


def matching(patterns: tuple[re.Pattern[str], ...], text: str) -> list[str]:
    found: list[str] = []
    for pattern in patterns:
        for match in pattern.finditer(text):
            value = match.group(0).strip()
            if value and value not in found:
                found.append(value)
            if len(found) >= 5:
                return found
    return found


def detect_extreme_result(text: str) -> dict | None:
    """Precision-first duration + extraordinary outcome evidence."""
    evidence = matching(EXTREME_PATTERNS, text)
    if not evidence:
        return None
    return {"matched_patterns": evidence}


def detect_immediate_effect(text: str) -> dict | None:
    """Require immediacy and health/diet/treatment outcome, not sensation alone."""
    immediate = matching(IMMEDIATE_PATTERNS, text)
    outcomes = matching((_compile(HEALTH_OUTCOME),), text)
    if not immediate or not outcomes:
        return None
    return {"immediacy": immediate, "health_outcome": outcomes}


def detect_promotional(text: str, description_count: int) -> dict | None:
    structural = matching(PROMO_STRUCTURAL, text)
    phrases = matching(PROMO_PHRASES, text)
    if not phrases or not structural:
        return None
    if len(structural) < 2 and description_count < 3:
        return None
    return {
        "structural_markers": structural,
        "promotional_phrases": phrases,
        "structural_marker_count": len(structural),
        "promotional_phrase_count": len(phrases),
        "description_signal_count": description_count,
    }


def detect_low_information(text: str) -> dict | None:
    if len(text) > 20:
        return None
    evidence = matching(PRAISE_PATTERNS, text)
    if not evidence:
        return None
    return {
        "normalized_text_length": len(text),
        "character_length": len(text),
        "praise_pattern": evidence[0],
    }


def detect_hard_negative(text: str, description) -> dict | None:
    if len(text) < 80 or description.description_signal_count < 2:
        return None
    if not description.has_personal_experience or not SPECIFIC_EXPERIENCE.search(text):
        return None
    return {
        "description_signal_count": description.description_signal_count,
        "description_signals": list(description.description_signals),
        "personal_experience_evidence": list(description.personal_experience_signals),
    }


def detect_text_sources(content: str) -> dict[str, dict]:
    normalized = normalize_content(content)
    if normalized is None:
        return {}
    description = analyze_text(content)
    result: dict[str, dict] = {}
    for name, detector in (
        (EXTREME_RESULT, detect_extreme_result),
        (IMMEDIATE_EFFECT, detect_immediate_effect),
    ):
        evidence = detector(normalized)
        if evidence:
            result[name] = evidence
    promotional = detect_promotional(content, description.description_signal_count)
    if promotional:
        result[PROMOTIONAL_TEMPLATE] = promotional
    low = detect_low_information(normalized)
    if low:
        result[LOW_INFORMATION] = low
    hard = detect_hard_negative(normalized, description)
    if hard:
        result[HARD_NEGATIVE] = hard
    return result


def load_description_provenance(v1_path: Path, v2_path: Path) -> dict[tuple[str, str, str], dict]:
    v2: dict[str, dict] = {}
    with v2_path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            v2[row["candidate_id"]] = row
    result = {}
    with v1_path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            key = tuple(canonical_identifier(row.get(name)) for name in ("platform", "product_id", "review_id"))
            if None in key:
                continue
            refined = v2.get(row["candidate_id"])
            result[key] = {
                "candidate_id": row["candidate_id"],
                "v1_tier": row["tier"],
                "v2_tier": refined["v2_tier"] if refined else "NOT_CANDIDATE",
                "description_signal_count": int(row["description_signal_count"]),
                "description_signals": row["description_signals"].split("|") if row["description_signals"] else [],
                "description_evidence": json.loads(row["description_evidence"]),
            }
    return result


def create_schema(db: sqlite3.Connection) -> None:
    db.executescript("""
    PRAGMA journal_mode=OFF; PRAGMA synchronous=OFF; PRAGMA temp_store=FILE;
    CREATE TABLE review_index (
      row_uid TEXT PRIMARY KEY, platform TEXT NOT NULL, source_row INTEGER NOT NULL,
      product_id TEXT, review_id TEXT, product_category_raw TEXT,
      normalized_category TEXT NOT NULL, category_mapping_reason TEXT NOT NULL,
      normalized_content_hash TEXT, content_length INTEGER,
      valid_identity INTEGER NOT NULL, valid_content INTEGER NOT NULL
    ) WITHOUT ROWID;
    CREATE INDEX review_hash_idx ON review_index(normalized_content_hash);
    CREATE TABLE content_groups (
      normalized_content_hash TEXT PRIMARY KEY, content_length INTEGER NOT NULL,
      global_count INTEGER NOT NULL
    ) WITHOUT ROWID;
    CREATE TABLE group_platform (
      normalized_content_hash TEXT, platform TEXT, member_count INTEGER NOT NULL,
      PRIMARY KEY(normalized_content_hash, platform)
    ) WITHOUT ROWID;
    CREATE TABLE group_product (
      normalized_content_hash TEXT, platform TEXT, product_id TEXT,
      member_count INTEGER NOT NULL,
      PRIMARY KEY(normalized_content_hash, platform, product_id)
    ) WITHOUT ROWID;
    CREATE TABLE candidate_content (row_uid TEXT PRIMARY KEY, content TEXT NOT NULL) WITHOUT ROWID;
    CREATE TABLE source_evidence (
      row_uid TEXT, candidate_source TEXT, evidence_json TEXT NOT NULL,
      PRIMARY KEY(row_uid, candidate_source)
    ) WITHOUT ROWID;
    CREATE INDEX source_name_idx ON source_evidence(candidate_source);
    CREATE TABLE duplicate_clusters (
      cluster_id TEXT PRIMARY KEY, normalized_content_hash TEXT UNIQUE,
      content_length INTEGER, global_count INTEGER,
      unique_platform_count INTEGER, unique_product_count INTEGER,
      duplicate_scope TEXT, frequency_band TEXT
    ) WITHOUT ROWID;
    CREATE TABLE duplicate_members (
      cluster_id TEXT, row_uid TEXT, platform_count INTEGER,
      same_product_count INTEGER, PRIMARY KEY(cluster_id, row_uid)
    ) WITHOUT ROWID;
    CREATE TABLE random_control_eligible (row_uid TEXT PRIMARY KEY) WITHOUT ROWID;
    CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL) WITHOUT ROWID;
    CREATE VIEW candidate_manifest AS
      SELECT r.row_uid,r.platform,r.product_id,r.review_id,r.product_category_raw,
             r.normalized_category,c.content,r.normalized_content_hash,r.content_length,
             grouped.candidate_sources,dm.cluster_id,dc.global_count AS global_duplicate_count,
             dm.platform_count AS platform_duplicate_count,
             dm.same_product_count AS same_product_duplicate_count
      FROM review_index r JOIN candidate_content c USING(row_uid)
      JOIN (
        SELECT row_uid,GROUP_CONCAT(candidate_source,'|') AS candidate_sources
        FROM (SELECT row_uid,candidate_source FROM source_evidence ORDER BY row_uid,candidate_source)
        GROUP BY row_uid
      ) grouped USING(row_uid)
      LEFT JOIN duplicate_members dm USING(row_uid)
      LEFT JOIN duplicate_clusters dc USING(cluster_id);
    """)


def _upsert_count(db, table: str, keys: tuple, values: tuple) -> None:
    columns = ",".join(keys)
    placeholders = ",".join("?" for _ in values)
    db.execute(
        f"INSERT INTO {table}({columns},member_count) VALUES({placeholders},1) "
        f"ON CONFLICT({columns}) DO UPDATE SET member_count=member_count+1", values,
    )


def _insert_source(db, row_uid: str, source: str, evidence: dict, content: str) -> None:
    db.execute(
        "INSERT OR IGNORE INTO source_evidence VALUES(?,?,?)",
        (row_uid, source, json.dumps(evidence, ensure_ascii=False, separators=(",", ":"))),
    )
    db.execute("INSERT OR IGNORE INTO candidate_content VALUES(?,?)", (row_uid, content))


def _validate_header(platform: str, fieldnames: list[str] | None) -> None:
    if fieldnames is None:
        raise ValueError(f"{platform}: CSV header가 없습니다.")
    missing = [name for name in REQUIRED_COLUMNS if fieldnames.count(name) != 1]
    if missing or len(fieldnames) != len(set(fieldnames)):
        raise ValueError(f"{platform}: 필수/중복 컬럼 오류: {missing}")


def scan_first_pass(db, paths, description_provenance, progress=False) -> tuple[int, Counter]:
    total = 0
    platform_counts = Counter()
    for expected, path in paths.items():
        if progress:
            print(f"[pass 1/2] {expected}: {portable_report_path(path, '<LOCAL_REVIEW_EXPORT>')}", flush=True)
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            _validate_header(expected, reader.fieldnames)
            for source_row, row in enumerate(reader, start=2):
                total += 1
                platform = canonical_identifier(row.get("platform"))
                if platform != expected:
                    raise ValueError(f"{expected}:{source_row} platform={platform!r}")
                platform_counts[platform] += 1
                product_id = canonical_identifier(row.get("product_id"))
                review_id = canonical_identifier(row.get("review_id"))
                raw_category = row.get("product_category") or ""
                normalized_category, reason = normalize_category(platform, raw_category)
                content = row.get("content")
                normalized = normalize_content(content)
                digest = content_hash(normalized) if normalized is not None else None
                length = len(normalized) if normalized is not None else None
                row_uid = f"{platform}:{source_row}"
                db.execute(
                    "INSERT INTO review_index VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                    (row_uid, platform, source_row, product_id, review_id, raw_category,
                     normalized_category, reason, digest, length,
                     int(None not in (platform, product_id, review_id)), int(normalized is not None)),
                )
                if normalized is None:
                    continue
                db.execute(
                    "INSERT INTO content_groups VALUES(?,?,1) ON CONFLICT(normalized_content_hash) "
                    "DO UPDATE SET global_count=global_count+1", (digest, length),
                )
                _upsert_count(db, "group_platform", ("normalized_content_hash", "platform"), (digest, platform))
                if product_id is not None:
                    _upsert_count(db, "group_product", ("normalized_content_hash", "platform", "product_id"), (digest, platform, product_id))
                if None not in (platform, product_id, review_id):
                    provenance = description_provenance.get((platform, product_id, review_id))
                    if provenance:
                        _insert_source(db, row_uid, PRODUCT_DESCRIPTION, provenance, content)
                for source, evidence in detect_text_sources(content).items():
                    _insert_source(db, row_uid, source, evidence, content)
                if total % 10_000 == 0:
                    db.commit()
        db.commit()
    return total, platform_counts


def frequency_band(count: int) -> str:
    if count < 5:
        return "2-4"
    if count < 10:
        return "5-9"
    if count < 20:
        return "10-19"
    return "20+"


def materialize_clusters(db) -> int:
    groups = db.execute(
        "SELECT normalized_content_hash,content_length,global_count FROM content_groups "
        "WHERE global_count>1 ORDER BY normalized_content_hash"
    ).fetchall()
    for number, (digest, length, count) in enumerate(groups, start=1):
        platforms = db.execute("SELECT COUNT(*) FROM group_platform WHERE normalized_content_hash=?", (digest,)).fetchone()[0]
        products = db.execute("SELECT COUNT(*) FROM group_product WHERE normalized_content_hash=?", (digest,)).fetchone()[0]
        scope = "CROSS_PLATFORM" if platforms > 1 else "CROSS_PRODUCT_SAME_PLATFORM" if products > 1 else "SAME_PRODUCT"
        db.execute("INSERT INTO duplicate_clusters VALUES(?,?,?,?,?,?,?,?)", (
            f"EXACT-{number:07d}", digest, length, count, platforms, products, scope, frequency_band(count)))
    db.commit()
    return len(groups)


def scan_second_pass(db, paths, progress=False) -> None:
    duplicate_hashes = {row[0]: row[1] for row in db.execute("SELECT normalized_content_hash,cluster_id FROM duplicate_clusters")}
    for expected, path in paths.items():
        if progress:
            print(f"[pass 2/2] {expected}: duplicate membership", flush=True)
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            _validate_header(expected, reader.fieldnames)
            for source_row, row in enumerate(reader, start=2):
                content = row.get("content")
                normalized = normalize_content(content)
                if normalized is None:
                    continue
                digest = content_hash(normalized)
                cluster_id = duplicate_hashes.get(digest)
                if cluster_id is None:
                    continue
                row_uid = f"{expected}:{source_row}"
                product_id = canonical_identifier(row.get("product_id"))
                platform_count = db.execute(
                    "SELECT member_count FROM group_platform WHERE normalized_content_hash=? AND platform=?",
                    (digest, expected),
                ).fetchone()[0]
                product = db.execute(
                    "SELECT member_count FROM group_product WHERE normalized_content_hash=? AND platform=? AND product_id=?",
                    (digest, expected, product_id),
                ).fetchone()
                same_product_count = product[0] if product else 0
                db.execute("INSERT INTO duplicate_members VALUES(?,?,?,?)", (cluster_id, row_uid, platform_count, same_product_count))
                evidence = {
                    "cluster_id": cluster_id,
                    "normalized_content_hash": digest,
                    "global_duplicate_count": db.execute("SELECT global_count FROM content_groups WHERE normalized_content_hash=?", (digest,)).fetchone()[0],
                    "platform_duplicate_count": platform_count,
                    "same_product_duplicate_count": same_product_count,
                }
                _insert_source(db, row_uid, EXACT_DUPLICATE, evidence, content)
                if len(normalized) < 30:
                    _insert_source(db, row_uid, REPEATED_SHORT, evidence, content)
            db.commit()


def materialize_random_eligibility(db) -> int:
    placeholders = ",".join("?" for _ in SUSPICIOUS_FOCUSED)
    db.execute(
        "INSERT INTO random_control_eligible "
        "SELECT r.row_uid FROM review_index r WHERE r.valid_identity=1 AND r.valid_content=1 "
        "AND r.content_length>=20 AND TRIM(r.product_category_raw)<>'' "
        f"AND NOT EXISTS (SELECT 1 FROM source_evidence s WHERE s.row_uid=r.row_uid AND s.candidate_source IN ({placeholders}))",
        tuple(sorted(SUSPICIOUS_FOCUSED)),
    )
    db.commit()
    return db.execute("SELECT COUNT(*) FROM random_control_eligible").fetchone()[0]


def qdict(db, sql: str, params=()) -> dict:
    return {key: value for key, value in db.execute(sql, params)}


def source_stats(db) -> dict:
    result = {}
    for source in SOURCES:
        total = db.execute("SELECT COUNT(*) FROM source_evidence WHERE candidate_source=?", (source,)).fetchone()[0]
        products = db.execute(
            "SELECT COUNT(DISTINCT r.platform||char(31)||COALESCE(r.product_id,'')) "
            "FROM source_evidence s JOIN review_index r USING(row_uid) WHERE s.candidate_source=?", (source,),
        ).fetchone()[0]
        platforms = qdict(db,
            "SELECT r.platform,COUNT(*) FROM source_evidence s JOIN review_index r USING(row_uid) "
            "WHERE s.candidate_source=? GROUP BY r.platform ORDER BY r.platform", (source,))
        categories = qdict(db,
            "SELECT r.normalized_category,COUNT(*) FROM source_evidence s JOIN review_index r USING(row_uid) "
            "WHERE s.candidate_source=? GROUP BY r.normalized_category ORDER BY r.normalized_category", (source,))
        lengths = qdict(db,
            "SELECT CASE WHEN r.content_length<20 THEN '<20' WHEN r.content_length<50 THEN '20-49' "
            "WHEN r.content_length<100 THEN '50-99' WHEN r.content_length<200 THEN '100-199' ELSE '200+' END,COUNT(*) "
            "FROM source_evidence s JOIN review_index r USING(row_uid) WHERE s.candidate_source=? GROUP BY 1", (source,))
        result[source] = {"review_count": total, "unique_candidate_count": total,
                          "unique_product_count": products,
                          "platform_distribution": platforms, "category_distribution": categories,
                          "content_length_distribution": lengths}
    return result


def overlap_stats(db) -> dict:
    combinations = qdict(db, """
      SELECT sources,COUNT(*) FROM (
        SELECT row_uid,GROUP_CONCAT(candidate_source,'|') sources
        FROM (SELECT row_uid,candidate_source FROM source_evidence ORDER BY row_uid,candidate_source)
        GROUP BY row_uid) GROUP BY sources ORDER BY COUNT(*) DESC LIMIT 30
    """)
    source_count = qdict(db, """
      SELECT CASE WHEN n>=3 THEN '3+' ELSE CAST(n AS TEXT) END,COUNT(*) FROM
      (SELECT row_uid,COUNT(*) n FROM source_evidence GROUP BY row_uid) GROUP BY 1
    """)
    pairs = {}
    for a, b in ((PRODUCT_DESCRIPTION, PROMOTIONAL_TEMPLATE), (EXTREME_RESULT, IMMEDIATE_EFFECT), (LOW_INFORMATION, REPEATED_SHORT)):
        pairs[f"{a} & {b}"] = db.execute(
            "SELECT COUNT(*) FROM source_evidence a JOIN source_evidence b USING(row_uid) "
            "WHERE a.candidate_source=? AND b.candidate_source=?", (a, b),
        ).fetchone()[0]
    return {"source_count_per_review": source_count, "top_combinations": combinations, "requested_pairs": pairs}


def duplicate_stats(db) -> dict:
    return {
        "cluster_count": db.execute("SELECT COUNT(*) FROM duplicate_clusters").fetchone()[0],
        "member_count": db.execute("SELECT COUNT(*) FROM duplicate_members").fetchone()[0],
        "frequency_bands": qdict(db, "SELECT frequency_band,COUNT(*) FROM duplicate_clusters GROUP BY frequency_band"),
        "scopes": qdict(db, "SELECT duplicate_scope,COUNT(*) FROM duplicate_clusters GROUP BY duplicate_scope"),
    }


def recommend_allocation(stats: dict, total=6000) -> dict:
    order = [PRODUCT_DESCRIPTION, EXTREME_RESULT, IMMEDIATE_EFFECT, PROMOTIONAL_TEMPLATE, REPEATED_SHORT, EXACT_DUPLICATE, LOW_INFORMATION]
    weights = {PRODUCT_DESCRIPTION: .12, EXTREME_RESULT: .17, IMMEDIATE_EFFECT: .17,
               PROMOTIONAL_TEMPLATE: .19, REPEATED_SHORT: .14, EXACT_DUPLICATE: .13,
               LOW_INFORMATION: .08}
    allocation = {name: min(stats[name]["review_count"], round(total * weights[name])) for name in order}
    remaining = total - sum(allocation.values())
    while remaining > 0:
        changed = False
        for name in order:
            if allocation[name] < stats[name]["review_count"]:
                allocation[name] += 1
                remaining -= 1
                changed = True
                if remaining == 0:
                    break
        if not changed:
            break
    return {"target": total, "recommended_source_quotas_before_overlap_dedup": allocation,
            "unallocated_if_insufficient_volume": remaining}


def build_summary(db, paths, total, platform_counts, elapsed, signatures_before, signatures_after, db_path) -> dict:
    sources = source_stats(db)
    random_count = db.execute("SELECT COUNT(*) FROM random_control_eligible").fetchone()[0]
    hard_count = sources[HARD_NEGATIVE]["review_count"]
    category_candidate = qdict(db, """
      SELECT normalized_category,COUNT(DISTINCT row_uid) FROM review_index
      JOIN source_evidence USING(row_uid) GROUP BY normalized_category
    """)
    return {
        "analysis_type": "text-only human-review candidate-source manifest; no automatic labels and no final 10K pool",
        "storage": {
            "format": "SQLite",
            "path": portable_report_path(db_path),
            "reason": "review_index and duplicate membership preserve all rows while candidate_content copies bodies only for candidate rows; random eligibility stores row_uid only",
            "tables": ["review_index", "candidate_manifest", "source_evidence", "candidate_content", "duplicate_clusters", "duplicate_members", "random_control_eligible", "metadata"],
        },
        "execution": {"full_scan_reviews": total, "passes": 2, "elapsed_seconds": elapsed,
                      "source_signatures_before": signatures_before,
                      "source_signatures_after": signatures_after,
                      "source_signatures_unchanged": signatures_before == signatures_after},
        "platform_counts": dict(platform_counts),
        "source_metrics": sources,
        "overlap": overlap_stats(db),
        "duplicate_clusters": duplicate_stats(db),
        "random_control_eligible": random_count,
        "candidate_category_distribution": category_candidate,
        "diet_candidate_count": category_candidate.get("DIET", 0),
        "health_supplement_candidate_count": category_candidate.get("HEALTH_SUPPLEMENT", 0),
        "pilot_10k_feasibility": {
            "signal_focused_target": 6000,
            "hard_negative_target": 2500,
            "hard_negative_available": hard_count,
            "random_control_target": 1500,
            "random_control_available": random_count,
            "signal_allocation": recommend_allocation(sources),
            "platform_sqrt_soft_targets": sqrt_platform_targets(platform_counts, 10000),
            "category_policy": {"minimum": "50 each when available; DIET 150 and HEALTH_SUPPLEMENT 500 preferred", "maximum_soft_cap": "25% per normalized category"},
            "hard_negative_shortfall": max(0, 2500 - hard_count),
            "exact_target_feasible_without_rule_expansion": hard_count >= 2500 and random_count >= 1500,
            "created_final_10k_pool": False,
        },
        "excluded_by_design": ["CURRENT_PTEXT_HIGH", "CURRENT_PTEXT_BOUNDARY", "semantic near-duplicate full scan", "model/LLM inference", "human labels"],
        "lexical_near_duplicate_next_step": "Use length/language/category blocking plus MinHash/LSH over normalized character shingles; calibrate on a bounded audit sample before any 1.15M-scale run.",
    }


def render_markdown(summary: dict) -> str:
    execution = summary["execution"]
    lines = [
        "# Large Human Review Candidate Source Manifest", "",
        "> 사람 검토 후보 탐색 결과입니다. candidate source는 SUSPICIOUS/NORMAL/UNCERTAIN 라벨이 아니며 최종 10K pool을 생성하지 않았습니다.", "",
        "## Execution", "",
        f"- Full scan: **{execution['full_scan_reviews']:,} reviews**, 2 streaming passes",
        f"- Duration: **{execution['elapsed_seconds']:.2f} seconds**",
        f"- Raw signatures unchanged: **{execution['source_signatures_unchanged']}**",
        f"- Storage: SQLite (`{summary['storage']['path']}`); random eligibility는 본문을 복제하지 않고 row_uid만 저장", "",
        "## Candidate sources", "",
        "| source | reviews | unique products |", "| --- | ---: | ---: |",
    ]
    for source, item in summary["source_metrics"].items():
        lines.append(f"| {source} | {item['review_count']:,} | {item['unique_product_count']:,} |")
    lines += ["", f"- RANDOM_CONTROL_ELIGIBLE: **{summary['random_control_eligible']:,}** (eligibility only; not sampled)", "",
              "## Platform and category distributions", ""]
    for source, item in summary["source_metrics"].items():
        lines += [f"### {source}", "", f"- platforms: `{item['platform_distribution']}`",
                  f"- provisional categories: `{item['category_distribution']}`",
                  f"- length bands: `{item['content_length_distribution']}`", ""]
    lines += ["## Source overlap", "", f"- source count/review: `{summary['overlap']['source_count_per_review']}`",
              f"- requested pairs: `{summary['overlap']['requested_pairs']}`", "", "Top combinations:", ""]
    for combo, count in summary["overlap"]["top_combinations"].items():
        lines.append(f"- `{combo}`: {count:,}")
    dup = summary["duplicate_clusters"]
    lines += ["", "## Exact duplicate clusters", "",
              f"- clusters: **{dup['cluster_count']:,}**", f"- members: **{dup['member_count']:,}**",
              f"- frequency bands: `{dup['frequency_bands']}`", f"- scopes: `{dup['scopes']}`",
              "- 반복 리뷰는 삭제/통합하지 않았고 duplicate_members에 모두 보존했습니다.", "",
              "## Bias checks", "",
              f"- DIET candidates: **{summary['diet_candidate_count']:,}**",
              f"- HEALTH_SUPPLEMENT candidates: **{summary['health_supplement_candidate_count']:,}**",
              "- BEAUTY/oliveyoung 및 FOOD/kurly 집중은 source별 platform/category 표로 확인하며 다음 sampling 단계에서 soft cap을 적용해야 합니다.",
              "- LOW_INFORMATION_PRAISE와 repeated-short는 weak source이며 단독 suspicious 근거로 사용하지 않습니다.", "",
              "## 10K feasibility (recommendation only)", ""]
    pilot = summary["pilot_10k_feasibility"]
    lines += [f"- Signal-focused 6,000 source quotas before overlap dedup: `{pilot['signal_allocation']['recommended_source_quotas_before_overlap_dedup']}`",
              f"- Hard Negative: target 2,500 / available {pilot['hard_negative_available']:,}",
              f"- Random Control: target 1,500 / eligible {pilot['random_control_available']:,}",
              f"- Exact 6,000/2,500/1,500 composition feasible without rule expansion: **{pilot['exact_target_feasible_without_rule_expansion']}** (Hard Negative shortfall {pilot['hard_negative_shortfall']:,})",
              f"- sqrt platform soft targets: `{pilot['platform_sqrt_soft_targets']}`",
              "- Category soft policy: each category 50 when available, DIET 150 / HEALTH_SUPPLEMENT 500 preferred, any category max 25%.",
              "- 실제 10K 선택에서는 overlap을 제거하고 product/cluster cap 및 platform×category strata를 적용해야 합니다.", "",
              "## Scope and next step", "",
              "- CURRENT_PTEXT_HIGH/BOUNDARY, semantic near-duplicate full scan, model/LLM inference, training은 실행하지 않았습니다.",
              "- Near-duplicate는 length/language/category blocking + normalized character-shingle MinHash/LSH를 작은 audit sample에서 먼저 보정하는 방식을 권장합니다.",
              "- 다음 단계는 이 manifest를 대상으로 quota dry-run 및 사람이 승인한 뒤에만 10K pool을 생성하는 것입니다.",
              "- 자동 human label은 어디에도 생성하지 않았습니다.", ""]
    return "\n".join(lines)


def file_signature(path: Path) -> dict:
    stat = path.stat()
    return {"size": stat.st_size, "mtime_ns": stat.st_mtime_ns}


def build_manifest(paths, description_path, v2_path, db_path, progress=False, expected_total=None):
    if db_path.exists():
        raise FileExistsError(f"기존 결과를 덮어쓰지 않습니다: {db_path}")
    signatures_before = {name: file_signature(path) for name, path in paths.items()}
    started = time.perf_counter()
    provenance = load_description_provenance(description_path, v2_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(db_path)
    try:
        create_schema(db)
        total, platform_counts = scan_first_pass(db, paths, provenance, progress)
        if expected_total is not None and total != expected_total:
            raise ValueError(f"review count mismatch: {total:,} != {expected_total:,}")
        materialize_clusters(db)
        scan_second_pass(db, paths, progress)
        materialize_random_eligibility(db)
        signatures_after = {name: file_signature(path) for name, path in paths.items()}
        if signatures_before != signatures_after:
            raise ValueError("raw source signature changed during scan")
        elapsed = time.perf_counter() - started
        summary = build_summary(db, paths, total, platform_counts, elapsed,
                                signatures_before, signatures_after, db_path)
        db.executemany("INSERT INTO metadata VALUES(?,?)", (
            ("analysis_type", summary["analysis_type"]),
            ("human_labels_created", "false"),
            ("final_10k_pool_created", "false"),
            ("summary_json", json.dumps(summary, ensure_ascii=False, separators=(",", ":"))),
        ))
        db.commit()
        return summary
    except Exception:
        db.close()
        raise
    finally:
        if db:
            db.close()


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Build text-only candidate-source manifest; no labels or final 10K pool")
    for platform, default in DEFAULT_INPUTS.items():
        parser.add_argument(f"--{platform}", type=Path, default=default)
    parser.add_argument("--description-v1", type=Path, default=DEFAULT_DESCRIPTION)
    parser.add_argument("--description-v2", type=Path, default=DEFAULT_V2)
    parser.add_argument("--database", type=Path, default=DEFAULT_DB)
    parser.add_argument("--json-report", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-report", type=Path, default=DEFAULT_MD)
    parser.add_argument("--expected-total", type=int, default=1_151_943)
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    paths = {name: getattr(args, name).expanduser().resolve() for name in DEFAULT_INPUTS}
    outputs = [args.database.resolve(), args.json_report.resolve(), args.markdown_report.resolve()]
    if len(set(outputs)) != 3 or any(path.exists() for path in outputs):
        print("오류: output 경로는 서로 달라야 하며 기존 파일을 덮어쓰지 않습니다.", file=sys.stderr)
        return 1
    try:
        summary = build_manifest(paths, args.description_v1.resolve(), args.description_v2.resolve(),
                                 args.database.resolve(), progress=True, expected_total=args.expected_total)
        args.json_report.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_report.parent.mkdir(parents=True, exist_ok=True)
        args.json_report.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        args.markdown_report.write_text(render_markdown(summary), encoding="utf-8")
        print(render_markdown(summary))
        print("FINAL_10K_POOL_CREATED=false\nAUTOMATIC_HUMAN_LABELS_CREATED=false")
        return 0
    except Exception as exc:
        print(f"오류: candidate manifest 생성 실패: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
