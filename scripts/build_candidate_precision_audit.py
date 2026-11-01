"""Build a label-blank precision audit and quota dry-run from the canonical manifest.

Candidate sources and prototype expansions are discovery provenance, never labels.
The canonical SQLite database is opened read-only and is never modified.
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

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from analyze_new_review_inventory import PROJECT_ROOT, normalize_content, portable_report_path  # noqa: E402
from build_large_human_review_candidate_manifest import (  # noqa: E402
    EXACT_DUPLICATE, EXTREME_RESULT, HARD_NEGATIVE, IMMEDIATE_EFFECT,
    LOW_INFORMATION, PRODUCT_DESCRIPTION, PROMOTIONAL_TEMPLATE, REPEATED_SHORT,
)

EXTREME_EXPANDED = "EXTREME_RESULT_EXPANDED_PROTOTYPE"
IMMEDIATE_EXPANDED = "IMMEDIATE_EFFECT_EXPANDED_PROTOTYPE"
HARD_EXPANDED = "HARD_NEGATIVE_EXPANDED_CANDIDATE"
EXISTING_TARGETS = {
    EXTREME_RESULT: None, IMMEDIATE_EFFECT: None, PRODUCT_DESCRIPTION: 100,
    PROMOTIONAL_TEMPLATE: 100, LOW_INFORMATION: 100, REPEATED_SHORT: 200,
    EXACT_DUPLICATE: 200, HARD_NEGATIVE: 150,
}
EXPANDED_TARGETS = {EXTREME_EXPANDED: 100, IMMEDIATE_EXPANDED: 100, HARD_EXPANDED: 150}
DEFAULT_DB = PROJECT_ROOT / "outputs" / "large_human_review_candidate_manifest_20261028.sqlite3"
DEFAULT_AUDIT = PROJECT_ROOT / "outputs" / "human_review_candidate_precision_audit_20261028.csv"
DEFAULT_EXPANSION = PROJECT_ROOT / "outputs" / "human_review_rule_expansion_candidates_20261028.csv"
DEFAULT_AUDIT_MD = PROJECT_ROOT / "reports" / "human_review_candidate_precision_audit_20261028.md"
DEFAULT_AUDIT_JSON = PROJECT_ROOT / "reports" / "human_review_candidate_precision_audit_20261028.json"
DEFAULT_DRY_MD = PROJECT_ROOT / "reports" / "human_review_10k_quota_dry_run_20261028.md"
DEFAULT_DRY_JSON = PROJECT_ROOT / "reports" / "human_review_10k_quota_dry_run_20261028.json"

DURATION = r"(?:하루|이틀|사흘|며칠|일주일|한\s*달|\d+\s*(?:일|주|주일|개월|달))"
DOMAIN = r"(?:체중|살|식욕|붓기|체지방|허리|배|변비|화장실|수면|잠|통증|염증|혈당|콜레스테롤|피로|피부|여드름|트러블|모공|모발|머리|탈모|두피|가려움)"
CHANGE = r"(?:빠졌|빠지|감량|줄었|줄어|감소|사라졌|없어졌|개선|좋아졌|나아졌|들어갔|잘\s*간|잘\s*왔|덜\s*빠|났(?:어요|습니다|다))"
IMMEDIATE = r"(?:먹자마자|복용하자마자|섭취하자마자|바르자마자|쓰자마자|사용하자마자|한\s*번\s*(?:먹|복용|섭취|바르|사용)\w*|하루\s*만에|다음\s*날\s*바로|즉각(?:적)?|즉시|바로\s*(?:효과|개선|빠짐))"
SENSORY = re.compile(r"(?:시원|향이?\s*나|달다|달아요|상큼|촉촉|끈적|부드럽|따갑|화끈|쿨링)", re.I)
EXPERIENCE = re.compile(r"(?:(?:\d+\s*(?:일|주|개월|달)|며칠|몇\s*주|한\s*달).{0,12}(?:사용|복용|착용|먹)|직접\s*(?:입|먹|써|사용|설치)|입어\s*보|먹어\s*보|써\s*보|세탁\s*(?:후|하고)|배송.{0,12}(?:받|도착).{0,16}(?:사용|써)|우리\s*집|제\s*(?:피부|두피|머리|체형)|내\s*(?:피부|두피|머리|체형)|재구매|조리|설치)", re.I)
TRADEOFF = re.compile(r"(?:장점|단점|아쉽|다만|하지만|반면|취향|개인차|경우에는|때만|핏|기장|사이즈|세척|수납|소음|배터리|호환|식감|가족\s*반응)", re.I)

AUDIT_FIELDS = [
    "audit_id", "audit_section", "row_uid", "platform", "product_id", "review_id",
    "product_category_raw", "normalized_category", "content", "candidate_sources",
    "primary_audit_source", "source_evidence", "relevant_metrics", "duplicate_in_packet",
    "human_label", "human_note",
]


def stable_key(*values: object) -> str:
    return sha256("\x1f".join(str(v) for v in values).encode("utf-8")).hexdigest()


def frequency_bucket(count: int | None) -> str:
    count = count or 0
    if count < 5:
        return "2-4"
    if count < 10:
        return "5-9"
    if count < 20:
        return "10-19"
    return "20+"


def detect_extreme_expanded(text: str) -> dict | None:
    text = normalize_content(text) or ""
    matches = []
    numeric = re.search(DURATION + r".{0,35}(?:\d+(?:\.\d+)?\s*(?:kg|킬로|cm|센티)).{0,24}(?:빠졌|감량|줄었|줄어|뺐)", text, re.I)
    reverse_numeric = re.search(r"\d+(?:\.\d+)?\s*(?:kg|킬로|cm|센티).{0,24}(?:빠졌|감량|줄었|줄어|뺐).{0,30}" + DURATION, text, re.I)
    dramatic = re.search(DOMAIN + r".{0,30}(?:완전히|싹|확(?:실히)?|눈에\s*띄게).{0,22}" + CHANGE, text, re.I)
    health = re.search(DURATION + r".{0,35}" + DOMAIN + r".{0,28}" + CHANGE, text, re.I)
    for name, match in (("numeric_change", numeric or reverse_numeric), ("contextual_dramatic_change", dramatic), ("duration_health_change", health)):
        if match:
            matches.append({"type": name, "text": match.group(0)})
    if not matches:
        return None
    # Numeric product specifications lack an outcome verb and are excluded above.
    return {"prototype": EXTREME_EXPANDED, "matches": matches, "false_positive_risk": "self-reported ordinary change or ambiguous duration"}


def detect_immediate_expanded(text: str) -> dict | None:
    text = normalize_content(text) or ""
    marker = re.search(IMMEDIATE, text, re.I)
    if not marker:
        return None
    window = text[max(0, marker.start() - 35): marker.end() + 70]
    outcome = re.search(DOMAIN + r".{0,25}" + CHANGE + r"|" + CHANGE + r".{0,25}" + DOMAIN, window, re.I)
    if not outcome:
        return None
    sensory = SENSORY.search(window)
    return {
        "prototype": IMMEDIATE_EXPANDED, "immediate_marker": marker.group(0),
        "effect_context": outcome.group(0), "sensory_term_also_present": bool(sensory),
        "false_positive_risk": "temporal sequence does not prove causality",
    }


def detect_hard_negative_expanded(text: str, category: str) -> dict | None:
    text = normalize_content(text) or ""
    if len(text) < 40:
        return None
    experience = EXPERIENCE.search(text)
    tradeoff = TRADEOFF.search(text)
    category_terms = {
        "FASHION": r"(?:키|몸무게|사이즈|핏|기장|세탁|착용)",
        "FOOD": r"(?:맛|식감|조리|재구매|가족|먹어)",
        "ELECTRONICS": r"(?:설치|배터리|소음|속도|호환|충전)",
        "LIVING": r"(?:집에서|세척|수납|설치|청소|공간)",
        "HEALTH_SUPPLEMENT": r"(?:복용|섭취|개인차|체감|며칠|\d+\s*(?:주|개월|달))",
        "DIET": r"(?:복용|섭취|식단|운동|체감|몸무게|\d+\s*(?:주|개월|달))",
    }
    category_match = re.search(category_terms.get(category, r"(?:직접|사용|구매|배송|장점|단점)"), text, re.I)
    if not experience or not (tradeoff or category_match):
        return None
    return {
        "prototype": HARD_EXPANDED, "experience": experience.group(0),
        "specific_detail": (tradeoff or category_match).group(0), "category_context": category,
        "false_positive_risk": "personal experience can still contain promotional or unsupported efficacy language",
    }


def connect_read_only(path: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{path.resolve().as_posix()}?mode=ro", uri=True)


def base_query(extra_where: str = "", params: tuple = ()) -> tuple[str, tuple]:
    sql = """
      SELECT r.row_uid,r.platform,r.product_id,r.review_id,r.product_category_raw,r.normalized_category,
             c.content,r.content_length,dm.cluster_id,dc.global_count,dc.duplicate_scope,dc.frequency_band,
             dm.platform_count,dm.same_product_count,grouped.sources,grouped.evidence_map
      FROM review_index r JOIN candidate_content c USING(row_uid)
      LEFT JOIN duplicate_members dm USING(row_uid) LEFT JOIN duplicate_clusters dc USING(cluster_id)
      LEFT JOIN (
        SELECT row_uid,GROUP_CONCAT(candidate_source,'|') sources,
               JSON_GROUP_OBJECT(candidate_source,evidence_json) evidence_map
        FROM source_evidence GROUP BY row_uid
      ) grouped USING(row_uid)
    """ + extra_where
    return sql, params


def row_dict(row: tuple) -> dict:
    keys = ("row_uid", "platform", "product_id", "review_id", "product_category_raw", "normalized_category",
            "content", "content_length", "cluster_id", "global_duplicate_count", "duplicate_scope",
            "frequency_band", "platform_duplicate_count", "same_product_duplicate_count", "candidate_sources", "source_evidence_map")
    return dict(zip(keys, row))


def expansion_scan(db: sqlite3.Connection) -> tuple[dict[str, list[dict]], dict[str, list[dict]]]:
    result = {EXTREME_EXPANDED: [], IMMEDIATE_EXPANDED: [], HARD_EXPANDED: []}
    existing = {source: [] for source in EXISTING_TARGETS}
    sql, params = base_query(" ORDER BY r.row_uid")
    for raw in db.execute(sql, params):
        row = row_dict(raw)
        evidence_map = json.loads(row.pop("source_evidence_map") or "{}")
        for source in existing:
            if source in evidence_map:
                item = dict(row)
                item["prototype_source"] = source
                item["prototype_evidence"] = json.loads(evidence_map[source])
                if source == PRODUCT_DESCRIPTION:
                    item["existing_tier"] = item["prototype_evidence"].get("v2_tier") or item["prototype_evidence"].get("v1_tier") or "UNKNOWN"
                existing[source].append(item)
        for source, evidence in (
            (EXTREME_EXPANDED, detect_extreme_expanded(row["content"])),
            (IMMEDIATE_EXPANDED, detect_immediate_expanded(row["content"])),
            (HARD_EXPANDED, detect_hard_negative_expanded(row["content"], row["normalized_category"])),
        ):
            if evidence:
                item = dict(row)
                item["prototype_source"] = source
                item["prototype_evidence"] = evidence
                result[source].append(item)
    return result, existing


def stratified_sample(rows: list[dict], target: int, strata, cluster_cap: int = 1,
                      exclude_clusters: set[str] | None = None) -> list[dict]:
    exclude_clusters = exclude_clusters or set()
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        key = tuple(row.get(name) or "NONE" for name in strata)
        groups[key].append(row)
    for values in groups.values():
        values.sort(key=lambda r: stable_key(r["row_uid"], *strata))
    selected, cluster_counts = [], Counter()
    keys = sorted(groups, key=lambda k: stable_key(*k))
    while len(selected) < target:
        changed = False
        for key in keys:
            values = groups[key]
            while values:
                row = values.pop(0)
                cluster = row.get("cluster_id")
                if cluster and (cluster in exclude_clusters or cluster_counts[cluster] >= cluster_cap):
                    continue
                selected.append(row)
                if cluster:
                    cluster_counts[cluster] += 1
                changed = True
                break
            if len(selected) >= target:
                break
        if not changed:
            break
    return selected


def existing_rows(db: sqlite3.Connection, source: str) -> list[dict]:
    sql, params = base_query(
        " JOIN source_evidence selected ON selected.row_uid=r.row_uid WHERE selected.candidate_source=? ORDER BY r.row_uid",
        (source,),
    )
    rows = []
    for raw in db.execute(sql, params):
        row = row_dict(raw)
        evidence = db.execute("SELECT evidence_json FROM source_evidence WHERE row_uid=? AND candidate_source=?", (row["row_uid"], source)).fetchone()[0]
        row["prototype_source"] = source
        row["prototype_evidence"] = json.loads(evidence)
        if source == PRODUCT_DESCRIPTION:
            row["existing_tier"] = row["prototype_evidence"].get("v2_tier") or row["prototype_evidence"].get("v1_tier") or "UNKNOWN"
        rows.append(row)
    return rows


def choose_existing_audit(all_existing: dict[str, list[dict]]) -> dict[str, list[dict]]:
    result, repeated_clusters = {}, set()
    for source, target in EXISTING_TARGETS.items():
        rows = all_existing[source]
        if target is None:
            picked = rows
        elif source == PRODUCT_DESCRIPTION:
            picked = stratified_sample(rows, target, ("platform", "normalized_category", "existing_tier"), 1)
        elif source == PROMOTIONAL_TEMPLATE:
            for row in rows:
                text = row["content"]
                row["promo_type"] = "STRUCTURED" if re.search(r"(?:장점|단점|총평)\s*[:：-]", text) else "RECOMMENDATION" if "추천" in text else "INGREDIENT_EFFECT" if re.search(r"(?:성분|효능)", text) else "USAGE"
            picked = stratified_sample(rows, target, ("promo_type", "platform", "normalized_category"), 1)
        elif source == LOW_INFORMATION:
            for row in rows:
                row["praise_length"] = "VERY_SHORT" if row["content_length"] < 10 else "SHORT"
                row["repeated_flag"] = "REPEATED" if REPEATED_SHORT in row["candidate_sources"].split("|") else "UNIQUE"
            picked = stratified_sample(rows, target, ("praise_length", "repeated_flag", "platform", "normalized_category"), 1)
        elif source == REPEATED_SHORT:
            picked = stratified_sample(rows, target, ("frequency_band", "platform", "normalized_category"), 2)
            repeated_clusters = {r["cluster_id"] for r in picked if r.get("cluster_id")}
        elif source == EXACT_DUPLICATE:
            picked = stratified_sample(rows, target, ("duplicate_scope", "frequency_band", "platform", "normalized_category"), 2, repeated_clusters)
            if len(picked) < target:
                extra = stratified_sample([r for r in rows if r["row_uid"] not in {x["row_uid"] for x in picked}], target-len(picked), ("duplicate_scope", "frequency_band"), 2)
                picked.extend(extra)
        else:
            for row in rows:
                row["diversity_priority"] = "PRIORITY" if row["platform"] != "oliveyoung" or row["normalized_category"] != "BEAUTY" else "BEAUTY_OLIVEYOUNG"
            picked = stratified_sample(rows, target, ("diversity_priority", "normalized_category", "platform"), 1)
        result[source] = picked
    return result


def choose_expanded_audit(expansions: dict[str, list[dict]], existing: dict[str, list[dict]]) -> dict[str, list[dict]]:
    corresponding = {EXTREME_EXPANDED: EXTREME_RESULT, IMMEDIATE_EXPANDED: IMMEDIATE_EFFECT, HARD_EXPANDED: HARD_NEGATIVE}
    result = {}
    for source, target in EXPANDED_TARGETS.items():
        old = corresponding[source]
        rows = [r for r in expansions[source] if old not in (r["candidate_sources"] or "").split("|")]
        if source == HARD_EXPANDED:
            for row in rows:
                row["diversity_priority"] = "PRIORITY" if row["platform"] != "oliveyoung" or row["normalized_category"] != "BEAUTY" else "BEAUTY_OLIVEYOUNG"
            strata = ("diversity_priority", "normalized_category", "platform")
        else:
            strata = ("normalized_category", "platform")
        result[source] = stratified_sample(rows, target, strata, 1)
    return result


def audit_rows(existing: dict[str, list[dict]], expanded: dict[str, list[dict]]) -> list[dict]:
    all_sections = [(f"EXISTING::{k}", k, rows) for k, rows in existing.items()] + [(f"EXPANDED::{k}", k, rows) for k, rows in expanded.items()]
    counts = Counter(r["row_uid"] for _, _, rows in all_sections for r in rows)
    output, number = [], 0
    for section, source, rows in all_sections:
        for row in rows:
            number += 1
            metrics = {k: row.get(k) for k in ("content_length", "cluster_id", "global_duplicate_count", "platform_duplicate_count", "same_product_duplicate_count", "duplicate_scope", "frequency_band")}
            output.append({
                "audit_id": f"PCA-{number:05d}", "audit_section": section, "row_uid": row["row_uid"],
                "platform": row["platform"], "product_id": row["product_id"], "review_id": row["review_id"],
                "product_category_raw": row["product_category_raw"], "normalized_category": row["normalized_category"],
                "content": row["content"], "candidate_sources": row["candidate_sources"], "primary_audit_source": source,
                "source_evidence": json.dumps(row["prototype_evidence"], ensure_ascii=False, separators=(",", ":")),
                "relevant_metrics": json.dumps(metrics, ensure_ascii=False, separators=(",", ":")),
                "duplicate_in_packet": "YES" if counts[row["row_uid"]] > 1 else "NO", "human_label": "", "human_note": "",
            })
    return output


def distributions(rows: list[dict]) -> dict:
    return {
        "platform": dict(sorted(Counter(r["platform"] for r in rows).items())),
        "category": dict(sorted(Counter(r["normalized_category"] for r in rows).items())),
    }


def expansion_summary(expansions: dict[str, list[dict]]) -> dict:
    mapping = {EXTREME_EXPANDED: EXTREME_RESULT, IMMEDIATE_EXPANDED: IMMEDIATE_EFFECT, HARD_EXPANDED: HARD_NEGATIVE}
    result = {}
    for source, rows in expansions.items():
        old = mapping[source]
        overlap = sum(old in (r["candidate_sources"] or "").split("|") for r in rows)
        newly = [r for r in rows if old not in (r["candidate_sources"] or "").split("|")]
        result[source] = {"total": len(rows), "existing_overlap": overlap, "newly_added": len(newly),
                          **distributions(rows), "newly_added_distribution": distributions(newly)}
    return result


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader(); writer.writerows(rows)


def expansion_csv_rows(expansions: dict[str, list[dict]]) -> list[dict]:
    rows = []
    for source, values in expansions.items():
        for row in values:
            rows.append({
                "row_uid": row["row_uid"], "platform": row["platform"], "product_id": row["product_id"], "review_id": row["review_id"],
                "product_category_raw": row["product_category_raw"], "normalized_category": row["normalized_category"], "content": row["content"],
                "existing_candidate_sources": row["candidate_sources"], "prototype_source": source,
                "prototype_evidence": json.dumps(row["prototype_evidence"], ensure_ascii=False, separators=(",", ":")),
                "human_label": "", "human_note": "",
            })
    return sorted(rows, key=lambda r: (r["prototype_source"], r["row_uid"]))


def _select_candidates(candidates: list[dict], target: int, used: set[str], product_counts: Counter,
                       cluster_counts: Counter, product_cap: int, cluster_cap: int) -> list[dict]:
    selected, groups = [], defaultdict(list)
    for row in candidates:
        groups[(row["normalized_category"], row["platform"])].append(row)
    for rows in groups.values():
        rows.sort(key=lambda r: stable_key(r["row_uid"]))
    keys = sorted(groups, key=lambda key: stable_key(*key))
    while len(selected) < target:
        changed = False
        for key in keys:
            rows = groups[key]
            while rows:
                row = rows.pop(0)
                uid = row["row_uid"]
                product = (row["platform"], row.get("product_id") or "")
                cluster = row.get("cluster_id")
                if uid in used or product_counts[product] >= product_cap or (cluster and cluster_counts[cluster] >= cluster_cap):
                    continue
                selected.append(row); used.add(uid); product_counts[product] += 1
                if cluster:
                    cluster_counts[cluster] += 1
                changed = True
                break
            if len(selected) >= target:
                break
        if not changed:
            break
    return selected


def simulate_scenario(plan: dict, all_existing: dict[str, list[dict]], expansions: dict[str, list[dict]], random_rows: list[dict]) -> dict:
    maps = dict(all_existing)
    old = {EXTREME_EXPANDED: EXTREME_RESULT, IMMEDIATE_EXPANDED: IMMEDIATE_EFFECT, HARD_EXPANDED: HARD_NEGATIVE}
    for source, values in expansions.items():
        maps[source] = [r for r in values if old[source] not in (r["candidate_sources"] or "").split("|")]
    used: set[str] = set(); product_counts, cluster_counts = Counter(), Counter()
    assignments, signal_rows = {}, []
    for source, target in plan["signal_source_requested"].items():
        picked = _select_candidates(maps[source], target, used, product_counts, cluster_counts,
                                    plan["caps"]["product_max_reviews"], plan["caps"]["duplicate_cluster_max_reviews"])
        assignments[source] = len(picked); signal_rows.extend(picked)
    hard_candidates = list(all_existing[HARD_NEGATIVE]) + maps[HARD_EXPANDED]
    hard_rows = _select_candidates(hard_candidates, 2500, used, product_counts, cluster_counts,
                                   plan["caps"]["product_max_reviews"], plan["caps"]["duplicate_cluster_max_reviews"])
    random_selected = _select_candidates(random_rows, 1500, used, product_counts, cluster_counts,
                                         plan["caps"]["product_max_reviews"], plan["caps"]["duplicate_cluster_max_reviews"])
    selected = signal_rows + hard_rows + random_selected
    return {
        "source_assignment_after_row_uid_dedup_and_caps": assignments,
        "bucket_unique_row_uids": {"signal_focused": len(signal_rows), "hard_negative": len(hard_rows), "random_control": len(random_selected)},
        "final_unique_row_uid": len(selected),
        "dedup_and_cap_shortfall": {"signal_focused": 6000-len(signal_rows), "hard_negative": 2500-len(hard_rows), "random_control": 1500-len(random_selected), "total_10k": 10000-len(selected)},
        "actual_platform_distribution": distributions(selected)["platform"],
        "actual_category_distribution": distributions(selected)["category"],
        "actual_duplicate_cluster_rows": sum(bool(r.get("cluster_id")) for r in selected),
        "actual_unique_duplicate_clusters": len({r["cluster_id"] for r in selected if r.get("cluster_id")}),
        "max_reviews_per_cluster": max(Counter(r["cluster_id"] for r in selected if r.get("cluster_id")).values(), default=0),
        "max_reviews_per_product": max(Counter((r["platform"], r.get("product_id") or "") for r in selected).values(), default=0),
    }


def scenario_plan(name: str, source_counts: dict, expansion_counts: dict) -> dict:
    if name == "precision_first":
        weights, cluster_cap, product_cap = {
            PRODUCT_DESCRIPTION: 574, EXTREME_RESULT: 37, EXTREME_EXPANDED: 1100,
            IMMEDIATE_EFFECT: 10, IMMEDIATE_EXPANDED: 800, PROMOTIONAL_TEMPLATE: 497,
            LOW_INFORMATION: 282, REPEATED_SHORT: 1350, EXACT_DUPLICATE: 1350,
        }, 1, 2
        category = {"BEAUTY": 2100, "FOOD": 2100, "FASHION": 900, "LIVING": 900, "HEALTH_SUPPLEMENT": 900, "ELECTRONICS": 750, "DIET": 350, "OTHER": 2000}
        platform = {"elevenst": 1900, "kurly": 2600, "musinsa": 1600, "naver": 150, "ohouse": 400, "oliveyoung": 3350}
    elif name == "balanced":
        weights, cluster_cap, product_cap = {
            PRODUCT_DESCRIPTION: 574, EXTREME_RESULT: 37, EXTREME_EXPANDED: 1300,
            IMMEDIATE_EFFECT: 10, IMMEDIATE_EXPANDED: 900, PROMOTIONAL_TEMPLATE: 497,
            LOW_INFORMATION: 282, REPEATED_SHORT: 1200, EXACT_DUPLICATE: 1200,
        }, 1, 2
        category = {"BEAUTY": 1900, "FOOD": 1900, "FASHION": 1050, "LIVING": 1000, "HEALTH_SUPPLEMENT": 1000, "ELECTRONICS": 900, "DIET": 450, "OTHER": 1800}
        platform = {"elevenst": 2000, "kurly": 2600, "musinsa": 1750, "naver": 175, "ohouse": 475, "oliveyoung": 3000}
    else:
        weights, cluster_cap, product_cap = {
            PRODUCT_DESCRIPTION: 574, EXTREME_RESULT: 37, EXTREME_EXPANDED: 1500,
            IMMEDIATE_EFFECT: 10, IMMEDIATE_EXPANDED: 1000, PROMOTIONAL_TEMPLATE: 497,
            LOW_INFORMATION: 282, REPEATED_SHORT: 1050, EXACT_DUPLICATE: 1050,
        }, 1, 1
        category = {"BEAUTY": 1600, "FOOD": 1600, "FASHION": 1200, "LIVING": 1150, "HEALTH_SUPPLEMENT": 1100, "ELECTRONICS": 1050, "DIET": 550, "OTHER": 1750}
        platform = {"elevenst": 2100, "kurly": 2400, "musinsa": 1900, "naver": 200, "ohouse": 550, "oliveyoung": 2850}
    availability = {**source_counts, **{k: v["newly_added"] for k, v in expansion_counts.items()}}
    requested = dict(weights)
    feasible = {k: min(v, availability.get(k, 0)) for k, v in requested.items()}
    source_shortfall = sum(requested.values()) - sum(feasible.values())
    return {
        "name": name, "bucket_targets": {"signal_focused": 6000, "hard_negative": 2500, "random_control": 1500},
        "signal_source_requested": requested, "signal_source_feasible_before_row_uid_dedup": feasible,
        "signal_source_availability_shortfall": source_shortfall,
        "hard_negative_availability": source_counts[HARD_NEGATIVE] + expansion_counts[HARD_EXPANDED]["newly_added"],
        "hard_negative_target_feasible": source_counts[HARD_NEGATIVE] + expansion_counts[HARD_EXPANDED]["newly_added"] >= 2500,
        "random_control_available": source_counts["RANDOM_CONTROL_ELIGIBLE"],
        "duplicate_family_requested": requested[REPEATED_SHORT] + requested[EXACT_DUPLICATE],
        "duplicate_family_share_of_signal": round((requested[REPEATED_SHORT] + requested[EXACT_DUPLICATE]) / 6000, 4),
        "caps": {"duplicate_cluster_max_reviews": cluster_cap, "normalized_text_max_reviews": cluster_cap, "product_max_reviews": product_cap},
        "category_soft_allocation_10k": category, "platform_soft_allocation_10k": platform,
        "final_unique_row_uid": None,
    }


def markdown_table(mapping: dict, left: str, right: str) -> list[str]:
    lines = [f"| {left} | {right} |", "| --- | ---: |"]
    lines.extend(f"| {k} | {v:,} |" if isinstance(v, int) else f"| {k} | {v} |" for k, v in mapping.items())
    return lines


def render_audit_md(summary: dict, audit: list[dict]) -> str:
    lines = ["# Human Review Candidate Precision Audit", "", "> 후보 source/prototype provenance이며 정답 라벨이 아닙니다. human_label과 human_note는 모두 비어 있습니다.", "",
             "## Scope", "", f"- Canonical full index: **{summary['scope']['full_index_reviews']:,}**", f"- Expansion scan: canonical candidate-content **{summary['scope']['candidate_content_reviews']:,}**건 (raw 6개 CSV가 현재 경로에 없어 full-corpus expansion은 미실행)",
             f"- Existing source audit rows: **{summary['audit']['existing_rows']:,}**", f"- Expanded audit rows: **{summary['audit']['expanded_rows']:,}**", f"- Total audit rows / unique row_uid: **{summary['audit']['total_rows']:,} / {summary['audit']['unique_row_uids']:,}**", "",
             "## Audit counts", ""]
    lines += markdown_table(summary["audit"]["section_counts"], "section", "rows")
    lines += ["", "## Audit distribution", "", "### Platform", ""] + markdown_table(summary["audit"]["platform"], "platform", "rows")
    lines += ["", "### Category", ""] + markdown_table(summary["audit"]["category"], "category", "rows")
    lines += ["", "## Expansion prototype", ""]
    for source, item in summary["expansions"].items():
        lines += [f"### {source}", "", f"- total: **{item['total']:,}** / existing overlap: **{item['existing_overlap']:,}** / expanded-only: **{item['newly_added']:,}**", f"- platforms: `{item['platform']}`", f"- categories: `{item['category']}`", f"- expanded-only platforms: `{item['newly_added_distribution']['platform']}`", f"- expanded-only categories: `{item['newly_added_distribution']['category']}`", ""]
    lines += ["## Duplicate audit composition", "", f"- REPEATED_SHORT frequency buckets: `{summary['duplicate_audit']['repeated_frequency']}`", f"- EXACT frequency buckets: `{summary['duplicate_audit']['exact_frequency']}`", f"- EXACT scopes: `{summary['duplicate_audit']['exact_scope']}`", "",
              "## Representative rows", "", "전체 content와 blank human fields는 CSV에 있습니다.", "", "| audit_id | source | platform | category | content preview |", "| --- | --- | --- | --- | --- |"]
    for row in audit[:30]:
        preview = row["content"].replace("|", "\\|").replace("\n", " ")[:90]
        lines.append(f"| {row['audit_id']} | {row['primary_audit_source']} | {row['platform']} | {row['normalized_category']} | {preview} |")
    lines += ["", "## Interpretation guardrails", "", "- 기존 37/10건은 좁은 coverage 가능성을 뜻할 뿐 실제 recall 수치가 아니다.", "- expanded 후보 증가는 성능 개선을 뜻하지 않으며 사람이 precision을 확인해야 한다.", "- sensory/일상 변화/시간적 선후관계/개인 경험형 광고 문구가 주요 false-positive 위험이다.", "- 어떤 후보도 SUSPICIOUS/NORMAL/UNCERTAIN로 자동 판정하지 않았다.", ""]
    return "\n".join(lines)


def render_dry_md(dry: dict) -> str:
    lines = ["# Human Review 10K Quota Dry-run", "", "> 실제 10K review CSV나 human label을 생성하지 않은 allocation simulation입니다.", "",
             "## Shared policy", "", "- Signal 6,000 / Hard Negative 2,500 / Random Control 1,500", "- multi-source row는 scenario의 source 우선순위 하나에만 배정하고 최종 선택 단계에서 row_uid dedup", "- duplicate/network 계열 soft cap 35~45%, cluster/normalized text/product cap 적용", "- prototype source는 사람 precision 확인 전 정답 source로 간주하지 않음", ""]
    for scenario in dry["scenarios"]:
        lines += [f"## {scenario['name']}", "", f"- buckets: `{scenario['bucket_targets']}`", f"- signal source requested: `{scenario['signal_source_requested']}`", f"- feasible before row_uid dedup: `{scenario['signal_source_feasible_before_row_uid_dedup']}`", f"- availability shortfall before dedup: **{scenario['signal_source_availability_shortfall']:,}**", f"- source assignment after row_uid dedup/caps: `{scenario['source_assignment_after_row_uid_dedup_and_caps']}`", f"- unique bucket rows: `{scenario['bucket_unique_row_uids']}`", f"- final unique row_uid / total shortfall: **{scenario['final_unique_row_uid']:,} / {scenario['dedup_and_cap_shortfall']['total_10k']:,}**", f"- hard-negative available / target feasible: **{scenario['hard_negative_availability']:,} / {scenario['hard_negative_target_feasible']}**", f"- duplicate family requested share: **{scenario['duplicate_family_share_of_signal']:.1%}**", f"- actual duplicate cluster rows / unique clusters: **{scenario['actual_duplicate_cluster_rows']:,} / {scenario['actual_unique_duplicate_clusters']:,}**", f"- caps: `{scenario['caps']}`; observed max cluster/product: `{scenario['max_reviews_per_cluster']}/{scenario['max_reviews_per_product']}`", f"- actual category allocation: `{scenario['actual_category_distribution']}`", f"- actual platform allocation: `{scenario['actual_platform_distribution']}`", ""]
    lines += ["## Recommendation", "", "**Balanced**를 권장한다. signal coverage를 늘리면서 duplicate 계열을 40% 이하로 제한하고, oliveyoung/BEAUTY와 kurly/FOOD 집중을 완화하며 DIET·HEALTH_SUPPLEMENT·FASHION·LIVING·ELECTRONICS representation을 확보한다.", "",
              "## Human review gates", "", "1. expanded-only audit precision 확인", "2. source별 precision과 reviewer agreement 확인", "3. category/platform/product/cluster caps 확정", "4. 그 뒤에만 별도 승인으로 실제 10K pool materialization", ""]
    return "\n".join(lines)


def build(args) -> tuple[dict, dict]:
    outputs = [args.audit_csv, args.expansion_csv, args.audit_md, args.audit_json, args.dry_md, args.dry_json]
    if any(Path(p).exists() for p in outputs):
        raise FileExistsError("기존 결과를 덮어쓰지 않습니다: " + ", ".join(str(p) for p in outputs if Path(p).exists()))
    with connect_read_only(args.database) as db:
        if db.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise ValueError("canonical manifest quick_check failed")
        full_count = db.execute("SELECT COUNT(*) FROM review_index").fetchone()[0]
        content_count = db.execute("SELECT COUNT(*) FROM candidate_content").fetchone()[0]
        source_counts = {k: v for k, v in db.execute("SELECT candidate_source,COUNT(*) FROM source_evidence GROUP BY candidate_source")}
        source_counts["RANDOM_CONTROL_ELIGIBLE"] = db.execute("SELECT COUNT(*) FROM random_control_eligible").fetchone()[0]
        expansions, all_existing = expansion_scan(db)
        existing = choose_existing_audit(all_existing)
        expanded = choose_expanded_audit(expansions, existing)
        random_rows = [dict(zip(("row_uid", "platform", "product_id", "normalized_category"), row)) | {"cluster_id": None}
                       for row in db.execute("""
                         SELECT row_uid,platform,product_id,normalized_category FROM (
                           SELECT r.row_uid,r.platform,r.product_id,r.normalized_category,
                                  ROW_NUMBER() OVER (PARTITION BY r.platform,r.product_id ORDER BY r.row_uid) product_rank
                           FROM random_control_eligible e JOIN review_index r USING(row_uid)
                         ) WHERE product_rank<=2 ORDER BY normalized_category,platform,row_uid
                       """)]
    audit = audit_rows(existing, expanded)
    if any(r["human_label"] or r["human_note"] for r in audit):
        raise AssertionError("human fields must remain blank")
    exp_summary = expansion_summary(expansions)
    existing_n = sum(len(v) for v in existing.values()); expanded_n = sum(len(v) for v in expanded.values())
    audit_summary = {
        "analysis_type": "label-blank candidate precision audit and prototype expansion",
        "scope": {"full_index_reviews": full_count, "candidate_content_reviews": content_count, "expansion_scan_scope": "canonical candidate_content; raw export CSVs unavailable at execution", "canonical_manifest_modified": False, "final_10k_pool_created": False, "automatic_human_labels_created": False},
        "audit": {"existing_rows": existing_n, "expanded_rows": expanded_n, "total_rows": len(audit), "unique_row_uids": len({r['row_uid'] for r in audit}), "duplicate_audit_rows": sum(r["duplicate_in_packet"] == "YES" for r in audit), "section_counts": dict(Counter(r["audit_section"] for r in audit)), **distributions(audit)},
        "existing_source_counts": source_counts, "expansions": exp_summary,
        "duplicate_audit": {"repeated_frequency": dict(Counter(r.get("frequency_band") for r in existing[REPEATED_SHORT])), "exact_frequency": dict(Counter(r.get("frequency_band") for r in existing[EXACT_DUPLICATE])), "exact_scope": dict(Counter(r.get("duplicate_scope") for r in existing[EXACT_DUPLICATE]))},
        "limitations": ["raw 6-platform CSVs were unavailable; expansion recall outside canonical candidate_content was not measured", "candidate counts do not establish precision or recall", "human labels remain blank"],
    }
    scenarios = []
    for name in ("precision_first", "balanced", "diversity_first"):
        scenario = scenario_plan(name, source_counts, exp_summary)
        scenario.update(simulate_scenario(scenario, all_existing, expansions, random_rows))
        scenarios.append(scenario)
    dry = {"analysis_type": "allocation-only dry-run; no review dataset", "scenarios": scenarios, "recommended_scenario": "balanced", "created_final_10k_pool": False, "automatic_human_labels_created": False}
    write_csv(Path(args.audit_csv), AUDIT_FIELDS, audit)
    exp_rows = expansion_csv_rows(expansions)
    write_csv(Path(args.expansion_csv), ["row_uid", "platform", "product_id", "review_id", "product_category_raw", "normalized_category", "content", "existing_candidate_sources", "prototype_source", "prototype_evidence", "human_label", "human_note"], exp_rows)
    Path(args.audit_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.audit_json).write_text(json.dumps(audit_summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    Path(args.audit_md).write_text(render_audit_md(audit_summary, audit), encoding="utf-8")
    Path(args.dry_json).write_text(json.dumps(dry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    Path(args.dry_md).write_text(render_dry_md(dry), encoding="utf-8")
    return audit_summary, dry


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Create label-blank audit/prototype outputs; never a final 10K pool")
    p.add_argument("--database", type=Path, default=DEFAULT_DB)
    p.add_argument("--audit-csv", type=Path, default=DEFAULT_AUDIT)
    p.add_argument("--expansion-csv", type=Path, default=DEFAULT_EXPANSION)
    p.add_argument("--audit-md", type=Path, default=DEFAULT_AUDIT_MD)
    p.add_argument("--audit-json", type=Path, default=DEFAULT_AUDIT_JSON)
    p.add_argument("--dry-md", type=Path, default=DEFAULT_DRY_MD)
    p.add_argument("--dry-json", type=Path, default=DEFAULT_DRY_JSON)
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    try:
        audit, dry = build(args)
        print(json.dumps({"audit_rows": audit["audit"]["total_rows"], "unique_row_uids": audit["audit"]["unique_row_uids"], "expansions": audit["expansions"], "recommended": dry["recommended_scenario"]}, ensure_ascii=False, indent=2))
        print("AUTOMATIC_HUMAN_LABELS_CREATED=false\nFINAL_10K_POOL_CREATED=false\nCANONICAL_MANIFEST_MODIFIED=false")
        return 0
    except Exception as exc:
        print(f"오류: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
