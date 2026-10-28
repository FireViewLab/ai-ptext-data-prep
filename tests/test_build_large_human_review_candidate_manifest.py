import csv
from hashlib import sha256
from pathlib import Path
import sqlite3

from scripts.build_large_human_review_candidate_manifest import (
    EXACT_DUPLICATE,
    EXTREME_RESULT,
    HARD_NEGATIVE,
    IMMEDIATE_EFFECT,
    LOW_INFORMATION,
    PRODUCT_DESCRIPTION,
    PROMOTIONAL_TEMPLATE,
    REPEATED_SHORT,
    build_manifest,
    detect_extreme_result,
    detect_immediate_effect,
    detect_low_information,
    detect_text_sources,
)


def test_extreme_result_requires_outcome_not_product_weight():
    assert detect_extreme_result("일주일 만에 4kg 빠졌어요")
    assert detect_extreme_result("며칠 만에 붓기가 완전히 사라졌어요")
    assert detect_extreme_result("4kg짜리 제품이라 묵직합니다") is None


def test_immediate_effect_excludes_ordinary_sensory_reaction():
    assert detect_immediate_effect("먹자마자 변비가 좋아졌어요")
    assert detect_immediate_effect("바르자마자 여드름이 싹 사라졌어요")
    assert detect_immediate_effect("바르자마자 시원해요") is None
    assert detect_immediate_effect("먹자마자 맛이 상큼하게 느껴져요") is None


def test_low_information_is_weak_source_not_a_label():
    evidence = detect_low_information("너무 좋아요!")
    assert evidence
    assert "human_label" not in evidence
    assert detect_low_information("배송이 빠르고 한 달 써보니 편해요") is None


def test_promotional_and_hard_negative_can_overlap_without_label():
    text = (
        "제품 특징: 병풀 성분을 함유한 젤 제형입니다.\n"
        "주요 성분: 세라마이드 2%를 포함합니다.\n"
        "사용 방법: 적당량을 덜어 도포하세요. 피부 진정에 도움을 줍니다.\n"
        "제가 직접 구매해서 한 달 동안 사용해 보니 발림성이 좋았어요. 추천드립니다."
    )
    sources = detect_text_sources(text)
    assert PROMOTIONAL_TEMPLATE in sources
    assert HARD_NEGATIVE in sources
    assert all("human_label" not in evidence for evidence in sources.values())


def write_raw(path: Path, platform: str, rows: list[dict[str, str]]) -> None:
    fields = ["platform", "product_id", "review_id", "content", "product_category"]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({"platform": platform, **row})


def write_description_files(v1: Path, v2: Path) -> None:
    v1_fields = [
        "candidate_id", "tier", "platform", "product_id", "review_id",
        "description_signal_count", "description_signals", "description_evidence",
    ]
    with v1.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=v1_fields)
        writer.writeheader()
        writer.writerow({
            "candidate_id": "NEW-DESC-000001", "tier": "HIGH", "platform": "shop",
            "product_id": "001", "review_id": "0001", "description_signal_count": "3",
            "description_signals": "ingredient_or_spec|product_description|benefit_claim",
            "description_evidence": "{}",
        })
    with v2.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["candidate_id", "v2_tier"])
        writer.writeheader()
        writer.writerow({"candidate_id": "NEW-DESC-000001", "v2_tier": "HIGH"})


def test_manifest_preserves_rows_identity_overlap_and_duplicate_counts(tmp_path: Path):
    raw = tmp_path / "reviews_shop.csv"
    repeated = "최고예요"
    rows = [
        {"product_id": "001", "review_id": "0001", "content": "병풀 성분 제품 설명", "product_category": "스킨케어"},
        {"product_id": "002", "review_id": "0002", "content": repeated, "product_category": "스킨케어"},
        {"product_id": "002", "review_id": "0003", "content": repeated, "product_category": "스킨케어"},
        {"product_id": "003", "review_id": "0004", "content": "일주일 만에 4kg 빠졌어요", "product_category": "다이어트"},
        {"product_id": "004", "review_id": "0005", "content": "평범한 사용 후기입니다", "product_category": "생활용품"},
    ]
    write_raw(raw, "shop", rows)
    before = sha256(raw.read_bytes()).hexdigest()
    v1, v2 = tmp_path / "v1.csv", tmp_path / "v2.csv"
    write_description_files(v1, v2)
    database = tmp_path / "manifest.sqlite3"

    summary = build_manifest({"shop": raw}, v1, v2, database, expected_total=5)

    assert sha256(raw.read_bytes()).hexdigest() == before
    assert summary["execution"]["full_scan_reviews"] == 5
    assert summary["source_metrics"][PRODUCT_DESCRIPTION]["review_count"] == 1
    assert summary["source_metrics"][EXTREME_RESULT]["review_count"] == 1
    assert summary["source_metrics"][LOW_INFORMATION]["review_count"] == 2
    assert summary["source_metrics"][REPEATED_SHORT]["review_count"] == 2
    assert summary["source_metrics"][EXACT_DUPLICATE]["review_count"] == 2
    assert summary["duplicate_clusters"]["cluster_count"] == 1

    with sqlite3.connect(database) as db:
        assert db.execute("SELECT COUNT(*) FROM review_index").fetchone()[0] == 5
        assert db.execute("SELECT product_id,review_id FROM review_index WHERE row_uid='shop:2'").fetchone() == ("001", "0001")
        sources = {row[0] for row in db.execute("SELECT candidate_source FROM source_evidence WHERE row_uid='shop:3'")}
        assert {LOW_INFORMATION, REPEATED_SHORT, EXACT_DUPLICATE} <= sources
        manifest = db.execute("SELECT candidate_sources FROM candidate_manifest WHERE row_uid='shop:3'").fetchone()[0]
        assert manifest.split("|") == sorted(sources)
        assert db.execute("SELECT COUNT(*) FROM duplicate_members").fetchone()[0] == 2
        assert db.execute("SELECT value FROM metadata WHERE key='human_labels_created'").fetchone()[0] == "false"
        assert db.execute("SELECT value FROM metadata WHERE key='final_10k_pool_created'").fetchone()[0] == "false"


def test_random_eligibility_is_only_a_flag_and_mapping_is_reused(tmp_path: Path):
    raw = tmp_path / "reviews_kurly.csv"
    write_raw(raw, "kurly", [{
        "product_id": "0007", "review_id": "0008",
        "content": "배송 상태와 맛을 자세히 적은 일반적인 후기입니다.",
        "product_category": "반찬 > 두부",
    }])
    v1, v2 = tmp_path / "v1.csv", tmp_path / "v2.csv"
    write_description_files(v1, v2)
    database = tmp_path / "manifest.sqlite3"
    summary = build_manifest({"kurly": raw}, v1, v2, database, expected_total=1)
    assert summary["random_control_eligible"] == 1
    with sqlite3.connect(database) as db:
        row = db.execute("SELECT normalized_category,product_id,review_id FROM review_index").fetchone()
        assert row == ("FOOD", "0007", "0008")
        assert db.execute("SELECT COUNT(*) FROM random_control_eligible").fetchone()[0] == 1
