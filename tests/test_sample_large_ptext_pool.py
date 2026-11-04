import csv
from collections import namedtuple
from hashlib import sha256
import json
import os
from pathlib import Path
import sqlite3

import pytest

from scripts import sample_large_ptext_pool as sampler


def digest(text):
    normalized = sampler.normalize_content(text)
    return sha256(normalized.encode("utf-8")).hexdigest(), len(normalized)


def make_fixture(tmp_path: Path, *, reverse=False, mismatch=False):
    raw_root = tmp_path / "raw"
    raw_root.mkdir(parents=True)
    database = tmp_path / "canonical.sqlite3"
    rows = []
    by_platform = {"alpha": [], "beta": []}
    for platform in by_platform:
        for offset in range(18):
            source_row = offset + 2
            number = offset + (0 if platform == "alpha" else 100)
            content = f"synthetic fixture sentence {platform} {number}"
            category = "CAT_A" if offset % 3 else "CAT_B"
            row = {
                "row_uid": f"{platform}:{source_row}",
                "platform": platform,
                "source_row": source_row,
                "product_id": f"product-{platform}-{offset}",
                "review_id": f"review-{platform}-{offset}",
                "content": content,
                "product_category": category,
                "normalized_category": category,
                "candidate": offset < 6,
                "control": 4 <= offset < 14,
                "source": "HARD_NEGATIVE_CANDIDATE" if offset in (4, 5) else "EXACT_DUPLICATE_CLUSTER",
                "cluster": f"cluster-{platform}-{offset}" if offset < 6 else None,
            }
            rows.append(row)
            raw_row = dict(row)
            if mismatch and platform == "alpha" and offset == 0:
                raw_row["content"] = "synthetic mismatching fixture"
            by_platform[platform].append(raw_row)

    with sqlite3.connect(database) as db:
        db.executescript(
            """
            CREATE TABLE review_index(
              row_uid TEXT PRIMARY KEY,platform TEXT,source_row INTEGER,product_id TEXT,
              review_id TEXT,product_category_raw TEXT,normalized_category TEXT,
              category_mapping_reason TEXT,normalized_content_hash TEXT,content_length INTEGER,
              valid_identity INTEGER,valid_content INTEGER
            );
            CREATE TABLE candidate_content(row_uid TEXT PRIMARY KEY,content TEXT);
            CREATE TABLE random_control_eligible(row_uid TEXT PRIMARY KEY);
            CREATE TABLE source_evidence(row_uid TEXT,candidate_source TEXT,evidence_json TEXT,
              PRIMARY KEY(row_uid,candidate_source));
            CREATE TABLE duplicate_members(cluster_id TEXT,row_uid TEXT,platform_count INTEGER,
              same_product_count INTEGER,PRIMARY KEY(cluster_id,row_uid));
            """
        )
        insertion = list(reversed(rows)) if reverse else rows
        for row in insertion:
            content_hash, length = digest(row["content"])
            db.execute(
                "INSERT INTO review_index VALUES(?,?,?,?,?,?,?,?,?,?,1,1)",
                (row["row_uid"], row["platform"], row["source_row"], row["product_id"],
                 row["review_id"], row["product_category"], row["normalized_category"],
                 "fixture", content_hash, length),
            )
            if row["candidate"]:
                db.execute("INSERT INTO candidate_content VALUES(?,?)", (row["row_uid"], row["content"]))
                db.execute("INSERT INTO source_evidence VALUES(?,?,?)", (row["row_uid"], row["source"], "{}"))
            if row["control"]:
                db.execute("INSERT INTO random_control_eligible VALUES(?)", (row["row_uid"],))
            if row["cluster"]:
                db.execute("INSERT INTO duplicate_members VALUES(?,?,1,1)", (row["cluster"], row["row_uid"]))

    raw_paths = {}
    fields = ["platform", "product_id", "review_id", "content", "product_category"]
    for platform, platform_rows in by_platform.items():
        path = raw_root / f"reviews_{platform}.csv"
        raw_paths[platform] = path
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for row in platform_rows:
                writer.writerow({name: row[name] for name in fields})
    signatures = {platform: sampler.file_signature(path) for platform, path in raw_paths.items()}
    with sqlite3.connect(database) as db:
        db.execute("CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL)")
        db.execute(
            "INSERT INTO metadata VALUES('summary_json',?)",
            (json.dumps({"execution": {"source_signatures_before": signatures}}),),
        )
    return database, raw_paths


