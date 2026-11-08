import csv
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from openpyxl import Workbook
import pytest

from scripts import sample_ptext_pilot as pilot
from scripts import ptext_pilot_review as review


def synthetic_content(index: int, target_length: int) -> str:
    prefix = f"fixture-{index}-"
    return prefix + ("가" * max(1, target_length - len(prefix)))


def make_rows(*, reverse=False, candidate_count=60, same_candidate_product=False):
    counts = {"CANDIDATE": candidate_count, "CONTROL": 50, "DIVERSITY": 50}
    lengths = [12, 20, 49, 50, 99, 100, 199, 200, 240]
    sources = [
        "EXACT_DUPLICATE_CLUSTER",
        "REPEATED_SHORT_TEMPLATE",
        "HARD_NEGATIVE_CANDIDATE",
        "PRODUCT_DESCRIPTION_REPLACEMENT",
        "PROMOTIONAL_TEMPLATE",
        "LOW_INFORMATION_PRAISE",
    ]
    platforms = sorted(pilot.SOURCE_PLATFORMS)
    rows = []
    index = 0
    for group, count in counts.items():
        for offset in range(count):
            target_length = lengths[index % len(lengths)]
            if group == "CONTROL" and target_length < 20:
                target_length = 20
            content = synthetic_content(index, target_length)
            normalized = pilot.normalize_content(content)
            digest = sha256(normalized.encode("utf-8")).hexdigest()
            platform = platforms[offset % len(platforms)]
            product = "shared-product" if same_candidate_product and group == "CANDIDATE" else f"product-{index}"
            rows.append(
                {
                    "pool_id": f"pool-{index}",
                    "row_uid": f"row-{index}",
                    "sampling_group": group,
                    "sampling_reason": "SYNTHETIC_FIXTURE",
                    "label_status": "UNLABELED",
                    "platform": platform,
                    "source_row": str(index + 2),
                    "product_id": product,
                    "review_id": f"review-{index}",
                    "product_category_raw": f"raw-{offset % 9}",
                    "normalized_category": f"CATEGORY_{offset % 9}",
                    "content": content,
                    "normalized_content_hash": digest,
                    "content_length": str(len(normalized)),
                    "duplicate_cluster_id": f"cluster-{index}" if offset % 3 == 0 else "",
                    "candidate_sources": sources[offset % len(sources)] if group == "CANDIDATE" else "",
                    "original_candidate_member": "1" if group == "CANDIDATE" else "0",
                    "original_control_eligible": "1" if group == "CONTROL" else "0",
                    "seed": str(pilot.SOURCE_POOL_SEED),
                    "policy_version": pilot.SOURCE_POOL_POLICY_VERSION,
                }
            )
            index += 1
    if reverse:
        rows.reverse()
    return rows


def write_pool(tmp_path: Path, rows):
    tmp_path.mkdir(parents=True, exist_ok=True)
    pool = tmp_path / "pool.csv"
    with pool.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=pilot.POOL_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    marker = tmp_path / "SUCCESS.json"
    groups = dict(sorted(Counter(row["sampling_group"] for row in rows).items()))
    marker.write_text(json.dumps({
        "status": "SUCCESS",
        "seed": pilot.SOURCE_POOL_SEED,
        "policy_version": pilot.SOURCE_POOL_POLICY_VERSION,
        "targets": groups,
        "selected": groups,
        "materialization": {
            "rows": len(rows),
            "groups": groups,
            "csv_sha256": pilot.file_sha256(pool),
            "all_label_status_unlabeled": True,
            "linkage_verified": True,
        },
    }), encoding="utf-8")
    return pool, marker


def configure_fixture_contract(monkeypatch, rows, *, expected_groups=None):
    groups = expected_groups or dict(Counter(row["sampling_group"] for row in rows))
    monkeypatch.setattr(pilot, "SOURCE_POOL_ROWS", sum(groups.values()))
    monkeypatch.setattr(pilot, "SOURCE_POOL_TARGETS", groups)


def selected_ids(rows, seed=pilot.DEFAULT_SEED, **kwargs):
    parsed = [pilot.PilotRow.from_mapping(row) for row in rows]
    selected, report = pilot.select_pilot_rows(parsed, seed=seed, **kwargs)
    return [(row.row_uid, row.sampling_group) for row, _ in selected], report


def update_marker(marker: Path, mutation):
    value = json.loads(marker.read_text(encoding="utf-8"))
    mutation(value)
    marker.write_text(json.dumps(value), encoding="utf-8")


