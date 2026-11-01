import csv
import hashlib
from pathlib import Path

from scripts.analyze_review_category_strategy import (
    CandidateSet,
    canonical_category_text,
    normalize_category,
    scan,
    sqrt_platform_targets,
)


def write_reviews(path: Path, platform: str, rows: list[dict[str, str]]) -> None:
    fields = ["platform", "product_id", "review_id", "content", "product_category"]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({"platform": platform, **row})


def test_provisional_mapping_uses_explicit_and_platform_roots():
    assert normalize_category("oliveyoung", "스킨케어")[0] == "BEAUTY"
    assert normalize_category("kurly", "반찬 > 두부/어묵/맛살 > 두부")[0] == "FOOD"
    assert normalize_category("musinsa", "Clothing > 바지 > 슬랙스")[0] == "FASHION"
    assert normalize_category("naver", "가구/인테리어>침실가구>침대")[0] == "LIVING"
    assert normalize_category("elevenst", "건강식품>유산균>성인 유산균")[0] == "HEALTH_SUPPLEMENT"
    assert normalize_category("elevenst", "강아지용품>사료")[0] == "PET"
    assert normalize_category("elevenst", "")[0] == "ETC_UNKNOWN"


def test_category_canonicalization_only_normalizes_formatting():
    assert canonical_category_text(" 가구  >  침대 ") == "가구>침대"
    assert canonical_category_text("ＡＢＣ") == "abc"


def test_scan_preserves_sources_and_matches_candidates(tmp_path: Path):
    platform_rows = {
        "elevenst": [
            {"product_id": "001", "review_id": "01", "content": "a", "product_category": "건강식품>유산균"},
            {"product_id": "002", "review_id": "02", "content": "b", "product_category": ""},
        ],
        "kurly": [{"product_id": "003", "review_id": "03", "content": "c", "product_category": "반찬 > 두부"}],
        "musinsa": [{"product_id": "004", "review_id": "04", "content": "d", "product_category": "Clothing > 바지"}],
        "naver": [{"product_id": "005", "review_id": "05", "content": "e", "product_category": "가구/인테리어>침대"}],
        "ohouse": [{"product_id": "006", "review_id": "06", "content": "f", "product_category": "가구 > 책상"}],
        "oliveyoung": [{"product_id": "007", "review_id": "07", "content": "g", "product_category": "스킨케어"}],
    }
    paths = {}
    hashes = {}
    for platform, rows in platform_rows.items():
        path = tmp_path / f"reviews_{platform}.csv"
        write_reviews(path, platform, rows)
        paths[platform] = path
        hashes[platform] = hashlib.sha256(path.read_bytes()).hexdigest()

    candidate = {
        "candidate_id": "C-1", "platform": "elevenst", "product_id": "001", "review_id": "01"
    }
    sets = {"TEST": CandidateSet("TEST", [candidate])}
    result = scan(paths, sets, expected_total=None)

    assert result["total_reviews"] == 7
    assert result["product_category"]["blank_rows"] == 1
    assert result["description_candidate_sets"]["TEST"]["matched_count"] == 1
    assert result["description_candidate_sets"]["TEST"]["normalized_category_counts"] == {
        "HEALTH_SUPPLEMENT": 1
    }
    assert all(hashlib.sha256(path.read_bytes()).hexdigest() == hashes[p] for p, path in paths.items())


def test_sqrt_targets_sum_to_requested_pool_size():
    targets = sqrt_platform_targets({"a": 100, "b": 400, "c": 900}, 1000)
    assert sum(targets.values()) == 1000
    assert targets["a"] < targets["b"] < targets["c"]
