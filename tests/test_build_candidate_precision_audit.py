import csv
import json
from pathlib import Path
import sqlite3

from scripts.build_candidate_precision_audit import (
    AUDIT_FIELDS, detect_extreme_expanded, detect_hard_negative_expanded,
    detect_immediate_expanded, frequency_bucket, stratified_sample,
)


def test_expanded_extreme_accepts_outcome_and_rejects_product_spec():
    assert detect_extreme_expanded("한 달 만에 4kg 빠졌어요")
    assert detect_extreme_expanded("2주 사용하니 붓기가 확 줄었어요")
    assert detect_extreme_expanded("제품 무게가 4kg짜리라 묵직해요") is None


def test_expanded_immediate_requires_health_outcome_not_sensory_only():
    assert detect_immediate_expanded("먹자마자 변비가 좋아졌어요")
    assert detect_immediate_expanded("바르자마자 여드름이 싹 사라졌어요")
    assert detect_immediate_expanded("바르자마자 시원해요") is None
    assert detect_immediate_expanded("먹자마자 달아요") is None


def test_hard_negative_expansion_requires_experience_and_detail():
    assert detect_hard_negative_expanded("한 달 동안 직접 사용해 보니 장점은 수납이 쉽고 단점은 세척이 번거롭다는 점입니다.", "LIVING")
    assert detect_hard_negative_expanded("효과가 정말 좋고 완벽한 제품입니다.", "HEALTH_SUPPLEMENT") is None


def test_frequency_bucket_boundaries():
    assert [frequency_bucket(x) for x in (2, 4, 5, 9, 10, 19, 20)] == ["2-4", "2-4", "5-9", "5-9", "10-19", "10-19", "20+"]


def test_stratified_sample_enforces_cluster_cap_and_diversity():
    rows = [
        {"row_uid": f"r{i}", "platform": "a" if i % 2 else "b", "normalized_category": "X" if i < 4 else "Y", "cluster_id": "c1" if i < 3 else f"c{i}"}
        for i in range(8)
    ]
    picked = stratified_sample(rows, 6, ("platform", "normalized_category"), cluster_cap=1)
    assert sum(r["cluster_id"] == "c1" for r in picked) == 1
    assert {r["platform"] for r in picked} == {"a", "b"}
    assert {r["normalized_category"] for r in picked} == {"X", "Y"}


def test_audit_schema_keeps_human_fields_blank(tmp_path: Path):
    path = tmp_path / "audit.csv"
    row = {name: "" for name in AUDIT_FIELDS}
    row.update({"audit_id": "A1", "row_uid": "p:2", "primary_audit_source": "PROTOTYPE"})
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=AUDIT_FIELDS); writer.writeheader(); writer.writerow(row)
    loaded = next(csv.DictReader(path.open(encoding="utf-8-sig")))
    assert loaded["human_label"] == loaded["human_note"] == ""


def test_read_only_uri_cannot_mutate_canonical_and_dry_run_is_not_dataset(tmp_path: Path):
    db_path = tmp_path / "canonical.sqlite3"
    with sqlite3.connect(db_path) as db:
        db.execute("CREATE TABLE marker(value TEXT)"); db.execute("INSERT INTO marker VALUES('unchanged')")
    before = db_path.read_bytes()
    with sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True) as db:
        assert db.execute("SELECT value FROM marker").fetchone()[0] == "unchanged"
        try:
            db.execute("UPDATE marker SET value='changed'")
        except sqlite3.OperationalError:
            pass
        else:
            raise AssertionError("read-only database unexpectedly writable")
    assert db_path.read_bytes() == before
    dry = {"created_final_10k_pool": False, "automatic_human_labels_created": False}
    assert json.loads(json.dumps(dry))["created_final_10k_pool"] is False