def test_valid_synthetic_pool_contract_is_accepted(tmp_path, monkeypatch):
    rows = make_rows()
    configure_fixture_contract(monkeypatch, rows)
    pool, marker = write_pool(tmp_path, rows)
    loaded, contract = pilot.verify_and_load_pool(pool, marker)
    assert len(loaded) == len(rows)
    assert contract["materialization"]["all_label_status_unlabeled"] is True


@pytest.mark.parametrize(
    ("mutation", "code"),
    [
        (lambda marker: marker.update(seed=1), "POOL_SEED_MISMATCH"),
        (lambda marker: marker.update(policy_version="other"), "POOL_POLICY_VERSION_MISMATCH"),
        (lambda marker: marker["selected"].update(CANDIDATE=1), "POOL_SELECTED_COUNTS_MISMATCH"),
        (lambda marker: marker["materialization"].update(all_label_status_unlabeled=False), "POOL_UNLABELED_FLAG_INVALID"),
        (lambda marker: marker["materialization"].update(linkage_verified=False), "POOL_LINKAGE_FLAG_INVALID"),
    ],
)
def test_invalid_marker_contract_is_rejected(tmp_path, monkeypatch, mutation, code):
    rows = make_rows()
    configure_fixture_contract(monkeypatch, rows)
    pool, marker = write_pool(tmp_path, rows)
    update_marker(marker, mutation)
    with pytest.raises(pilot.PilotError, match=code):
        pilot.verify_and_load_pool(pool, marker)


def test_actual_csv_group_count_mismatch_is_rejected(tmp_path, monkeypatch):
    expected_rows = make_rows()
    expected_groups = dict(Counter(row["sampling_group"] for row in expected_rows))
    changed_rows = [dict(row) for row in expected_rows]
    changed_rows[0]["sampling_group"] = "CONTROL"
    configure_fixture_contract(monkeypatch, changed_rows, expected_groups=expected_groups)
    pool, marker = write_pool(tmp_path, changed_rows)
    update_marker(marker, lambda value: (
        value.update(targets=expected_groups, selected=expected_groups),
        value["materialization"].update(groups=expected_groups),
    ))
    with pytest.raises(pilot.PilotError, match="POOL_CSV_GROUP_COUNTS_MISMATCH"):
        pilot.verify_and_load_pool(pool, marker)


def test_blank_required_identifier_is_rejected(tmp_path, monkeypatch):
    rows = make_rows()
    rows[0]["review_id"] = ""
    configure_fixture_contract(monkeypatch, rows)
    pool, marker = write_pool(tmp_path, rows)
    with pytest.raises(pilot.PilotError, match="POOL_REVIEW_ID_INVALID"):
        pilot.verify_and_load_pool(pool, marker)


def test_same_seed_is_reproducible_when_input_order_changes():
    first, report1 = selected_ids(make_rows())
    second, report2 = selected_ids(make_rows(reverse=True))
    assert first == second
    assert report1["selected"] == report2["selected"] == pilot.DEFAULT_TARGETS


def test_pilot_seed_and_policy_are_fixed():
    rows = [pilot.PilotRow.from_mapping(row) for row in make_rows()]
    with pytest.raises(pilot.PilotError, match="PILOT_SEED_FIXED"):
        pilot.select_pilot_rows(rows, seed=1)
    with pytest.raises(pilot.PilotError, match="PILOT_POLICY_VERSION_FIXED"):
        pilot.select_pilot_rows(rows, policy_version="other-policy")


def test_exact_targets_and_all_hard_caps_hold():
    rows = [pilot.PilotRow.from_mapping(row) for row in make_rows()]
    selected, report = pilot.select_pilot_rows(rows)
    pilot.validate_selected_rows(selected)
    assert report["selected"] == pilot.DEFAULT_TARGETS
    assert len(selected) == 100
    assert set(report["groups"]["CANDIDATE"]["platform"]) == pilot.SOURCE_PLATFORMS
    assert len(report["groups"]["CANDIDATE"]["candidate_source"]) == 6
    assert "<20" not in report["groups"]["CONTROL"]["length_band"]


@pytest.mark.parametrize(
    ("value", "expected"),
    [(19, "<20"), (20, "20-49"), (49, "20-49"), (50, "50-99"),
     (99, "50-99"), (100, "100-199"), (199, "100-199"), (200, "200+")],
)
def test_length_band_boundaries(value, expected):
    assert pilot.length_band(value) == expected


def test_impossible_quota_fails_without_relaxing_product_cap():
    rows = [pilot.PilotRow.from_mapping(row) for row in make_rows(same_candidate_product=True)]
    with pytest.raises(pilot.PilotError, match="PILOT_QUOTA_UNSATISFIED"):
        pilot.select_pilot_rows(rows)


