"""Diagnose v3 quota bottlenecks without creating a review dataset or labels."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = PROJECT_ROOT / "outputs" / "large_human_review_candidate_manifest_20261028.sqlite3"
DEFAULT_EXPANSION = PROJECT_ROOT / "outputs" / "human_review_rule_expansion_candidates_20261028_v3.csv"
DEFAULT_V3 = PROJECT_ROOT / "reports" / "human_review_10k_quota_dry_run_20261028_v3.json"
DEFAULT_JSON = PROJECT_ROOT / "reports" / "human_review_10k_bottleneck_audit_20261030.json"
DEFAULT_MD = PROJECT_ROOT / "reports" / "human_review_10k_bottleneck_audit_20261030.md"

PRODUCT = "PRODUCT_DESCRIPTION_REPLACEMENT"
EXTREME = "EXTREME_RESULT_CLAIM"
EXTREME_X = "EXTREME_RESULT_EXPANDED_PROTOTYPE"
IMMEDIATE = "IMMEDIATE_EFFECT_CLAIM"
IMMEDIATE_X = "IMMEDIATE_EFFECT_EXPANDED_PROTOTYPE"
PROMOTIONAL = "PROMOTIONAL_TEMPLATE"
LOW_INFO = "LOW_INFORMATION_PRAISE"
REPEATED = "REPEATED_SHORT_TEMPLATE"
EXACT = "EXACT_DUPLICATE_CLUSTER"
HARD = "HARD_NEGATIVE_CANDIDATE"
HARD_X = "HARD_NEGATIVE_EXPANDED_CANDIDATE"
RANDOM = "RANDOM_CONTROL_ELIGIBLE"
SIGNAL_ORDER = (PRODUCT, EXTREME, EXTREME_X, IMMEDIATE, IMMEDIATE_X, PROMOTIONAL, LOW_INFO, REPEATED, EXACT)
_ORDER_CACHE: dict[tuple[int, int, str], tuple[list[dict], list[dict]]] = {}
_GROUP_CACHE: dict[tuple[int, int], tuple[list[dict], list[tuple], dict[tuple, list[dict]]]] = {}


def stable_key(*values: object) -> str:
    return sha256("\x1f".join(str(v) for v in values).encode()).hexdigest()


def ro_connect(path: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{path.resolve().as_posix()}?mode=ro", uri=True)


def candidate(row) -> dict:
    keys = ("row_uid", "platform", "product_id", "normalized_category", "normalized_content_hash", "cluster_id")
    return dict(zip(keys, row))


def load_candidates(db: sqlite3.Connection, expansion_path: Path) -> tuple[dict, list[dict], dict]:
    meta = {}
    for row in db.execute("""
      SELECT r.row_uid,r.platform,r.product_id,r.normalized_category,r.normalized_content_hash,dm.cluster_id
      FROM review_index r JOIN candidate_content c USING(row_uid)
      LEFT JOIN duplicate_members dm USING(row_uid)
    """):
        item = candidate(row); meta[item["row_uid"]] = item

    sources = {source: [] for source in SIGNAL_ORDER + (HARD, HARD_X)}
    memberships: dict[str, set[str]] = defaultdict(set)
    for uid, source in db.execute("SELECT row_uid,candidate_source FROM source_evidence"):
        memberships[uid].add(source)
        if source in sources:
            sources[source].append(meta[uid])

    with expansion_path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            source, uid = row["prototype_source"], row["row_uid"]
            old = {EXTREME_X: EXTREME, IMMEDIATE_X: IMMEDIATE, HARD_X: HARD}[source]
            if old not in row["existing_candidate_sources"].split("|"):
                sources[source].append(meta[uid])
                memberships[uid].add(source)

    random_rows = []
    for row in db.execute("""
      SELECT row_uid,platform,product_id,normalized_category,normalized_content_hash,cluster_id,product_rank FROM (
        SELECT r.row_uid,r.platform,r.product_id,r.normalized_category,r.normalized_content_hash,dm.cluster_id,
               ROW_NUMBER() OVER (PARTITION BY r.platform,r.product_id ORDER BY r.row_uid) product_rank
        FROM random_control_eligible e JOIN review_index r USING(row_uid)
        LEFT JOIN duplicate_members dm USING(row_uid)
      ) WHERE product_rank<=5 ORDER BY normalized_category,platform,row_uid
    """):
        item = candidate(row[:6]); item["product_rank"] = row[6]; random_rows.append(item)
        memberships[item["row_uid"]].add(RANDOM)

    stats = {
        "full_reviews": db.execute("SELECT COUNT(*) FROM review_index").fetchone()[0],
        "candidate_content": len(meta),
        "random_eligible": db.execute("SELECT COUNT(*) FROM random_control_eligible").fetchone()[0],
        "random_product_window_rows": len(random_rows),
    }
    return sources, random_rows, {"memberships": memberships, **stats}


def ordered(rows: list[dict], mode: str) -> list[dict]:
    cache_key = (id(rows), len(rows), mode)
    cached = _ORDER_CACHE.get(cache_key)
    if cached is not None:
        return cached[1]
    unique = {row["row_uid"]: row for row in rows}
    if mode == "flat":
        result = sorted(unique.values(), key=lambda row: stable_key(row["row_uid"]))
        _ORDER_CACHE[cache_key] = (rows, result)
        return result
    groups = defaultdict(list)
    for row in unique.values():
        groups[(row["normalized_category"], row["platform"])].append(row)
    for values in groups.values():
        values.sort(key=lambda row: stable_key(row["row_uid"]))
    keys = sorted(groups, key=lambda key: stable_key(*key))
    result = []
    while True:
        changed = False
        for key in keys:
            if groups[key]:
                result.append(groups[key].pop(0)); changed = True
        if not changed:
            _ORDER_CACHE[cache_key] = (rows, result)
            return result


class State:
    def __init__(self):
        self.used: set[str] = set()
        self.products = Counter()
        self.clusters = Counter()
        self.texts = Counter()

    def copy(self):
        other = State()
        other.used = set(self.used); other.products = self.products.copy()
        other.clusters = self.clusters.copy(); other.texts = self.texts.copy()
        return other


def choose(rows: list[dict], target: int, state: State, product_cap: int | None,
           cluster_cap: int | None, text_cap: int | None, mode: str,
           mutate: bool = True) -> list[dict]:
    work = state if mutate else state.copy()
    selected = []
    def accept(row):
        uid = row["row_uid"]
        product = (row["platform"], row.get("product_id") or "")
        cluster, text_hash = row.get("cluster_id"), row.get("normalized_content_hash")
        if uid in work.used:
            return False
        if product_cap is not None and work.products[product] >= product_cap:
            return False
        if cluster and cluster_cap is not None and work.clusters[cluster] >= cluster_cap:
            return False
        if text_hash and text_cap is not None and work.texts[text_hash] >= text_cap:
            return False
        selected.append(row); work.used.add(uid); work.products[product] += 1
        if cluster:
            work.clusters[cluster] += 1
        if text_hash:
            work.texts[text_hash] += 1
        return True

    if mode == "flat":
        for row in ordered(rows, mode):
            accept(row)
            if len(selected) >= target:
                break
        return selected

    cache_key = (id(rows), len(rows))
    cached = _GROUP_CACHE.get(cache_key)
    if cached is None:
        unique = {row["row_uid"]: row for row in rows}
        groups = defaultdict(list)
        for row in unique.values():
            groups[(row["normalized_category"], row["platform"])].append(row)
        for values in groups.values():
            values.sort(key=lambda row: stable_key(row["row_uid"]))
        keys = sorted(groups, key=lambda key: stable_key(*key))
        cached = (rows, keys, dict(groups)); _GROUP_CACHE[cache_key] = cached
    _, keys, groups = cached
    indexes = Counter()
    while len(selected) < target:
        changed = False
        for key in keys:
            values = groups[key]
            while indexes[key] < len(values):
                row = values[indexes[key]]; indexes[key] += 1
                if accept(row):
                    changed = True; break
            if len(selected) >= target:
                break
        if not changed:
            break
    return selected


def select_with_attribution(label: str, rows: list[dict], requested: int, state: State,
                            config: dict) -> tuple[list[dict], dict]:
    pool_ids = {row["row_uid"] for row in rows}
    available = len(pool_ids)
    raw_already_used = len(pool_ids & state.used)
    no_caps = len(choose(rows, requested, state, None, None, None, config["ordering"], False))
    product = len(choose(rows, requested, state, config["product_cap"], None, None, config["ordering"], False))
    product_cluster = len(choose(rows, requested, state, config["product_cap"], config["cluster_cap"], None, config["ordering"], False))
    selected = choose(rows, requested, state, config["product_cap"], config["cluster_cap"], config["text_cap"], config["ordering"], True)
    selected_n = len(selected)
    losses = {
        "source_availability": requested - min(requested, available),
        "row_uid_collision": min(requested, available) - no_caps,
        "product_cap": no_caps - product,
        "duplicate_cluster_cap": product - product_cluster,
        "normalized_text_cap": product_cluster - selected_n,
    }
    if any(value < 0 for value in losses.values()) or sum(losses.values()) != requested - selected_n:
        raise AssertionError((label, losses, requested, selected_n))
    return selected, {"requested": requested, "available": available,
                      "raw_row_uids_already_used": raw_already_used,
                      "available_after_row_uid_exclusion": available-raw_already_used,
                      "selected": selected_n,
                      "unfilled": requested-selected_n, "sequential_loss_attribution": losses}


def distributions(rows: list[dict]) -> dict:
    return {
        "platform": dict(sorted(Counter(row["platform"] for row in rows).items())),
        "category": dict(sorted(Counter(row["normalized_category"] for row in rows).items())),
    }


def metrics(rows: list[dict], state: State, source_selected: dict, bucket_selected: dict, diagnostics: dict) -> dict:
    products = {(r["platform"], r.get("product_id") or "") for r in rows}
    clusters = [r["cluster_id"] for r in rows if r.get("cluster_id")]
    texts = [r["normalized_content_hash"] for r in rows if r.get("normalized_content_hash")]
    duplicate_cluster_counts = Counter(clusters); text_counts = Counter(texts)
    return {
        "final_unique_row_uid": len({r["row_uid"] for r in rows}),
        "target_shortfall": 10000-len({r["row_uid"] for r in rows}),
        "bucket_selected": bucket_selected,
        "source_selected": source_selected,
        "source_diagnostics": diagnostics,
        **distributions(rows),
        "unique_products": len(products),
        "unique_duplicate_clusters": len(set(clusters)),
        "rows_in_duplicate_clusters": len(clusters),
        "max_rows_per_duplicate_cluster": max(duplicate_cluster_counts.values(), default=0),
        "normalized_texts_repeated_in_selection": sum(count > 1 for count in text_counts.values()),
        "max_rows_per_normalized_text": max(text_counts.values(), default=0),
    }


def simulate(name: str, quotas: dict, sources: dict, random_rows: list[dict], config: dict) -> dict:
    state, all_rows, source_selected, diagnostics = State(), [], {}, {}
    bucket_selected = {"signal_focused": 0, "hard_negative": 0, "random_control": 0}
    bucket_order = config.get("bucket_order", ("signal", "hard", "random"))

    def run_signal():
        rows_out = []
        if config.get("signal_union_fill"):
            pool = [row for source in SIGNAL_ORDER for row in sources[source]]
            selected, diag = select_with_attribution("SIGNAL_UNION", pool, 6000, state, config)
            source_selected["SIGNAL_UNION"] = len(selected); diagnostics["SIGNAL_UNION"] = diag
            return selected
        for source in config.get("signal_order", SIGNAL_ORDER):
            selected, diag = select_with_attribution(source, sources[source], quotas[source], state, config)
            rows_out.extend(selected); source_selected[source] = len(selected); diagnostics[source] = diag
        return rows_out

    def run_hard():
        pool = sources[HARD] + sources[HARD_X]
        selected, diag = select_with_attribution("HARD_NEGATIVE_UNION", pool, 2500, state, config)
        source_selected["HARD_NEGATIVE_UNION"] = len(selected); diagnostics["HARD_NEGATIVE_UNION"] = diag
        selected_ids = {r["row_uid"] for r in selected}
        existing_ids = {r["row_uid"] for r in sources[HARD]}
        source_selected[HARD] = len(selected_ids & existing_ids)
        source_selected[HARD_X] = len(selected_ids - existing_ids)
        return selected

    def run_random():
        frame = [r for r in random_rows if r["product_rank"] <= (config["product_cap"] or 5)]
        if not config.get("random_duplicate_metadata", False):
            frame = [dict(r, cluster_id=None, normalized_content_hash=None) for r in frame]
        selected, diag = select_with_attribution(RANDOM, frame, 1500, state, config)
        diag["diagnostic_frame_available"] = diag["available"]
        diag["raw_row_uids_already_used_in_frame"] = diag["raw_row_uids_already_used"]
        diag["available"] = config["random_available"]
        diag["raw_row_uids_already_used"] = None
        diag["available_after_row_uid_exclusion"] = None
        source_selected[RANDOM] = len(selected); diagnostics[RANDOM] = diag
        return selected

    runners = {"signal": (run_signal, "signal_focused"), "hard": (run_hard, "hard_negative"), "random": (run_random, "random_control")}
    for bucket in bucket_order:
        selected = runners[bucket][0](); all_rows.extend(selected); bucket_selected[runners[bucket][1]] = len(selected)
    result = {"name": name, "policy": {k: v for k, v in config.items() if k != "random_available"}}
    result.update(metrics(all_rows, state, source_selected, bucket_selected, diagnostics))
    return result


def availability_adjusted_quotas(quotas: dict, sources: dict) -> dict:
    return {source: min(quotas[source], len({r["row_uid"] for r in sources[source]})) for source in SIGNAL_ORDER}


def hard_independent_capacity(sources: dict, product_caps=(1, 2, 3, 5)) -> dict:
    pool = sources[HARD] + sources[HARD_X]
    result = {}
    for cap in product_caps:
        state = State()
        picked = choose(pool, 2500, state, cap, 1, None, "round_robin", True)
        result[str(cap)] = {"selected_from_empty_state": len(picked), "target_shortfall": 2500-len(picked),
                            "unique_products": len({(r['platform'],r.get('product_id') or '') for r in picked})}
    state = State(); picked = choose(pool, 2500, state, None, None, None, "round_robin", True)
    result["unlimited"] = {"selected_from_empty_state": len(picked), "target_shortfall": 2500-len(picked)}
    return result


def schema_audit(db: sqlite3.Connection, stats: dict) -> dict:
    tables = {name: sql for name, sql in db.execute("SELECT name,sql FROM sqlite_master WHERE type IN ('table','view')")}
    raw_present = all((PROJECT_ROOT / "data" / "review-export" / f"reviews_{p}.csv").exists() for p in ("elevenst","kurly","musinsa","naver","ohouse","oliveyoung"))
    return {
        "review_index_rows": stats["full_reviews"], "candidate_content_rows": stats["candidate_content"],
        "candidate_manifest_rows": db.execute("SELECT COUNT(*) FROM candidate_manifest").fetchone()[0],
        "source_evidence_rows": db.execute("SELECT COUNT(*) FROM source_evidence").fetchone()[0],
        "random_control_eligible_rows": stats["random_eligible"],
        "all_review_fields_available": ["row_uid","platform","source_row","product_id","review_id","product_category_raw","normalized_category","normalized_content_hash","content_length","valid_identity","valid_content"],
        "content_available_for_all_reviews": False,
        "content_available_rows": stats["candidate_content"],
        "content_missing_outside_candidate_content": stats["full_reviews"]-stats["candidate_content"],
        "can_apply_new_text_rules_outside_candidate_content": False,
        "raw_csvs_currently_present": raw_present,
        "required_full_scan_inputs": [f"reviews_{p}.csv" for p in ("elevenst","kurly","musinsa","naver","ohouse","oliveyoung")],
        "required_columns": ["platform","product_id","review_id","content","product_category"],
        "safe_full_corpus_conditions": ["all six immutable raw CSVs mounted read-only", "size/mtime/SHA signatures captured before and after", "row count and platform identity validated", "prototype outputs written to new paths", "canonical SQLite and annotations opened read-only", "no labels and no final 10K pool"],
        "relevant_objects": sorted(tables),
    }


def render_md(report: dict) -> str:
    lines = ["# Human Review 10K Quota Bottleneck Audit", "", "> 진단용 in-memory simulation입니다. human label과 실제 10K review dataset을 생성하지 않았고 canonical SQLite를 read-only로 열었습니다.", "",
             "## Executive findings", ""]
    for item in report["findings"]:
        lines.append(f"- {item}")
    lines += ["", "## v3 reproduction and sequential loss attribution", ""]
    for scenario in report["v3_reproduction"]:
        lines += [f"### {scenario['name']}", "", f"- buckets: `{scenario['bucket_selected']}` / unique **{scenario['final_unique_row_uid']:,}** / shortfall **{scenario['target_shortfall']:,}**", f"- source selected: `{scenario['source_selected']}`", "", "| source/bucket | requested | available | already used | selected | unfilled | availability | row_uid target loss | product | cluster | text |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
        for source, d in scenario["source_diagnostics"].items():
            loss = d["sequential_loss_attribution"]
            lines.append(f"| {source} | {d['requested']} | {d['available']} | {d['raw_row_uids_already_used']} | {d['selected']} | {d['unfilled']} | {loss['source_availability']} | {loss['row_uid_collision']} | {loss['product_cap']} | {loss['duplicate_cluster_cap']} | {loss['normalized_text_cap']} |")
        lines += ["", f"- platform: `{scenario['platform']}`", f"- category: `{scenario['category']}`", f"- unique products/clusters: **{scenario['unique_products']:,} / {scenario['unique_duplicate_clusters']:,}**", ""]
    lines += ["## Balanced hard-negative bottleneck", "", f"- raw union availability: **{report['balanced_hard_negative']['raw_union_available']:,}**", f"- v3 selected: **{report['balanced_hard_negative']['v3_selected']:,} / 2,500**", f"- independent capacity from empty state: `{report['balanced_hard_negative']['independent_capacity']}`", "- 따라서 12,275는 단순 union cardinality이며 현재 signal 선점과 product/cluster/text cap을 통과하는 독립 선택 가능 수량이 아니다.", ""]
    lines += ["## Sensitivity", "", "| policy | unique | signal | hard | random | shortfall | products | clusters | max text |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for item in report["sensitivity"]:
        b = item["bucket_selected"]
        lines.append(f"| {item['name']} | {item['final_unique_row_uid']} | {b['signal_focused']} | {b['hard_negative']} | {b['random_control']} | {item['target_shortfall']} | {item['unique_products']} | {item['unique_duplicate_clusters']} | {item['max_rows_per_normalized_text']} |")
    lines += ["", "## Candidate-only ceiling and limits", "", f"- tested maximum: **{report['tested_maximum']['final_unique_row_uid']:,}** (`{report['tested_maximum']['name']}`)", f"- buckets: `{report['tested_maximum']['bucket_selected']}`", f"- unique products: **{report['tested_maximum']['unique_products']:,}**; rows in duplicate clusters / unique clusters: **{report['tested_maximum']['rows_in_duplicate_clusters']:,} / {report['tested_maximum']['unique_duplicate_clusters']:,}**", "- union-fill은 source quota를 제거하므로 기술적 capacity 진단일 뿐 권장 sampling 정책이 아니다. duplicate/network 계열과 검증 전 prototype이 지배할 위험이 있다.", ""]
    schema = report["schema_audit"]
    lines += ["## Full-corpus availability", "", f"- review_index: **{schema['review_index_rows']:,}** / candidate_content: **{schema['candidate_content_rows']:,}** / missing content: **{schema['content_missing_outside_candidate_content']:,}**", f"- raw CSVs present: **{schema['raw_csvs_currently_present']}**", "- review_index는 전체 identity/category/hash/length/source_row를 보존하지만 content는 candidate_content에만 있다.", "- 따라서 candidate 외부에 새 text rule을 적용하려면 원본 6개 CSV가 필요하며, 현재는 재스캔하지 않았다.", "", "## Recommended next actions", "", "1. expanded-only precision audit 완료 전 prototype quota 확대 금지", "2. Balanced에서 product cap 3 민감도와 hard-negative category/product coverage를 사람이 검토", "3. duplicate source quota뿐 아니라 전체 selected rows의 cluster/text 비율을 제약", "4. 6개 raw CSV를 read-only로 다시 제공한 뒤 별도 full-corpus prototype을 실행", "5. 승인 전까지 실제 10K pool과 human label을 생성하지 않음", ""]
    return "\n".join(lines)


def build(args) -> dict:
    if (args.json.exists() or args.markdown.exists()) and not args.replace_diagnostic:
        raise FileExistsError("기존 진단 결과를 덮어쓰지 않습니다")
    v3 = json.loads(args.v3.read_text(encoding="utf-8"))
    quotas_by_name = {item["name"]: item["signal_source_requested"] for item in v3["scenarios"]}
    with ro_connect(args.database) as db:
        if db.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise ValueError("canonical SQLite quick_check failed")
        sources, random_rows, stats = load_candidates(db, args.expansion)
        schema = schema_audit(db, stats)
    base = {"product_cap": 2, "cluster_cap": 1, "text_cap": None, "ordering": "round_robin", "bucket_order": ("signal","hard","random"), "random_available": stats["random_eligible"], "random_duplicate_metadata": False}
    v3_product_caps = {item["name"]: item["caps"]["product_max_reviews"] for item in v3["scenarios"]}
    reproduced = [simulate(name, quotas_by_name[name], sources, random_rows, dict(base, product_cap=v3_product_caps[name])) for name in ("precision_first","balanced","diversity_first")]
    expected = {item["name"]: item["final_unique_row_uid"] for item in v3["scenarios"]}
    for item in reproduced:
        if item["final_unique_row_uid"] != expected[item["name"]]:
            raise AssertionError(f"v3 reproduction mismatch: {item['name']} {item['final_unique_row_uid']} != {expected[item['name']]}; buckets={item['bucket_selected']}; sources={item['source_selected']}")
    balanced = quotas_by_name["balanced"]
    sensitivity = []
    adjusted = availability_adjusted_quotas(balanced, sources)
    sensitivity.append(simulate("availability_adjusted_quotas", adjusted, sources, random_rows, base))
    for order in (("hard","signal","random"), ("random","hard","signal")):
        cfg = dict(base, bucket_order=order)
        sensitivity.append(simulate("bucket_order_"+"-".join(order), balanced, sources, random_rows, cfg))
    for cap in (1,2,3,5):
        sensitivity.append(simulate(f"product_cap_{cap}", balanced, sources, random_rows, dict(base, product_cap=cap)))
    for cluster_cap, text_cap in ((1,1),(1,2),(2,1),(2,2),(5,5),(None,None)):
        label = f"cluster_{cluster_cap or 'none'}_text_{text_cap or 'none'}"
        sensitivity.append(simulate(label, balanced, sources, random_rows, dict(base, cluster_cap=cluster_cap, text_cap=text_cap)))
    sensitivity.append(simulate("flat_order_no_category_platform_round_robin", balanced, sources, random_rows, dict(base, ordering="flat")))
    sensitivity.append(simulate("random_with_duplicate_metadata", balanced, sources, random_rows, dict(base, random_duplicate_metadata=True)))
    sensitivity.append(simulate("signal_source_priority_reversed", balanced, sources, random_rows, dict(base, signal_order=tuple(reversed(SIGNAL_ORDER)))))
    duplicate_first = (REPEATED, EXACT, PRODUCT, EXTREME, EXTREME_X, IMMEDIATE, IMMEDIATE_X, PROMOTIONAL, LOW_INFO)
    sensitivity.append(simulate("signal_source_priority_duplicate_first", balanced, sources, random_rows, dict(base, signal_order=duplicate_first)))
    union_policies = []
    for product_cap in (2,3,5):
        union_policies.append(simulate(f"signal_union_fill_product_{product_cap}", balanced, sources, random_rows, dict(base, product_cap=product_cap, signal_union_fill=True)))
    tested_max = max(reproduced+sensitivity+union_policies, key=lambda item: item["final_unique_row_uid"])
    balanced_repro = next(item for item in reproduced if item["name"] == "balanced")
    report = {
        "analysis_type": "read-only quota bottleneck diagnostics; no labels or review dataset",
        "v3_reproduction": reproduced,
        "balanced_hard_negative": {"raw_union_available": 12275, "v3_selected": balanced_repro["bucket_selected"]["hard_negative"], "sequential_diagnostics": balanced_repro["source_diagnostics"]["HARD_NEGATIVE_UNION"], "independent_capacity": hard_independent_capacity(sources)},
        "sensitivity": sensitivity + union_policies,
        "tested_maximum": tested_max,
        "schema_audit": schema,
        "findings": [
            "v3의 category/platform balancing은 round-robin ordering이며 hard cap이나 quota rejection이 아니다.",
            "Signal은 expanded EXTREME/IMMEDIATE의 requested quota가 availability를 크게 초과해 cap 적용 전부터 부족하다.",
            "Balanced HARD_NEGATIVE 12,275는 raw union cardinality이며 signal 선점 및 product/cluster/text cap 이후의 독립 capacity가 아니다.",
            "duplicate cluster와 normalized text는 canonical exact-duplicate 데이터에서 같은 hash cluster를 표현하므로 cap=1에서는 효과가 중첩된다.",
            "source priority와 bucket order가 row_uid 선점 상태를 바꾸므로 손실은 독립적으로 합산할 수 없다.",
            "v3 random-control frame에는 cluster/hash metadata가 전달되지 않아 random bucket에는 duplicate/text cap이 적용되지 않았다.",
            "v3 보고서의 normalized_text_max_reviews=1 표기와 달리 선택 함수에는 별도 normalized-text cap이 구현되지 않았다.",
        ],
        "safety": {"automatic_human_labels_created": False, "final_10k_pool_created": False, "canonical_sqlite_modified": False, "v3_outputs_modified": False},
    }
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    args.markdown.write_text(render_md(report), encoding="utf-8")
    return report


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, default=DEFAULT_DB)
    parser.add_argument("--expansion", type=Path, default=DEFAULT_EXPANSION)
    parser.add_argument("--v3", type=Path, default=DEFAULT_V3)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MD)
    parser.add_argument("--replace-diagnostic", action="store_true", help="replace only this task's newly generated diagnostic reports")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    try:
        report = build(parse_args(argv))
        print(json.dumps({"reproduced": {x["name"]: x["final_unique_row_uid"] for x in report["v3_reproduction"]}, "tested_maximum": {"name": report["tested_maximum"]["name"], "unique": report["tested_maximum"]["final_unique_row_uid"]}}, ensure_ascii=False, indent=2))
        print("AUTOMATIC_HUMAN_LABELS_CREATED=false\nFINAL_10K_POOL_CREATED=false\nCANONICAL_SQLITE_MODIFIED=false")
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr); return 1


if __name__ == "__main__":
    raise SystemExit(main())