def refresh_stored_signatures(database: Path, raw_paths: dict[str, Path]):
    signatures = {platform: sampler.file_signature(path) for platform, path in raw_paths.items()}
    value = json.dumps({"execution": {"source_signatures_before": signatures}})
    with sqlite3.connect(database) as db:
        db.execute("UPDATE metadata SET value=? WHERE key='summary_json'", (value,))


def rewrite_csv(path: Path, rows: list[dict]):
    fields = ["platform", "product_id", "review_id", "content", "product_category"]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def selected(staging: Path):
    with sqlite3.connect(staging) as db:
        return db.execute(
            "SELECT row_uid,sampling_group FROM selection ORDER BY sampling_group,row_uid"
        ).fetchall()


def run_selection(database, path, seed, targets=None, **caps):
    targets = targets or {"CANDIDATE": 6, "CONTROL": 7, "DIVERSITY": 4}
    report = sampler.select_pool(
        database, path, targets, seed, "fixture-policy",
        caps.get("hash_cap", 1), caps.get("cluster_cap", 1), caps.get("product_cap", 2),
    )
    return report, selected(path)


def test_same_seed_is_reproducible_and_sqlite_order_independent(tmp_path):
    db1, _ = make_fixture(tmp_path / "one")
    db2, _ = make_fixture(tmp_path / "two", reverse=True)
    report1, rows1 = run_selection(db1, tmp_path / "one.sqlite3", 41)
    report2, rows2 = run_selection(db2, tmp_path / "two.sqlite3", 41)
    assert report1["status"] == report2["status"] == "READY"
    assert report1["seed"] == 41
    assert report1["policy_version"] == "fixture-policy"
    assert rows1 == rows2


def test_different_seed_changes_sample(tmp_path):
    database, _ = make_fixture(tmp_path / "fixture")
    _, first = run_selection(database, tmp_path / "first.sqlite3", 1)
    _, second = run_selection(database, tmp_path / "second.sqlite3", 2)
    assert first != second


def test_groups_are_disjoint_and_candidate_control_overlap_is_blocked(tmp_path):
    database, _ = make_fixture(tmp_path / "fixture")
    report, rows = run_selection(database, tmp_path / "selection.sqlite3", 7)
    assert len(rows) == len({uid for uid, _ in rows})
    assert report["row_uid_overlap_count"] == 0
    assert report["control_candidate_overlap_count"] == 0
    assert report["import_counts"]["candidate_control_overlap"] == 4
    assert report["candidate_source_counts"]["HARD_NEGATIVE_CANDIDATE"] >= 1
    assert "candidate_multi_source_count" in report
    assert set(report["diversity_original_membership"]) == {"candidate_member", "control_eligible"}
    with sqlite3.connect(tmp_path / "selection.sqlite3") as db:
        assert db.execute(
            "SELECT COUNT(*) FROM selection WHERE sampling_group='CONTROL' AND original_candidate_member=1"
        ).fetchone()[0] == 0


def make_cap_fixture(tmp_path: Path, *, same_hash=False, same_cluster=False, same_product=False):
    database, raw_paths = make_fixture(tmp_path)
    with sqlite3.connect(database) as db:
        base = db.execute(
            "SELECT normalized_content_hash,content_length,product_id FROM review_index WHERE row_uid='alpha:2'"
        ).fetchone()
        if same_hash:
            db.execute(
                "UPDATE review_index SET normalized_content_hash=?,content_length=? WHERE row_uid='alpha:3'",
                base[:2],
            )
        if same_cluster:
            db.execute("DELETE FROM duplicate_members WHERE row_uid='alpha:3'")
            db.execute("UPDATE duplicate_members SET cluster_id='shared' WHERE row_uid='alpha:2'")
            db.execute("INSERT INTO duplicate_members VALUES('shared','alpha:3',2,1)")
        if same_product:
            db.execute("UPDATE review_index SET product_id=? WHERE row_uid='alpha:3'", (base[2],))
    return database, raw_paths