def test_verified_relations_are_hard_caps_and_manifest_entities():
    raw = make_rows()
    candidate_ids = [row["row_uid"] for row in raw if row["sampling_group"] == "CANDIDATE"]
    relations = pilot.VerifiedRelations(
        {
            candidate_ids[0]: (("NEAR_DUPLICATE", "near-1"),),
            candidate_ids[1]: (("NEAR_DUPLICATE", "near-1"),),
        }
    )
    rows = [pilot.PilotRow.from_mapping(row) for row in raw]
    selected, _ = pilot.select_pilot_rows(rows, relations=relations)
    pilot.validate_selected_rows(selected, relations=relations)
    selected_ids_set = {row.row_uid for row, _ in selected}
    assert len(selected_ids_set & set(candidate_ids[:2])) <= 1
    manifest = pilot.build_exclusion_rows(
        selected, seed=pilot.DEFAULT_SEED, policy_version=pilot.DEFAULT_POLICY_VERSION, relations=relations
    )
    assert all(row["excluded_from"] == "TRAIN|VALIDATION|EVALUATION" for row in manifest)
    assert not any("row-" in row["entity_key_hash"] for row in manifest)


def test_only_verified_near_or_lineage_relations_are_applied(tmp_path):
    path = tmp_path / "relations.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=pilot.RELATION_FIELDS)
        writer.writeheader()
        writer.writerows(
            [
                {"row_uid": "row-1", "relation_type": "NEAR_DUPLICATE", "group_id": "near-1", "validation_status": "VERIFIED"},
                {"row_uid": "row-2", "relation_type": "V2_LINEAGE", "group_id": "lineage-1", "validation_status": "PROPOSED"},
                {"row_uid": "row-3", "relation_type": "NEAR_DUPLICATE", "group_id": "near-2", "validation_status": "UNREVIEWED"},
                {"row_uid": "row-4", "relation_type": "NEAR_DUPLICATE", "group_id": "near-3", "validation_status": "REJECTED"},
            ]
        )
    relations = pilot.load_verified_relations(path)
    assert relations.groups_by_row == {"row-1": (("NEAR_DUPLICATE", "near-1"),)}
    assert relations.pending_count == 3
    assert relations.status_counts == {"PROPOSED": 1, "REJECTED": 1, "UNREVIEWED": 1, "VERIFIED": 1}


def test_unknown_relation_status_is_rejected(tmp_path):
    path = tmp_path / "relations.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=pilot.RELATION_FIELDS)
        writer.writeheader()
        writer.writerow(
            {"row_uid": "row-1", "relation_type": "NEAR_DUPLICATE", "group_id": "near-1", "validation_status": "VERFIED"}
        )
    with pytest.raises(pilot.PilotError, match="RELATION_STATUS_INVALID"):
        pilot.load_verified_relations(path)


def test_v2_exact_review_product_and_synthetic_lineage_are_processed(tmp_path):
    raw = make_rows()
    target = raw[0]
    same_product = next(row for row in raw[1:] if row["platform"] == target["platform"])
    same_product["product_id"] = target["product_id"]
    workbook = Workbook()
    sheet = workbook.active
    sheet.append([
        "platform", "product_id", "review_id", "content", "label_origin", "group_id",
        "split", "source_excel_row", "parent_review_id", "parent_source_excel_row",
        "synthetic_family_id",
    ])
    sheet.append([
        target["platform"], target["product_id"], target["review_id"], target["content"],
        "human_candidate_review", "v2-group-1", "train", target["source_row"], "", "", "",
    ])
    sheet.append([
        target["platform"], target["product_id"], "synthetic-review", "synthetic fixture content",
        "synthetic", "v2-group-1", "train", "9000", target["review_id"], target["source_row"],
        "family-1",
    ])
    path = tmp_path / "v2.xlsx"
    workbook.save(path)
    exclusions = pilot.load_v2_exclusions(path)
    assert target["normalized_content_hash"] in exclusions.normalized_hashes
    assert (target["platform"], target["review_id"]) in exclusions.review_keys
    assert (target["platform"], target["product_id"]) in exclusions.product_keys
    assert exclusions.lineage_links == (
        pilot.V2LineageLink(
            platform=target["platform"], product_id=target["product_id"],
            parent_review_id=target["review_id"], parent_source_excel_row=target["source_row"],
            group_id="v2-group-1", split="train", synthetic_family_id="family-1",
        ),
    )
    selected, report = pilot.select_pilot_rows(
        [pilot.PilotRow.from_mapping(row) for row in raw], v2_exclusions=exclusions
    )
    selected_ids_set = {row.row_uid for row, _ in selected}
    assert target["row_uid"] not in selected_ids_set
    assert same_product["row_uid"] not in selected_ids_set
    assert sum(report["groups"][group]["v2_excluded"].get("V2_EXACT", 0) for group in pilot.GROUP_ORDER) >= 1
    assert sum(report["groups"][group]["v2_excluded"].get("V2_PRODUCT", 0) for group in pilot.GROUP_ORDER) >= 1
    assert report["v2_synthetic_lineage_links"] == 1


