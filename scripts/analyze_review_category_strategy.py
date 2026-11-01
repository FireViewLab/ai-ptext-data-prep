"""Read-only category distribution and human-review pool strategy analysis.

This script does not create a review pool, assign labels, run a model, or edit
source reviews. It streams the six review exports and writes aggregate reports.
The normalized category mapping is explicitly provisional and always preserves
the source ``product_category`` value alongside it.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from dataclasses import dataclass, field
import json
import math
from pathlib import Path
import re
import sys
import unicodedata

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from analyze_new_review_inventory import (  # noqa: E402
    DEFAULT_INPUTS,
    PROJECT_ROOT,
    canonical_identifier,
    portable_report_path,
)


PLATFORMS = tuple(DEFAULT_INPUTS)
EXPECTED_TOTAL = 1_151_943
NORMALIZED_CATEGORIES = (
    "BEAUTY",
    "HEALTH_SUPPLEMENT",
    "DIET",
    "FOOD",
    "FASHION",
    "LIVING",
    "ELECTRONICS",
    "BABY",
    "PET",
    "SPORTS_OUTDOOR",
    "ETC_UNKNOWN",
)

DEFAULT_V1 = PROJECT_ROOT / "outputs" / "new_description_candidates_20261018.csv"
DEFAULT_ANNOTATION = PROJECT_ROOT / "annotations" / "description_human_review_v1.csv"
DEFAULT_INVENTORY = PROJECT_ROOT / "reports" / "new_review_inventory_20261018.json"
DEFAULT_JSON = PROJECT_ROOT / "reports" / "review_category_strategy_20261028.json"
DEFAULT_MARKDOWN = PROJECT_ROOT / "reports" / "review_category_strategy_20261028.md"


class CategoryAnalysisError(ValueError):
    """Raised when source data cannot be analyzed without ambiguity."""


@dataclass
class CandidateSet:
    name: str
    rows: list[dict[str, str]]
    matched_ids: set[str] = field(default_factory=set)
    raw_categories: Counter = field(default_factory=Counter)
    normalized_categories: Counter = field(default_factory=Counter)
    platforms: Counter = field(default_factory=Counter)
    products: set[tuple[str, str]] = field(default_factory=set)


def is_blank(value: str | None) -> bool:
    return value is None or value.strip() == ""


def category_root(raw_category: str) -> str:
    return re.split(r"\s*>\s*", raw_category, maxsplit=1)[0].strip()


def canonical_category_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    value = re.sub(r"\s*>\s*", ">", value)
    return " ".join(value.split()).casefold()


def normalize_category(platform: str, raw_category: str | None) -> tuple[str, str]:
    """Return a conservative provisional top-level category and rule reason."""

    if is_blank(raw_category):
        return "ETC_UNKNOWN", "blank source category"

    raw = str(raw_category).strip()
    root = category_root(raw)
    lower = raw.casefold()

    if any(token in raw for token in ("출산/육아", "유아", "기저귀")) or root == "Kids":
        return "BABY", "explicit baby/child term"
    if any(token in raw for token in ("반려", "강아지", "고양이")) or root == "Pet":
        return "PET", "explicit pet term"
    if any(token in raw for token in ("다이어트", "체중조절", "슬리밍")):
        return "DIET", "explicit diet term"
    if (
        root in {"건강식품", "건강기능식품", "일반건강식품"}
        or any(token in raw for token in ("건강기능식품", "영양제", "유산균", "비타민/미네랄"))
    ):
        return "HEALTH_SUPPLEMENT", "explicit supplement term"

    if platform == "kurly":
        special = {
            "뷰티 인디": "BEAUTY",
            "뷰티 럭스": "BEAUTY",
            "뷰티 생활": "BEAUTY",
            "헬스": "HEALTH_SUPPLEMENT",
            "생활용품": "LIVING",
            "주방용품": "LIVING",
            "가구/인테리어": "LIVING",
            "가전제품": "ELECTRONICS",
            "패션/잡화": "FASHION",
            "스포츠/레저": "SPORTS_OUTDOOR",
        }
        if root in special:
            return special[root], f"kurly root: {root}"
        return "FOOD", "kurly food root default"

    if platform == "musinsa":
        mapping = {
            "Beauty": "BEAUTY",
            "Food/Health": "ETC_UNKNOWN",
            "Life": "LIVING",
            "Digital/Tech": "ELECTRONICS",
            "Pet": "PET",
            "Kids": "BABY",
            "Sportswear": "SPORTS_OUTDOOR",
            "Sports/Goods": "SPORTS_OUTDOOR",
            "Sportsshoes": "SPORTS_OUTDOOR",
            "Camping goods": "SPORTS_OUTDOOR",
        }
        if root in mapping:
            return mapping[root], f"musinsa root: {root}"
        if root in {
            "Clothing", "Shoes", "Bag", "Accessory", "Socks/Legwear",
            "Jewelry", "Underwear", "Eyewear", "Watch", "Headwear",
        }:
            return "FASHION", f"musinsa fashion root: {root}"

    if platform == "naver":
        return {
            "가구/인테리어": ("LIVING", "naver root"),
            "생활/건강": ("LIVING", "naver broad living root"),
            "출산/육아": ("BABY", "naver root"),
            "디지털/가전": ("ELECTRONICS", "naver root"),
        }.get(root, ("ETC_UNKNOWN", "unmapped naver root"))

    if platform == "ohouse":
        if root in {"가구", "패브릭", "조명"}:
            return "LIVING", f"ohouse root: {root}"

    if platform == "oliveyoung":
        if root in {"건강기능식품", "일반건강식품", "기능성/건강음료류"}:
            return "HEALTH_SUPPLEMENT", f"oliveyoung health root: {root}"
        if root in {
            "상온가공식품", "냉장/냉동가공식품", "과자류", "커피류", "유제품",
            "일반음료류", "차류", "사탕류", "소스/오일", "신선식품",
        }:
            return "FOOD", f"oliveyoung food root: {root}"
        if root in {
            "세제/청소", "주방용품", "기저귀/제지류", "홈 프래그런스",
            "리빙가전", "문구/팬시", "인테리어용품", "욕실용품",
        }:
            return "LIVING", f"oliveyoung living root: {root}"
        if root == "디지털/기기":
            return "ELECTRONICS", "oliveyoung digital root"
        if root == "반려동물용품":
            return "PET", "oliveyoung pet root"
        if root in {"패션잡화", "언더웨어/홈웨어", "패션의류"}:
            return "FASHION", f"oliveyoung fashion root: {root}"
        return "BEAUTY", "oliveyoung personal-care root default"

    if any(token in root for token in ("스킨", "헤어", "선케어", "클렌징", "메이크업", "바디케어", "구강/면도", "화장품", "향수")):
        return "BEAUTY", "beauty root keyword"
    if any(token in root for token in ("가전", "디지털", "컴퓨터", "휴대폰", "스마트기기", "모니터", "노트북", "태블릿", "음향")):
        return "ELECTRONICS", "electronics root keyword"
    if any(token in root for token in ("스포츠", "등산", "아웃도어", "캠핑", "자전거", "요가", "골프", "낚시", "헬스")):
        return "SPORTS_OUTDOOR", "sports/outdoor root keyword"
    if any(token in root for token in ("의류", "신발", "가방", "패션", "주얼리", "시계", "안경", "캐주얼")):
        return "FASHION", "fashion root keyword"
    if any(token in root for token in ("세제", "화장지", "물티슈", "주방용품", "욕실", "침구", "생활", "가구", "인테리어", "자동차용품")):
        return "LIVING", "living root keyword"
    if any(token in root for token in ("커피", "음료", "과자", "간식", "축산", "채소", "과일", "식품", "유제품", "곡물", "밀키트")):
        return "FOOD", "food root keyword"
    if "food" in lower:
        return "FOOD", "English food term"
    return "ETC_UNKNOWN", "no supported mapping rule"


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise CategoryAnalysisError(f"CSV header is missing: {path}")
        return list(reader.fieldnames), list(reader)


def identity(row: dict[str, str]) -> tuple[str | None, str | None, str | None]:
    return (
        canonical_identifier(row.get("platform")),
        canonical_identifier(row.get("product_id")),
        canonical_identifier(row.get("review_id")),
    )


def load_candidate_sets(v1_path: Path, annotation_path: Path) -> dict[str, CandidateSet]:
    _, v1 = read_csv(v1_path)
    _, annotation = read_csv(annotation_path)
    return {
        "DESCRIPTION_V1": CandidateSet("DESCRIPTION_V1", v1),
        "DESCRIPTION_V2": CandidateSet("DESCRIPTION_V2", annotation),
        "DESCRIPTION_V2_HIGH": CandidateSet(
            "DESCRIPTION_V2_HIGH", [row for row in annotation if row["v2_tier"] == "HIGH"]
        ),
        "HUMAN_SUSPICIOUS": CandidateSet(
            "HUMAN_SUSPICIOUS", [row for row in annotation if row["human_label"] == "SUSPICIOUS"]
        ),
        "HUMAN_NORMAL": CandidateSet(
            "HUMAN_NORMAL", [row for row in annotation if row["human_label"] == "NORMAL"]
        ),
    }


def file_signature(path: Path) -> tuple[int, int]:
    stat = path.stat()
    return stat.st_size, stat.st_mtime_ns


def pct(value: int, total: int) -> float:
    return value / total if total else 0.0


def sqrt_platform_targets(platform_counts: Counter, total: int) -> dict[str, int]:
    weights = {name: math.sqrt(count) for name, count in platform_counts.items()}
    denominator = sum(weights.values())
    raw = {name: total * weight / denominator for name, weight in weights.items()}
    result = {name: int(value) for name, value in raw.items()}
    remainder = total - sum(result.values())
    for name in sorted(raw, key=lambda item: raw[item] - result[item], reverse=True)[:remainder]:
        result[name] += 1
    return result


def scan(
    paths: dict[str, Path],
    candidate_sets: dict[str, CandidateSet],
    *,
    expected_total: int | None = EXPECTED_TOTAL,
) -> dict:
    signatures_before = {platform: file_signature(path) for platform, path in paths.items()}
    candidate_lookup: dict[tuple[str | None, str | None, str | None], list[tuple[str, str]]] = defaultdict(list)
    for set_name, candidate_set in candidate_sets.items():
        for row in candidate_set.rows:
            candidate_lookup[identity(row)].append((set_name, row["candidate_id"]))

    platform_counts = Counter()
    platform_raw_categories: dict[str, Counter] = defaultdict(Counter)
    raw_products: dict[tuple[str, str], set[tuple[str, str]]] = defaultdict(set)
    normalized_counts = Counter()
    normalized_products: dict[str, set[tuple[str, str]]] = defaultdict(set)
    platform_normalized: dict[str, Counter] = defaultdict(Counter)
    mapping_reasons = Counter()
    total = 0
    blank = 0

    required = {"platform", "product_id", "review_id", "product_category"}
    for expected_platform, path in paths.items():
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None or not required.issubset(reader.fieldnames):
                raise CategoryAnalysisError(f"{expected_platform}: required columns missing")
            for row in reader:
                total += 1
                platform = canonical_identifier(row.get("platform"))
                if platform != expected_platform:
                    raise CategoryAnalysisError(
                        f"{expected_platform}: observed platform {platform!r}"
                    )
                raw = row.get("product_category") or ""
                blank += is_blank(raw)
                normalized, reason = normalize_category(platform, raw)
                raw_key = raw if not is_blank(raw) else "<BLANK>"
                product_id = canonical_identifier(row.get("product_id"))
                platform_counts[platform] += 1
                platform_raw_categories[platform][raw_key] += 1
                normalized_counts[normalized] += 1
                platform_normalized[platform][normalized] += 1
                mapping_reasons[(normalized, reason)] += 1
                if product_id is not None:
                    raw_products[(platform, raw_key)].add((platform, product_id))
                    normalized_products[normalized].add((platform, product_id))

                row_identity = identity(row)
                for set_name, candidate_id in candidate_lookup.get(row_identity, ()):
                    candidate_set = candidate_sets[set_name]
                    if candidate_id in candidate_set.matched_ids:
                        raise CategoryAnalysisError(
                            f"Candidate identity matched multiple rows: {candidate_id}"
                        )
                    candidate_set.matched_ids.add(candidate_id)
                    candidate_set.raw_categories[(platform, raw_key)] += 1
                    candidate_set.normalized_categories[normalized] += 1
                    candidate_set.platforms[platform] += 1
                    if product_id is not None:
                        candidate_set.products.add((platform, product_id))

    if expected_total is not None and total != expected_total:
        raise CategoryAnalysisError(f"Review total is {total:,}; expected {expected_total:,}.")
    signatures_after = {platform: file_signature(path) for platform, path in paths.items()}
    if signatures_before != signatures_after:
        raise CategoryAnalysisError("A source CSV changed during the read-only scan.")

    raw_rows = []
    all_raw_counts = Counter()
    for platform in PLATFORMS:
        for raw, count in platform_raw_categories[platform].items():
            normalized, reason = normalize_category(platform, None if raw == "<BLANK>" else raw)
            all_raw_counts[raw] += count
            raw_rows.append(
                {
                    "platform": platform,
                    "raw_category": raw,
                    "review_count": count,
                    "unique_product_count": len(raw_products[(platform, raw)]),
                    "normalized_category_provisional": normalized,
                    "mapping_reason": reason,
                }
            )
    raw_rows.sort(key=lambda item: (-item["review_count"], item["platform"], item["raw_category"]))

    full_variants: dict[str, set[tuple[str, str]]] = defaultdict(set)
    leaf_groups: dict[str, list[dict]] = defaultdict(list)
    for row in raw_rows:
        if row["raw_category"] == "<BLANK>":
            continue
        full_variants[canonical_category_text(row["raw_category"])].add(
            (row["platform"], row["raw_category"])
        )
        leaf = re.split(r"\s*>\s*", row["raw_category"])[-1]
        leaf_groups[canonical_category_text(leaf)].append(row)

    variant_groups = [
        {"canonical": key, "variants": sorted([{"platform": p, "raw_category": r} for p, r in values], key=lambda x: (x["platform"], x["raw_category"]))}
        for key, values in full_variants.items() if len(values) > 1
    ]
    leaf_collisions = []
    for leaf, rows in leaf_groups.items():
        distinct = {(row["platform"], row["raw_category"]) for row in rows}
        if len(distinct) > 1:
            leaf_collisions.append(
                {
                    "canonical_leaf": leaf,
                    "raw_path_count": len(distinct),
                    "review_count": sum(row["review_count"] for row in rows),
                    "examples": [
                        {"platform": row["platform"], "raw_category": row["raw_category"]}
                        for row in sorted(rows, key=lambda item: -item["review_count"])[:5]
                    ],
                }
            )
    leaf_collisions.sort(key=lambda item: (-item["review_count"], item["canonical_leaf"]))

    candidate_results = {}
    for name, candidate_set in candidate_sets.items():
        manifest_ids = {row["candidate_id"] for row in candidate_set.rows}
        candidate_results[name] = {
            "manifest_count": len(candidate_set.rows),
            "matched_count": len(candidate_set.matched_ids),
            "unmatched_candidate_ids": sorted(manifest_ids - candidate_set.matched_ids),
            "platform_counts": dict(candidate_set.platforms),
            "normalized_category_counts": dict(candidate_set.normalized_categories),
            "raw_category_counts": [
                {"platform": key[0], "raw_category": key[1], "count": count}
                for key, count in candidate_set.raw_categories.most_common()
            ],
            "unique_product_count": len(candidate_set.products),
        }

    rare = {}
    for threshold in (1, 10, 100):
        selected = [row for row in raw_rows if row["raw_category"] != "<BLANK>" and row["review_count"] <= threshold]
        rare[str(threshold)] = {
            "platform_category_pairs": len(selected),
            "reviews": sum(row["review_count"] for row in selected),
        }

    return {
        "analysis_type": "read-only category distribution and review-pool strategy; no pool or labels created",
        "source_paths": {platform: portable_report_path(path, "<LOCAL_REVIEW_EXPORT>") for platform, path in paths.items()},
        "source_signatures_unchanged": True,
        "total_reviews": total,
        "platform_counts": dict(platform_counts),
        "product_category": {
            "blank_rows": blank,
            "blank_ratio": pct(blank, total),
            "raw_unique_global": len(all_raw_counts) - ("<BLANK>" in all_raw_counts),
            "platform_raw_unique": {
                platform: len([key for key in counts if key != "<BLANK>"])
                for platform, counts in platform_raw_categories.items()
            },
            "raw_rows": raw_rows,
            "rare_category_summary": rare,
            "canonical_variant_group_count": len(variant_groups),
            "canonical_variant_groups": variant_groups,
            "same_leaf_multiple_path_group_count": len(leaf_collisions),
            "same_leaf_multiple_path_top": leaf_collisions[:50],
        },
        "provisional_normalized_categories": {
            "warning": "Sampling design only. Keep raw category; do not treat as ground truth.",
            "review_counts": dict(normalized_counts),
            "unique_product_counts": {
                category: len(normalized_products[category]) for category in NORMALIZED_CATEGORIES
            },
            "platform_by_category": {
                platform: dict(counts) for platform, counts in platform_normalized.items()
            },
            "mapping_reason_counts": [
                {"normalized_category": key[0], "reason": key[1], "reviews": count}
                for key, count in mapping_reasons.most_common()
            ],
        },
        "description_candidate_sets": candidate_results,
        "sampling": {
            "sqrt_platform_targets": {
                str(size): sqrt_platform_targets(platform_counts, size)
                for size in (10_000, 20_000, 30_000)
            },
            "pool_scenarios": {
                "10000": {"signal_focused": 6000, "hard_negative": 2500, "random_normal_control": 1500},
                "20000": {"signal_focused": 11000, "hard_negative": 5500, "random_normal_control": 3500},
                "30000": {"signal_focused": 15000, "hard_negative": 9000, "random_normal_control": 6000},
            },
            "recommendation": "Start with a 10K gated pilot, then expand to 20K cumulative after yield and agreement review; do not jump directly to 30K.",
        },
    }


def load_inventory(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def table(headers: list[str], rows: list[list[object]]) -> list[str]:
    return [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
        *("| " + " | ".join(str(value) for value in row) + " |" for row in rows),
    ]


def render_markdown(result: dict, inventory: dict) -> str:
    total = result["total_reviews"]
    category = result["product_category"]
    normalized = result["provisional_normalized_categories"]
    candidates = result["description_candidate_sets"]
    inventory_platforms = inventory["platforms"]
    duplicate_extras = sum(
        item["normalized_content_duplicates"]["extra_rows"]
        for item in inventory_platforms.values()
    )
    short_rows = sum(item["under_20_chars"] for item in inventory_platforms.values())
    high = candidates["DESCRIPTION_V2_HIGH"]["manifest_count"]
    suspicious = candidates["HUMAN_SUSPICIOUS"]["manifest_count"]

    lines = [
        "# 1.15M Review Category Distribution and Human Review Pool Strategy", "",
        "> READ-ONLY analysis. 이 보고서는 최종 Human Review Pool을 생성하지 않고, 자동 human label·모델 추론·학습을 수행하지 않는다.", "",
        "## 1. 실제 전체 review 수와 분석 범위", "",
        f"- 전체: **{total:,}건** / 6개 플랫폼",
        "- 식별자는 문자열로 읽어 leading zero와 원래 표현을 보존했다.",
        "- 외부 raw CSV는 열기/스트리밍만 수행했으며 크기·mtime signature가 전후 동일하다.", "",
        *table(
            ["platform", "reviews", "share"],
            [[p, f"{count:,}", f"{pct(count, total):.2%}"] for p, count in result["platform_counts"].items()],
        ), "",
        "## 2. product_category coverage", "",
        f"- blank/null: **{category['blank_rows']:,}건 ({category['blank_ratio']:.2%})**",
        f"- nonblank raw category unique(global text): **{category['raw_unique_global']:,}개**",
        "- raw category는 삭제·치환하지 않고 모든 provisional normalized mapping과 함께 보존해야 한다.", "",
        *table(
            ["platform", "raw category 종류"],
            [[p, f"{count:,}"] for p, count in category["platform_raw_unique"].items()],
        ), "",
        "## 3. raw category 분포와 fragmentation", "",
        "### 상위 30 platform/raw category", "",
        *table(
            ["platform", "raw category", "reviews", "products", "provisional"],
            [[row["platform"], row["raw_category"].replace("|", "\\|"), f"{row['review_count']:,}", f"{row['unique_product_count']:,}", row["normalized_category_provisional"]] for row in category["raw_rows"][:30]],
        ), "",
        "### 하위 20 platform/raw category", "",
        *table(
            ["platform", "raw category", "reviews", "products", "provisional"],
            [[row["platform"], row["raw_category"].replace("|", "\\|"), f"{row['review_count']:,}", f"{row['unique_product_count']:,}", row["normalized_category_provisional"]] for row in sorted((item for item in category["raw_rows"] if item["raw_category"] != "<BLANK>"), key=lambda item: (item["review_count"], item["platform"], item["raw_category"]))[:20]],
        ), "",
        "### 희소 category", "",
        *table(
            ["최대 reviews/category", "platform-category pairs", "participating reviews"],
            [[limit, values["platform_category_pairs"], f"{values['reviews']:,}"] for limit, values in category["rare_category_summary"].items()],
        ), "",
        f"- NFKC/공백/구분자만 다른 canonical variant group: {category['canonical_variant_group_count']:,}개",
        f"- 동일 leaf명이 여러 hierarchy path에 존재하는 group: {category['same_leaf_multiple_path_group_count']:,}개",
        "- 따라서 raw 954개를 그대로 sampling stratum으로 쓰면 지나치게 세분화된다. 다만 leaf명이 같다는 이유만으로 자동 병합해서도 안 된다.", "",
        "## 4. platform × provisional normalized category", "",
        *table(
            ["platform", *NORMALIZED_CATEGORIES],
            [[p, *[f"{normalized['platform_by_category'].get(p, {}).get(c, 0):,}" for c in NORMALIZED_CATEGORIES]] for p in PLATFORMS],
        ), "",
        "관찰된 집중은 실제 데이터와 일치한다: oliveyoung은 BEAUTY 중심, musinsa는 FASHION/SPORTS 중심, kurly는 FOOD 중심, ohouse는 LIVING 중심이다. 단순 비례 sampling은 이 플랫폼-카테고리 결합을 그대로 증폭한다.", "",
        "## 5. 추천 normalized category 체계", "",
        "`BEAUTY`, `HEALTH_SUPPLEMENT`, `DIET`, `FOOD`, `FASHION`, `LIVING`, `ELECTRONICS`, `BABY`, `PET`, `SPORTS_OUTDOOR`, `ETC_UNKNOWN`",
        "",
        *table(
            ["normalized category", "reviews", "share", "unique products"],
            [[c, f"{normalized['review_counts'].get(c, 0):,}", f"{pct(normalized['review_counts'].get(c, 0), total):.2%}", f"{normalized['unique_product_counts'].get(c, 0):,}"] for c in NORMALIZED_CATEGORIES],
        ), "",
        "이 체계는 sampling용 상위 계층이다. `ETC_UNKNOWN`을 허용하고, raw category 및 mapping reason을 함께 저장해야 한다. 특히 musinsa `Food/Health`와 광범위한 root는 근거 없이 세분화하지 않는다.", "",
        "## 6. raw → normalized mapping 전략", "",
        "1. blank는 `ETC_UNKNOWN`으로 보존한다.",
        "2. baby/pet/diet/supplement처럼 명시적인 전체 path 용어를 우선한다.",
        "3. 플랫폼별 root taxonomy를 적용한다.",
        "4. 매핑 근거가 없는 값은 `ETC_UNKNOWN`으로 남긴다.",
        "5. mapping table은 `(platform, raw_category, normalized_category, mapping_reason, mapping_version)` 형태로 versioning한다.",
        "6. JSON의 `raw_rows`가 전체 platform/raw mapping manifest 역할을 한다.", "",
        "## 7. candidate source별 실제 탐색 가능성", "",
        *table(
            ["candidate source", "현재 가능성", "근거/필요 작업"],
            [
                ["PRODUCT_DESCRIPTION_REPLACEMENT", "즉시 재사용 가능", "기존 full-scan 574 → V2 387; HIGH 26 중 사람 SUSPICIOUS 24 (HIGH stratum 92.3%, 전체 precision 추정치는 아님)"],
                ["EXTREME_RESULT_CLAIM", "새 analyzer 필요", "기간+큰 수치/완전 변화 조합과 부정·인용 예외를 함께 설계"],
                ["IMMEDIATE_EFFECT_CLAIM", "새 analyzer 필요", "즉시/하루/먹자마자 등 시간 표현+효과 동사 조합; 단독 keyword 금지"],
                ["PROMOTIONAL_TEMPLATE", "새 analyzer 필요", "구조화된 장점/추천/총평과 cross-review phrase repetition을 결합"],
                ["LOW_INFORMATION_PRAISE", "탐색 쉬움, 단독 신호는 약함", f"20자 미만 {short_rows:,}건. 길이만으로 label 금지; 제품/플랫폼 cap 필수"],
                ["REPEATED_SHORT_TEMPLATE", "inventory 재사용 가능", f"normalized-content duplicate extra rows {duplicate_extras:,}건. 짧음+반복 결합"],
                ["NEAR_DUPLICATE_CLUSTER", "소규모 코드는 있으나 1.15M용 신규 구현 필요", "기존 TF-IDF pair 도구는 전체 1.15M 직접 적용에 부적합; blocking/MinHash형 단계 필요"],
                ["CURRENT_PTEXT_HIGH", "현재 단계 실행 금지", "scored manifest가 별도로 제공될 때만 candidate source로 ingest"],
                ["CURRENT_PTEXT_BOUNDARY", "현재 단계 실행 금지", "실제 score distribution 확인 후 band 결정; 0.4~0.6 하드코딩 금지"],
                ["HARD_NEGATIVE_CANDIDATE", "후보 source 산출 후 가능", "signal은 강하지만 개인 경험이 구체적인 리뷰를 별도 검토층으로 구성"],
                ["RANDOM_NORMAL_CONTROL", "즉시 가능", "signal 비적중 모집단에서 category/platform/product 제한 stratified random"],
            ],
        ), "",
        "## 8. 기존 repo에서 재사용 가능한 코드/module", "",
        "- `analyze_new_review_inventory.py`: streaming CSV, identifier policy, exact/normalized duplicate inventory",
        "- `analyze_ptext_description_candidates.py`: description signal 분석",
        "- `extract_new_description_candidates.py`: 1.15M streaming candidate manifest/identity dedup",
        "- `build_description_human_review_pool_v2.py`: V2 precision refinement와 normalized-content dedup",
        "- `detect_near_duplicates.py`: 소규모 TF-IDF near-duplicate 기준 참고용(1.15M 직접 재사용 금지)",
        "- `prepare_description_human_review_annotations.py`: annotation identity/integrity validator",
        "- model score/inference manifest를 만드는 runtime은 이 repo에 확인되지 않았다.", "",
        "## 9. 새로 필요한 analyzer/script", "",
        "1. `analyze_review_category_strategy.py` — 현재 보고서와 전체 mapping manifest 생성(구현됨)",
        "2. `extract_claim_candidates.py` — EXTREME/IMMEDIATE claim evidence만 기록, label 금지",
        "3. `extract_template_candidates.py` — promotional/low-information/repeated-short source",
        "4. `build_text_duplicate_clusters.py` — exact/near cluster와 대표 review 분리",
        "5. `merge_candidate_manifests.py` — multi-source provenance와 identity dedup",
        "6. `sample_human_review_pool.py` — quota/cap 기반 deterministic sampling; 최종 pool 생성은 승인 후 별도 단계",
        "7. `validate_human_review_pool.py` — source identity/content, strata, overlap, label blank 검증",
        "", "## 10. candidate source overlap 예상과 보존 구조", "",
        "- description ↔ promotional ↔ extreme/immediate는 높은 overlap이 예상된다.",
        "- low-information ↔ repeated-short ↔ near-duplicate도 높은 overlap이 예상된다.",
        "- 한 review를 source별로 복제하지 말고 `candidate_sources`를 multi-value provenance로 저장한다.",
        "- review table에는 identity/content/source evidence를, cluster table에는 `cluster_id`, member identity, representative 여부를 둔다.",
        "- exact identity duplicate는 한 review로 통합하되 membership metadata는 삭제하지 않는다.",
        "- normalized-content duplicate는 대표 1건을 기본 검토 대상으로 하고, cluster audit quota에서 추가 member를 선택한다.", "",
        "## 11. 10K / 20K / 30K 구성안", "",
        *table(
            ["pool", "signal-focused", "hard negative", "random normal", "용도"],
            [
                ["10K", "6,000", "2,500", "1,500", "첫 calibration gate"],
                ["20K", "11,000", "5,500", "3,500", "10K 결과가 안정적일 때 누적 확장"],
                ["30K", "15,000", "9,000", "6,000", "source yield/합의도 검증 후에만"],
            ],
        ), "",
        "공통: source 하나가 전체의 25%를 넘지 않게 soft cap을 두고, multi-source와 아직 적게 본 category/platform을 우선한다. 현재 description V2는 387건뿐이므로 임의 oversampling하지 않는다.", "",
        "## 12. 가장 추천하는 규모", "",
        "**10K gated pilot**을 먼저 권장한다. 현재 사람 precision 근거는 description HIGH 26건뿐이고 나머지 source는 아직 analyzer/yield calibration이 없다. 10K에서 source별 positive yield, reviewer agreement, category/platform coverage를 확인한 뒤 **20K cumulative**로 확장하는 것이 정보 효율적이다. 30K를 바로 만들면 약한 signal과 중복 cluster가 annotation 예산을 소모할 위험이 크다.", "",
        "### sqrt(platform size) 기준 10K soft target", "",
        *table(["platform", "target"], [[p, f"{v:,}"] for p, v in result["sampling"]["sqrt_platform_targets"]["10000"].items()]), "",
        "## 13. category/platform 편향 방지", "",
        "- platform과 normalized category의 joint stratum을 사용하되 raw category를 보조 metadata로 유지한다.",
        "- 기본 quota는 모집단 비례가 아니라 sqrt(size)로 완화한다.",
        "- platform max 30%, normalized category max 25%, candidate source max 25% soft cap을 둔다.",
        "- product는 기본 최대 2개 review, 동일 duplicate cluster는 기본 대표 1개로 제한한다.",
        "- 희소 stratum은 최소 수량을 보장하되 naver처럼 모집단이 작은 플랫폼은 과도한 소진을 막는다.",
        "- 각 quota 미달분은 인접 stratum으로 deterministic redistribution하고 사유를 manifest에 남긴다.", "",
        "## 14. Hard Negative 확보", "",
        "- signal evidence는 존재하지만 실제 구매·사용·착용·섭취·배송·체감이 구체적인 review를 우선한다.",
        "- description signal+personal experience, claim 표현+기간/개인차 한정, 구조화된 장문 정상 후기를 별도 source로 둔다.",
        "- reviewer에게 candidate source를 정답처럼 노출하지 않고, source는 provenance로만 보존한다.",
        "- SUSPICIOUS 확정 후의 반대 사례가 아니라 label 이전의 독립 sampling stratum이어야 한다.", "",
        "## 15. Random Normal 대조군", "",
        "- 모든 suspicious candidate source 비적중 모집단에서 추출한다.",
        "- platform×normalized category×length band로 stratify하고 product/cluster cap을 적용한다.",
        "- 10K 기준 1,500건(15%)부터 시작하고, source false-positive가 높으면 20K에서 17.5%로 확대한다.",
        "- random control에도 human label은 blank로 두며 NORMAL로 선입력하지 않는다.", "",
        "## 16. 다음 구현 단계", "",
        "1. 이 category mapping의 ETC_UNKNOWN/ambiguous root를 사람이 검토해 mapping v1을 고정한다.",
        "2. EXTREME/IMMEDIATE claim analyzer를 작은 stratified sample에서 precision calibration한다.",
        "3. promotional/repeated-short analyzer와 exact cluster manifest를 만든다.",
        "4. 1.15M용 near-duplicate blocking 설계를 별도 승인받고 cluster audit을 수행한다.",
        "5. model inference 없이 가능한 source manifest부터 생성하고 overlap/yield를 측정한다.",
        "6. P_text scored manifest가 외부에서 제공될 때 HIGH/BOUNDARY source를 합친다.",
        "7. multi-source merge manifest를 검증한 뒤 10K quota를 dry-run한다.",
        "8. category/platform/source/product/cluster coverage 보고서를 승인받은 후에만 최종 pool을 생성한다.",
        "9. future annotation에서는 `candidate_sources`와 human `pattern_type`을 분리한다. human pattern은 겹칠 수 있으므로 `primary_pattern_type`+`secondary_pattern_types` 또는 multi-value field를 검토하되 현재 schema는 수정하지 않는다.", "",
        "## Description candidate 편향 실측", "",
    ]
    for name in ("DESCRIPTION_V1", "DESCRIPTION_V2", "DESCRIPTION_V2_HIGH", "HUMAN_SUSPICIOUS", "HUMAN_NORMAL"):
        item = candidates[name]
        lines.extend([
            f"### {name}", "",
            f"- manifest/matched: {item['manifest_count']:,}/{item['matched_count']:,}",
            f"- platforms: `{item['platform_counts']}`",
            f"- provisional categories: `{item['normalized_category_counts']}`",
            f"- unique products: {item['unique_product_count']:,}", "",
        ])
    lines.extend([
        "V2 387건 중 oliveyoung은 342건(88.4%)이다. 현재 description candidate 결과를 미래 전체 pool의 category/platform 분포 기준으로 사용하면 안 된다.", "",
        "## Annotation vocabulary 설계 의견", "",
        "- 현재 schema는 변경하지 않는다.",
        "- future pool에서는 `candidate_sources`(machine/rule provenance)와 `human_pattern_type`(사람 판단)을 분리한다.",
        "- extreme, immediate, promotional은 동시에 성립할 수 있으므로 단일 pattern만 강제하면 정보 손실이 있다.",
        "- 권장안: 단일 `human_label` + `primary_pattern_type` + optional multi-value `secondary_pattern_types`; reviewer UI가 어렵다면 우선 primary만 받고 adjudication에서 secondary를 보강한다.",
    ])
    return "\n".join(lines) + "\n"


def write_reports(result: dict, inventory: dict, json_path: Path, markdown_path: Path) -> None:
    for path in (json_path, markdown_path):
        if path.exists():
            raise FileExistsError(f"Refusing to overwrite existing report: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(result, inventory), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read-only review category distribution and pool strategy analysis"
    )
    for platform, default in DEFAULT_INPUTS.items():
        parser.add_argument(f"--{platform}", type=Path, default=default)
    parser.add_argument("--description-v1", type=Path, default=DEFAULT_V1)
    parser.add_argument("--annotation", type=Path, default=DEFAULT_ANNOTATION)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--json-report", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-report", type=Path, default=DEFAULT_MARKDOWN)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = {platform: getattr(args, platform).expanduser().resolve() for platform in PLATFORMS}
    protected = set(paths.values()) | {
        args.description_v1.resolve(), args.annotation.resolve(), args.inventory.resolve()
    }
    outputs = {args.json_report.resolve(), args.markdown_report.resolve()}
    if protected & outputs or len(outputs) != 2:
        raise CategoryAnalysisError("Report destinations must be distinct from all inputs.")

    candidate_sets = load_candidate_sets(args.description_v1, args.annotation)
    result = scan(paths, candidate_sets)
    inventory = load_inventory(args.inventory)
    write_reports(result, inventory, args.json_report, args.markdown_report)
    print("READ-ONLY REVIEW CATEGORY STRATEGY - no pool or labels created")
    print(f"reviews={result['total_reviews']}")
    print(f"raw_categories={result['product_category']['raw_unique_global']}")
    print(f"blank_category_rows={result['product_category']['blank_rows']}")
    print(f"json_report={args.json_report}")
    print(f"markdown_report={args.markdown_report}")
    print("source_signatures_unchanged=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