@pytest.mark.parametrize("kind", ["same_hash", "same_cluster", "same_product"])
def test_hash_cluster_and_product_caps_report_shortfall(tmp_path, kind):
    database, _ = make_cap_fixture(tmp_path / kind, **{kind: True})
    report, _ = run_selection(
        database, tmp_path / f"{kind}.sqlite3", 9,
        targets={"CANDIDATE": 12, "CONTROL": 0, "DIVERSITY": 0},
        hash_cap=1, cluster_cap=1, product_cap=1,
    )
    assert report["status"] == "INSUFFICIENT_CAPACITY"
    assert report["groups"]["CANDIDATE"]["shortfall"] >= 1
    expected = {"same_hash": "normalized_hash_cap", "same_cluster": "cluster_cap", "same_product": "product_cap"}[kind]
    assert report["groups"]["CANDIDATE"]["cap_rejection_attempts"][expected] >= 1
    assert report["groups"]["CANDIDATE"]["cap_rejections"] == report["groups"]["CANDIDATE"]["cap_rejection_attempts"]
    assert report["groups"]["CANDIDATE"]["cap_rejection_metric"].startswith("selection attempts")


def test_quota_shortage_is_deterministically_redistributed():
    capacities = {("rare", "A"): 1, ("large", "B"): 100}
    first, shortfall = sampler.allocate_quotas(capacities, 20)
    second, _ = sampler.allocate_quotas(dict(reversed(list(capacities.items()))), 20)
    assert shortfall == 0
    assert first == second
    assert first[("rare", "A")] == 1
    assert sum(first.values()) == 20


def test_insufficient_population_fails_closed_without_success_marker(tmp_path):
    database, raw_paths = make_fixture(tmp_path / "fixture")
    output = tmp_path / "private_outputs" / "too-large"
    result = sampler.run_pipeline(
        database, raw_paths, output,
        {"CANDIDATE": 99, "CONTROL": 99, "DIVERSITY": 99},
        3, "fixture-policy", enforce_git_ignore=False,
    )
    assert result["status"] == "INSUFFICIENT_CAPACITY"
    assert not output.exists()
    assert not (result["staging_dir"] / "SUCCESS.json").exists()
    assert (result["staging_dir"] / "FAILURE.json").exists()


def test_successful_fixture_run_is_unlabeled_and_preserves_inputs(tmp_path):
    database, raw_paths = make_fixture(tmp_path / "fixture")
    protected = tmp_path / "existing-report.json"
    protected.write_text("unchanged", encoding="utf-8")
    before = {path: sha256(path.read_bytes()).hexdigest() for path in [database, *raw_paths.values(), protected]}
    output = tmp_path / "private_outputs" / "success"
    result = sampler.run_pipeline(
        database, raw_paths, output,
        {"CANDIDATE": 6, "CONTROL": 7, "DIVERSITY": 4},
        11, "fixture-policy", enforce_git_ignore=False,
    )
    assert result["status"] == "SUCCESS"
    assert (output / "SUCCESS.json").is_file()
    assert not any(output.parent.glob(".success.staging-*"))
    with (output / "ptext_unlabeled_pool.csv").open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 17
    assert {row["label_status"] for row in rows} == {"UNLABELED"}
    assert len({row["row_uid"] for row in rows}) == 17
    after = {path: sha256(path.read_bytes()).hexdigest() for path in before}
    assert before == after


def test_linkage_mismatch_never_promotes_or_creates_success(tmp_path):
    database, raw_paths = make_fixture(tmp_path / "fixture", mismatch=True)
    output = tmp_path / "private_outputs" / "mismatch"
    with pytest.raises(sampler.PipelineError, match="CSV_SQLITE_LINKAGE_MISMATCH"):
        sampler.run_pipeline(
            database, raw_paths, output,
            {"CANDIDATE": 12, "CONTROL": 0, "DIVERSITY": 0},
            5, "fixture-policy", product_cap=2, enforce_git_ignore=False,
        )
    assert not output.exists()
    staging = list(output.parent.glob(".mismatch.staging-*"))
    assert len(staging) == 1
    assert not (staging[0] / "SUCCESS.json").exists()


def test_raw_size_mismatch_fails_before_staging(tmp_path):
    database, raw_paths = make_fixture(tmp_path / "fixture")
    with raw_paths["alpha"].open("ab") as handle:
        handle.write(b"x")
    output = tmp_path / "private_outputs" / "size-mismatch"
    with pytest.raises(sampler.PipelineError, match="RAW_SOURCE_SIZE_MISMATCH"):
        sampler.run_pipeline(
            database, raw_paths, output,
            {"CANDIDATE": 1, "CONTROL": 1, "DIVERSITY": 1}, 1,
            enforce_git_ignore=False,
        )
    assert not output.exists()
    assert not list(output.parent.glob(".size-mismatch.staging-*"))