def test_pipeline_preserves_source_refuses_overwrite_and_builds_blind_files(tmp_path, monkeypatch):
    rows = make_rows()
    configure_fixture_contract(monkeypatch, rows)
    pool, marker = write_pool(tmp_path / "input", rows)
    before = (pilot.file_sha256(pool), pool.stat().st_mtime_ns)
    output = tmp_path / "private" / "pilot"
    result = pilot.run_pipeline(
        pool,
        marker,
        output,
        v2_path=None,
        enforce_private_output=False,
        require_v2_exclusions=False,
    )
    assert result["selected"] == pilot.DEFAULT_TARGETS
    assert before == (pilot.file_sha256(pool), pool.stat().st_mtime_ns)
    assert (output / "SUCCESS.json").is_file()
    assert (output / "leakage_exclusion_manifest.csv").is_file()

    with (output / "blind_review" / "reviewer_packets" / "reviewer_a.csv").open(
        "r", encoding="utf-8-sig", newline=""
    ) as handle:
        reviewer_a = list(csv.DictReader(handle))
        assert tuple(reviewer_a[0]) == ("annotation_id", "display_order", "content")
        assert not (set(reviewer_a[0]) & review.FORBIDDEN_PACKET_FIELDS)
    with (output / "blind_review" / "reviewer_packets" / "reviewer_b.csv").open(
        "r", encoding="utf-8-sig", newline=""
    ) as handle:
        reviewer_b = list(csv.DictReader(handle))
    assert [row["annotation_id"] for row in reviewer_a] != [row["annotation_id"] for row in reviewer_b]

    with pytest.raises(pilot.PilotError, match="OUTPUT_ALREADY_EXISTS"):
        pilot.run_pipeline(
            pool, marker, output, v2_path=None, enforce_private_output=False,
            require_v2_exclusions=False,
        )


def test_pipeline_rejects_seed_or_policy_override_before_output(tmp_path, monkeypatch):
    rows = make_rows()
    configure_fixture_contract(monkeypatch, rows)
    pool, marker = write_pool(tmp_path / "input", rows)
    for kwargs, code in [({"seed": 1}, "PILOT_SEED_FIXED"), ({"policy_version": "other"}, "PILOT_POLICY_VERSION_FIXED")]:
        output = tmp_path / code
        with pytest.raises(pilot.PilotError, match=code):
            pilot.run_pipeline(
                pool, marker, output, v2_path=None, enforce_private_output=False,
                require_v2_exclusions=False, **kwargs,
            )
        assert not output.exists()


@pytest.mark.parametrize(
    ("option", "value", "code"),
    [("--seed", "1", "PILOT_SEED_FIXED"), ("--policy-version", "other", "PILOT_POLICY_VERSION_FIXED")],
)
def test_cli_rejects_fixed_policy_override(tmp_path, capsys, option, value, code):
    output = tmp_path / "output"
    exit_code = pilot.main(["--output", str(output), option, value])
    assert exit_code == 2
    assert code in capsys.readouterr().out
    assert not output.exists()


def test_failure_does_not_publish_output(tmp_path, monkeypatch):
    rows = make_rows(candidate_count=39)
    configure_fixture_contract(monkeypatch, rows)
    pool, marker = write_pool(tmp_path / "input", rows)
    output = tmp_path / "pilot"
    with pytest.raises(pilot.PilotError, match="PILOT_QUOTA_UNSATISFIED"):
        pilot.run_pipeline(
            pool, marker, output, v2_path=None, enforce_private_output=False,
            require_v2_exclusions=False,
        )
    assert not output.exists()


def test_cli_error_redacts_review_content_and_identifiers(tmp_path, capsys, monkeypatch):
    rows = make_rows()
    secret_content = "DO_NOT_LOG_PRIVATE_REVIEW"
    rows[0]["content"] = secret_content
    configure_fixture_contract(monkeypatch, rows)
    pool, marker = write_pool(tmp_path / "input", rows)
    monkeypatch.setattr(pilot, "assert_git_ignored", lambda path: None)
    exit_code = pilot.main(
        ["--pool-csv", str(pool), "--success", str(marker), "--v2", str(tmp_path / "missing.xlsx"),
         "--output", str(tmp_path / "output")]
    )
    output = capsys.readouterr().out
    assert exit_code == 2
    assert secret_content not in output
    assert rows[0]["review_id"] not in output
    assert "error_code" in output

