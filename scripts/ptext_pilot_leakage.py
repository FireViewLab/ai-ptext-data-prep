"""Shared leakage-manifest schema and synthetic split-consumer checks.

The manifest stores hashes of canonical entity keys, never raw review text or
source identifiers.  This module is intentionally independent from a concrete
train/evaluation splitter so the same contract can be reused later.
"""

from __future__ import annotations

from collections import defaultdict
import csv
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Iterable, Mapping, Sequence


MANIFEST_VERSION = "ptext-pilot-exclusion-v1"
EXCLUDED_FROM = "TRAIN|VALIDATION|EVALUATION"
ENTITY_TYPES = frozenset(
    {
        "ROW_UID",
        "NORMALIZED_CONTENT_HASH",
        "PLATFORM_REVIEW",
        "PLATFORM_PRODUCT",
        "DUPLICATE_CLUSTER",
        "NEAR_DUPLICATE",
        "V2_LINEAGE",
    }
)
MANIFEST_FIELDS = (
    "manifest_version",
    "pilot_version",
    "sampling_seed",
    "policy_version",
    "annotation_id",
    "entity_type",
    "entity_key_hash",
    "exclusion_reason",
    "joint_leakage_group_id",
    "excluded_from",
)
HEX_64 = re.compile(r"^[0-9a-f]{64}$")
HEX_24 = re.compile(r"^[0-9a-f]{24}$")


class LeakageManifestError(ValueError):
    """Stable, non-sensitive manifest validation error."""