def test_raw_mtime_mismatch_fails_before_staging(tmp_path):
    database, raw_paths = make_fixture(tmp_path / "fixture")
    path = raw_paths["alpha"]
    stat = path.stat()
    os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns + 10_000_000_000))
    output = tmp_path / "private_outputs" / "mtime-mismatch"
    with pytest.raises(sampler.PipelineError, match="RAW_SOURCE_MTIME_MISMATCH"):
        sampler.run_pipeline(
            database, raw_paths, output,
            {"CANDIDATE": 1, "CONTROL": 1, "DIVERSITY": 1}, 1,
            enforce_git_ignore=False,
        )
    assert not output.exists()


def test_missing_canonical_signature_metadata_fails_closed(tmp_path):
    database, raw_paths = make_fixture(tmp_path / "fixture")
    with sqlite3.connect(database) as db:
        db.execute("DELETE FROM metadata WHERE key='summary_json'")
    output = tmp_path / "private_outputs" / "missing-signatures"
    with pytest.raises(sampler.PipelineError, match="CANONICAL_SOURCE_SIGNATURES_MISSING"):
        sampler.run_pipeline(
            database, raw_paths, output,
            {"CANDIDATE": 1, "CONTROL": 1, "DIVERSITY": 1}, 1,
            enforce_git_ignore=False,
        )
    assert not output.exists()


def test_platform_row_count_mismatch_fails_even_with_refreshed_signature(tmp_path):
    database, raw_paths = make_fixture(tmp_path / "fixture")
    path = raw_paths["alpha"]
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    rows.append({
        "platform": "alpha", "product_id": "extra-product", "review_id": "extra-review",
        "content": "synthetic extra fixture", "product_category": "CAT_A",
    })
    rewrite_csv(path, rows)
    refresh_stored_signatures(database, raw_paths)
    output = tmp_path / "private_outputs" / "row-count"
    with pytest.raises(sampler.PipelineError, match="RAW_MANIFEST_ROW_COUNT_MISMATCH"):
        sampler.run_pipeline(
            database, raw_paths, output,
            {"CANDIDATE": 1, "CONTROL": 1, "DIVERSITY": 1}, 1,
            enforce_git_ignore=False,
        )
    assert not output.exists()


def test_insert_delete_shift_is_detected_by_selected_row_linkage(tmp_path):
    database, raw_paths = make_fixture(tmp_path / "fixture")
    path = raw_paths["alpha"]
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    rows.insert(0, {
        "platform": "alpha", "product_id": "inserted-product", "review_id": "inserted-review",
        "content": "synthetic inserted fixture", "product_category": "CAT_A",
    })
    rows.pop()
    rewrite_csv(path, rows)
    refresh_stored_signatures(database, raw_paths)
    output = tmp_path / "private_outputs" / "shifted"
    with pytest.raises(sampler.PipelineError, match="CSV_SQLITE_LINKAGE_MISMATCH"):
        sampler.run_pipeline(
            database, raw_paths, output,
            {"CANDIDATE": 12, "CONTROL": 0, "DIVERSITY": 0}, 3,
            enforce_git_ignore=False,
        )
    assert not output.exists()
    staging = list(output.parent.glob(".shifted.staging-*"))
    assert len(staging) == 1
    assert not (staging[0] / "SUCCESS.json").exists()


def test_insufficient_disk_space_stops_before_staging(tmp_path, monkeypatch):
    database, raw_paths = make_fixture(tmp_path / "fixture")
    Usage = namedtuple("Usage", "total used free")
    monkeypatch.setattr(sampler.shutil, "disk_usage", lambda _: Usage(100, 99, 1))
    output = tmp_path / "private_outputs" / "no-space"
    with pytest.raises(sampler.PipelineError, match="INSUFFICIENT_DISK_SPACE"):
        sampler.run_pipeline(
            database, raw_paths, output,
            {"CANDIDATE": 1, "CONTROL": 1, "DIVERSITY": 1}, 1,
            enforce_git_ignore=False,
        )
    assert not output.exists()
    assert not list(output.parent.glob(".no-space.staging-*"))


