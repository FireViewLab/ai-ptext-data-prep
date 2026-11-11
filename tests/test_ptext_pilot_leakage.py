import copy
import csv

import pytest

from scripts import ptext_pilot_leakage as leakage


def record(record_id, *, row_uid, content_hash, platform="alpha", review_id="r", product_id="p", cluster=""):
    return {
        "record_id": record_id,
        "annotation_id": f"annotation-{record_id}",
        "row_uid": row_uid,
        "normalized_content_hash": content_hash,
        "platform": platform,
        "review_id": review_id,
        "product_id": product_id,
        "duplicate_cluster_id": cluster,
    }


def manifest_for(source):
    annotation_id = source["annotation_id"]
    group_id = leakage.joint_group_id(annotation_id)
    entities = [
        ("ROW_UID", (source["row_uid"],), "PILOT_SOURCE_REVIEW"),
        ("NORMALIZED_CONTENT_HASH", (source["normalized_content_hash"],), "PILOT_EXACT_CONTENT"),
        ("PLATFORM_REVIEW", (source["platform"], source["review_id"]), "PILOT_REVIEW_ID"),
        ("PLATFORM_PRODUCT", (source["platform"], source["product_id"]), "PILOT_PRODUCT"),
    ]
    if source["duplicate_cluster_id"]:
        entities.append(("DUPLICATE_CLUSTER", (source["duplicate_cluster_id"],), "PILOT_DUPLICATE_CLUSTER"))
    return [
        leakage.manifest_entry(
            pilot_version="ptext-pilot-v1",
            sampling_seed=20261108,
            annotation_id=annotation_id,
            entity_type=entity_type,
            entity_parts=parts,
            exclusion_reason=reason,
            group_id=group_id,
        )
        for entity_type, parts, reason in entities
    ]


def test_entity_key_rule_is_deterministic_and_component_safe():
    first = leakage.entity_key_hash("PLATFORM_REVIEW", "alpha", "review-1")
    second = leakage.entity_key_hash("PLATFORM_REVIEW", "alpha", "review-1")
    ambiguous = leakage.entity_key_hash("PLATFORM_REVIEW", "alpha:review", "1")
    other_boundary = leakage.entity_key_hash("PLATFORM_REVIEW", "alpha", "review:1")
    assert first == second
    assert first != ambiguous
    assert ambiguous != other_boundary


def test_manifest_consumer_excludes_row_hash_review_product_and_cluster_matches():
    source = record("pilot", row_uid="row-1", content_hash="a" * 64, review_id="review-1", product_id="product-1", cluster="cluster-1")
    manifest = manifest_for(source)
    records = [
        record("row", row_uid="row-1", content_hash="b" * 64, review_id="other-1", product_id="other-1"),
        record("hash", row_uid="row-2", content_hash="a" * 64, review_id="other-2", product_id="other-2"),
        record("review", row_uid="row-3", content_hash="c" * 64, review_id="review-1", product_id="other-3"),
        record("product", row_uid="row-4", content_hash="d" * 64, review_id="other-4", product_id="product-1"),
        record("cluster", row_uid="row-5", content_hash="e" * 64, review_id="other-5", product_id="other-5", cluster="cluster-1"),
        record("kept", row_uid="row-6", content_hash="f" * 64, review_id="other-6", product_id="other-6"),
    ]
    kept, excluded = leakage.consume_exclusion_manifest(records, manifest)
    assert [row["record_id"] for row in kept] == ["kept"]
    assert {row["record_id"] for row in excluded} == {"row", "hash", "review", "product", "cluster"}
    leakage.validate_manifest_completeness([source], manifest)
    leakage.validate_exclusions_applied(records, kept, manifest)


def test_verified_lineage_entity_is_consumed_but_unverified_relations_are_not_manifested():
    source = record("pilot", row_uid="row-1", content_hash="a" * 64)
    group_id = leakage.joint_group_id(source["annotation_id"])
    manifest = manifest_for(source) + [
        leakage.manifest_entry(
            pilot_version="ptext-pilot-v1", sampling_seed=20261108,
            annotation_id=source["annotation_id"], entity_type="V2_LINEAGE",
            entity_parts=("v2-group-1",), exclusion_reason="VERIFIED_V2_LINEAGE",
            group_id=group_id,
        )
    ]
    related = record("related", row_uid="row-9", content_hash="9" * 64, review_id="r9", product_id="p9")
    related["verified_relations"] = (("V2_LINEAGE", "v2-group-1"),)
    kept, excluded = leakage.consume_exclusion_manifest([related], manifest)
    assert kept == []
    assert excluded == [related]


def test_missing_manifest_entity_and_leaked_split_record_fail():
    source = record("pilot", row_uid="row-1", content_hash="a" * 64, review_id="review-1", product_id="product-1")
    manifest = manifest_for(source)
    with pytest.raises(leakage.LeakageManifestError, match="MANIFEST_ENTITY_MISSING"):
        leakage.validate_manifest_completeness([source], manifest[:-1])
    with pytest.raises(leakage.LeakageManifestError, match="EXCLUDED_RECORD_PRESENT_IN_SPLIT"):
        leakage.validate_exclusions_applied([source], [source], manifest)


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("manifest_version", "wrong", "MANIFEST_VERSION_INVALID"),
        ("entity_type", "UNKNOWN", "UNKNOWN_ENTITY_TYPE"),
        ("entity_key_hash", "bad", "ENTITY_KEY_HASH_INVALID"),
        ("excluded_from", "EVALUATION", "EXCLUSION_SCOPE_INVALID"),
    ],
)
def test_malformed_manifest_is_rejected(field, value, code):
    source = record("pilot", row_uid="row-1", content_hash="a" * 64)
    manifest = manifest_for(source)
    broken = copy.deepcopy(manifest)
    broken[0][field] = value
    with pytest.raises(leakage.LeakageManifestError, match=code):
        leakage.validate_manifest_rows(broken)


def test_joint_leakage_group_cannot_cross_splits():
    leakage.validate_group_split_isolation([("group-1", "train"), ("group-1", "train"), ("group-2", "test")])
    with pytest.raises(leakage.LeakageManifestError, match="LEAKAGE_GROUP_CROSSES_SPLITS"):
        leakage.validate_group_split_isolation([("group-1", "train"), ("group-1", "test")])


def test_written_manifest_round_trips_into_consumer(tmp_path):
    source = record("pilot", row_uid="row-1", content_hash="a" * 64)
    manifest = manifest_for(source)
    path = tmp_path / "manifest.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=leakage.MANIFEST_FIELDS)
        writer.writeheader()
        writer.writerows(manifest)
    loaded = leakage.read_manifest_csv(path)
    assert loaded == manifest
    kept, excluded = leakage.consume_exclusion_manifest([source], loaded)
    assert kept == []
    assert excluded == [source]