def _required_text(value: object, code: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise LeakageManifestError(code)
    if any(ord(character) < 32 for character in value):
        raise LeakageManifestError(code)
    return value


def canonical_entity_value(entity_type: str, *parts: object) -> str:
    """Canonicalize identifiers without numeric coercion or text normalization."""

    if entity_type not in ENTITY_TYPES:
        raise LeakageManifestError("UNKNOWN_ENTITY_TYPE")
    expected_parts = 2 if entity_type in {"PLATFORM_REVIEW", "PLATFORM_PRODUCT"} else 1
    if len(parts) != expected_parts:
        raise LeakageManifestError("ENTITY_PART_COUNT_INVALID")
    values = [_required_text(part, "ENTITY_VALUE_INVALID") for part in parts]
    if entity_type == "NORMALIZED_CONTENT_HASH":
        digest = values[0].lower()
        if not HEX_64.fullmatch(digest):
            raise LeakageManifestError("CONTENT_HASH_INVALID")
        return digest
    if expected_parts == 2:
        return json.dumps(values, ensure_ascii=False, separators=(",", ":"))
    return values[0]


def entity_key_hash(entity_type: str, *parts: object) -> str:
    canonical = canonical_entity_value(entity_type, *parts)
    return sha256(f"{MANIFEST_VERSION}\x1f{entity_type}\x1f{canonical}".encode("utf-8")).hexdigest()


def joint_group_id(annotation_id: str) -> str:
    value = _required_text(annotation_id, "ANNOTATION_ID_INVALID")
    return sha256(f"{MANIFEST_VERSION}\x1fPILOT_GROUP\x1f{value}".encode("utf-8")).hexdigest()[:24]


def manifest_entry(
    *,
    pilot_version: str,
    sampling_seed: int,
    annotation_id: str,
    entity_type: str,
    entity_parts: Sequence[object],
    exclusion_reason: str,
    group_id: str,
) -> dict[str, object]:
    if type(sampling_seed) is not int:
        raise LeakageManifestError("SAMPLING_SEED_INVALID")
    return {
        "manifest_version": MANIFEST_VERSION,
        "pilot_version": _required_text(pilot_version, "PILOT_VERSION_INVALID"),
        "sampling_seed": sampling_seed,
        "policy_version": _required_text(pilot_version, "POLICY_VERSION_INVALID"),
        "annotation_id": _required_text(annotation_id, "ANNOTATION_ID_INVALID"),
        "entity_type": entity_type,
        "entity_key_hash": entity_key_hash(entity_type, *entity_parts),
        "exclusion_reason": _required_text(exclusion_reason, "EXCLUSION_REASON_INVALID"),
        "joint_leakage_group_id": _required_text(group_id, "GROUP_ID_INVALID"),
        "excluded_from": EXCLUDED_FROM,
    }


def validate_manifest_rows(rows: Sequence[Mapping[str, object]]) -> None:
    if not rows:
        raise LeakageManifestError("MANIFEST_EMPTY")
    seen: set[tuple[str, str, str]] = set()
    annotation_groups: dict[str, str] = {}
    for row in rows:
        if tuple(row.keys()) != MANIFEST_FIELDS:
            raise LeakageManifestError("MANIFEST_SCHEMA_INVALID")
        if row["manifest_version"] != MANIFEST_VERSION:
            raise LeakageManifestError("MANIFEST_VERSION_INVALID")
        if row["excluded_from"] != EXCLUDED_FROM:
            raise LeakageManifestError("EXCLUSION_SCOPE_INVALID")
        if row["entity_type"] not in ENTITY_TYPES:
            raise LeakageManifestError("UNKNOWN_ENTITY_TYPE")
        if type(row["sampling_seed"]) is not int:
            raise LeakageManifestError("SAMPLING_SEED_INVALID")
        if not isinstance(row["entity_key_hash"], str) or not HEX_64.fullmatch(row["entity_key_hash"]):
            raise LeakageManifestError("ENTITY_KEY_HASH_INVALID")
        if not isinstance(row["joint_leakage_group_id"], str) or not HEX_24.fullmatch(row["joint_leakage_group_id"]):
            raise LeakageManifestError("GROUP_ID_INVALID")
        for field in ("pilot_version", "policy_version", "annotation_id", "exclusion_reason"):
            _required_text(row[field], f"{field.upper()}_INVALID")
        if row["pilot_version"] != row["policy_version"]:
            raise LeakageManifestError("POLICY_VERSION_MISMATCH")
        annotation_id = str(row["annotation_id"])
        group_id = str(row["joint_leakage_group_id"])
        if annotation_id in annotation_groups and annotation_groups[annotation_id] != group_id:
            raise LeakageManifestError("ANNOTATION_GROUP_MISMATCH")
        annotation_groups[annotation_id] = group_id
        key = (annotation_id, str(row["entity_type"]), str(row["entity_key_hash"]))
        if key in seen:
            raise LeakageManifestError("DUPLICATE_MANIFEST_ENTITY")
        seen.add(key)


def read_manifest_csv(path: Path) -> list[dict[str, object]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != MANIFEST_FIELDS:
            raise LeakageManifestError("MANIFEST_SCHEMA_INVALID")
        rows: list[dict[str, object]] = []
        for raw in reader:
            row: dict[str, object] = dict(raw)
            try:
                row["sampling_seed"] = int(str(row["sampling_seed"]))
            except (TypeError, ValueError) as exc:
                raise LeakageManifestError("SAMPLING_SEED_INVALID") from exc
            rows.append(row)
    validate_manifest_rows(rows)
    return rows


def direct_entity_hashes(record: Mapping[str, object]) -> set[str]:
    required = ("row_uid", "platform", "review_id", "product_id", "normalized_content_hash")
    if any(field not in record for field in required):
        raise LeakageManifestError("RECORD_SCHEMA_INVALID")
    hashes = {
        entity_key_hash("ROW_UID", record["row_uid"]),
        entity_key_hash("NORMALIZED_CONTENT_HASH", record["normalized_content_hash"]),
        entity_key_hash("PLATFORM_REVIEW", record["platform"], record["review_id"]),
        entity_key_hash("PLATFORM_PRODUCT", record["platform"], record["product_id"]),
    }
    cluster = record.get("duplicate_cluster_id")
    if cluster:
        hashes.add(entity_key_hash("DUPLICATE_CLUSTER", cluster))
    relations = record.get("verified_relations", ())
    if not isinstance(relations, (list, tuple)):
        raise LeakageManifestError("VERIFIED_RELATIONS_INVALID")
    for relation in relations:
        if not isinstance(relation, (list, tuple)) or len(relation) != 2:
            raise LeakageManifestError("VERIFIED_RELATIONS_INVALID")
        relation_type, group_id = relation
        if relation_type not in {"NEAR_DUPLICATE", "V2_LINEAGE"}:
            raise LeakageManifestError("VERIFIED_RELATION_TYPE_INVALID")
        hashes.add(entity_key_hash(str(relation_type), group_id))
    return hashes


def consume_exclusion_manifest(
    records: Sequence[Mapping[str, object]],
    manifest_rows: Sequence[Mapping[str, object]],
) -> tuple[list[Mapping[str, object]], list[Mapping[str, object]]]:
    """Partition records using direct entity matches from a validated manifest."""

    validate_manifest_rows(manifest_rows)
    excluded_hashes = {str(row["entity_key_hash"]) for row in manifest_rows}
    kept, excluded = [], []
    for record in records:
        (excluded if direct_entity_hashes(record) & excluded_hashes else kept).append(record)
    return kept, excluded


def validate_manifest_completeness(
    pilot_records: Sequence[Mapping[str, object]],
    manifest_rows: Sequence[Mapping[str, object]],
) -> None:
    """Require every pilot row's direct exclusion entities to be present."""

    validate_manifest_rows(manifest_rows)
    by_annotation: dict[str, set[str]] = defaultdict(set)
    for row in manifest_rows:
        by_annotation[str(row["annotation_id"])].add(str(row["entity_key_hash"]))
    for record in pilot_records:
        annotation_id = _required_text(record.get("annotation_id"), "ANNOTATION_ID_INVALID")
        if not direct_entity_hashes(record).issubset(by_annotation.get(annotation_id, set())):
            raise LeakageManifestError("MANIFEST_ENTITY_MISSING")


def validate_exclusions_applied(
    source_records: Sequence[Mapping[str, object]],
    split_records: Sequence[Mapping[str, object]],
    manifest_rows: Sequence[Mapping[str, object]],
) -> None:
    """Fail if a source record matching the manifest remains in any split."""

    _, expected_excluded = consume_exclusion_manifest(source_records, manifest_rows)
    _, leaked = consume_exclusion_manifest(split_records, manifest_rows)
    if leaked:
        raise LeakageManifestError("EXCLUDED_RECORD_PRESENT_IN_SPLIT")
    if not expected_excluded:
        raise LeakageManifestError("MANIFEST_MATCHES_NO_SOURCE_RECORD")


def validate_group_split_isolation(assignments: Iterable[tuple[str, str]]) -> None:
    """Ensure one joint leakage group is assigned to only one split."""

    splits_by_group: dict[str, set[str]] = defaultdict(set)
    for group_id, split in assignments:
        group = _required_text(group_id, "GROUP_ID_INVALID")
        split_name = _required_text(split, "SPLIT_INVALID")
        splits_by_group[group].add(split_name)
    if any(len(splits) > 1 for splits in splits_by_group.values()):
        raise LeakageManifestError("LEAKAGE_GROUP_CROSSES_SPLITS")