def test_sqlite_temp_storage_is_connection_local_memory(tmp_path):
    database, _ = make_fixture(tmp_path / "fixture")
    environment_before = dict(os.environ)
    with sampler.connect_read_only(database) as canonical:
        assert canonical.execute("PRAGMA temp_store").fetchone()[0] == 2
    staging = sqlite3.connect(":memory:")
    try:
        sampler.create_staging_schema(staging)
        assert staging.execute("PRAGMA temp_store").fetchone()[0] == 2
    finally:
        staging.close()
    assert dict(os.environ) == environment_before


def test_staging_promotion_failure_never_exposes_final_directory(tmp_path, monkeypatch):
    database, raw_paths = make_fixture(tmp_path / "fixture")
    output = tmp_path / "private_outputs" / "promotion-failure"
    monkeypatch.setattr(
        sampler,
        "promote_staging",
        lambda *_: (_ for _ in ()).throw(sampler.PipelineError("STAGING_PROMOTION_FAILED")),
    )
    with pytest.raises(sampler.PipelineError, match="STAGING_PROMOTION_FAILED"):
        sampler.run_pipeline(
            database, raw_paths, output,
            {"CANDIDATE": 2, "CONTROL": 2, "DIVERSITY": 2}, 1,
            enforce_git_ignore=False,
        )
    assert not output.exists()
    staging = list(output.parent.glob(".promotion-failure.staging-*"))
    assert len(staging) == 1
    assert (staging[0] / "SUCCESS.json").is_file()


def test_success_marker_write_failure_never_promotes(tmp_path, monkeypatch):
    database, raw_paths = make_fixture(tmp_path / "fixture")
    output = tmp_path / "private_outputs" / "marker-failure"
    original = sampler.safe_json_write

    def fail_marker(path, value):
        if path.name == "SUCCESS.json":
            raise sampler.PipelineError("SUCCESS_MARKER_WRITE_FAILED")
        return original(path, value)

    monkeypatch.setattr(sampler, "safe_json_write", fail_marker)
    with pytest.raises(sampler.PipelineError, match="SUCCESS_MARKER_WRITE_FAILED"):
        sampler.run_pipeline(
            database, raw_paths, output,
            {"CANDIDATE": 2, "CONTROL": 2, "DIVERSITY": 2}, 1,
            enforce_git_ignore=False,
        )
    assert not output.exists()
    staging = list(output.parent.glob(".marker-failure.staging-*"))
    assert len(staging) == 1
    assert not (staging[0] / "SUCCESS.json").exists()


def test_existing_output_path_is_never_overwritten(tmp_path):
    database, raw_paths = make_fixture(tmp_path / "fixture")
    output = tmp_path / "private_outputs" / "existing"
    output.mkdir(parents=True)
    marker = output / "keep.txt"
    marker.write_text("keep", encoding="utf-8")
    with pytest.raises(sampler.PipelineError, match="FINAL_OUTPUT_PATH_ALREADY_EXISTS"):
        sampler.run_pipeline(
            database, raw_paths, output,
            {"CANDIDATE": 1, "CONTROL": 1, "DIVERSITY": 1},
            1, enforce_git_ignore=False,
        )
    assert marker.read_text(encoding="utf-8") == "keep"


def test_console_error_is_redacted(monkeypatch, capsys):
    secret = "synthetic-private-identifier"
    monkeypatch.setattr(
        sampler,
        "parse_args",
        lambda argv=None: type("Args", (), {
            "output_name": "safe", "raw_root": Path("unused"), "database": Path(secret),
            "targets": {"CANDIDATE": 1, "CONTROL": 1, "DIVERSITY": 1},
            "seed": 1, "policy_version": "v", "normalized_hash_cap": 1,
            "duplicate_cluster_cap": 1, "product_cap": 1,
        })(),
    )
    monkeypatch.setattr(sampler, "run_pipeline", lambda *args, **kwargs: (_ for _ in ()).throw(sampler.PipelineError("SAFE_CODE")))
    assert sampler.main([]) == 1
    captured = capsys.readouterr()
    assert secret not in captured.out + captured.err
    assert "SAFE_CODE" in captured.err


def test_private_outputs_is_git_ignored():
    sampler.assert_git_ignored(sampler.PRIVATE_OUTPUT_ROOT / "synthetic-probe")
