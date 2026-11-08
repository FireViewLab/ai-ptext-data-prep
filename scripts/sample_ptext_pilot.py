"""Build a deterministic, unlabeled 100-row P_text pilot safely.

The 150K CSV and its SUCCESS marker are immutable inputs.  This module is safe
to exercise with synthetic fixtures; running it against the real pool is a
separate, explicitly approved operation.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import sys
from typing import Iterable, Mapping, Sequence
from uuid import uuid4

from openpyxl import load_workbook

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from ptext_pilot_near_duplicates import policy_contract as near_duplicate_policy_contract
from ptext_pilot_leakage import (
    MANIFEST_FIELDS as EXCLUSION_FIELDS,
    joint_group_id,
    manifest_entry,
    validate_manifest_completeness,
    validate_manifest_rows,
)
from ptext_pilot_review import write_blind_review_bundle
from sample_large_ptext_pool import (
    PipelineError as LargePoolError,
    assert_git_ignored,
    normalize_content,
    stable_priority,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PRIVATE_OUTPUT_ROOT = PROJECT_ROOT / "private_outputs"
DEFAULT_POOL_DIR = PRIVATE_OUTPUT_ROOT / "ptext_pool_150k_cap64_seed20261102_20261103"
DEFAULT_POOL_CSV = DEFAULT_POOL_DIR / "ptext_unlabeled_pool.csv"
DEFAULT_SUCCESS = DEFAULT_POOL_DIR / "SUCCESS.json"
DEFAULT_V2 = PROJECT_ROOT / "outputs" / "ptext_training_dataset_v2.xlsx"
DEFAULT_SEED = 20261108
DEFAULT_POLICY_VERSION = "ptext-pilot-v1"
DEFAULT_GUIDELINE_VERSION = "ptext-labeling-guide-v0.2"
DEFAULT_TARGETS = {"CANDIDATE": 40, "CONTROL": 30, "DIVERSITY": 30}
GROUP_ORDER = ("CANDIDATE", "CONTROL", "DIVERSITY")
SOURCE_POOL_SEED = 20261102
SOURCE_POOL_POLICY_VERSION = "ptext-large-pool-v1"
SOURCE_POOL_ROWS = 150_000
SOURCE_POOL_TARGETS = {"CANDIDATE": 60_000, "CONTROL": 70_000, "DIVERSITY": 20_000}
SOURCE_PLATFORMS = frozenset({"elevenst", "kurly", "musinsa", "naver", "ohouse", "oliveyoung"})

POOL_FIELDS = (
    "pool_id", "row_uid", "sampling_group", "sampling_reason", "label_status",
    "platform", "source_row", "product_id", "review_id", "product_category_raw",
    "normalized_category", "content", "normalized_content_hash", "content_length",
    "duplicate_cluster_id", "candidate_sources", "original_candidate_member",
    "original_control_eligible", "seed", "policy_version",
)
MASTER_FIELDS = POOL_FIELDS + (
    "annotation_id", "length_band", "pilot_selection_reason", "pilot_seed",
    "pilot_policy_version",
)
RELATION_FIELDS = ("row_uid", "relation_type", "group_id", "validation_status")
ALLOWED_RELATION_TYPES = frozenset({"NEAR_DUPLICATE", "V2_LINEAGE"})
RELATION_STATUSES = frozenset({"VERIFIED", "PROPOSED", "UNREVIEWED", "REJECTED"})


class PilotError(RuntimeError):
    """Fail-closed error with a redacted stable code."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


HEX_64 = re.compile(r"^[0-9a-f]{64}$")


def _required_identifier(value: str, code: str) -> str:
    if not value or value != value.strip() or any(ord(character) < 32 for character in value):
        raise PilotError(code)
    return value


def _validate_count_map(value: object, expected: Mapping[str, int], code: str) -> None:
    if not isinstance(value, dict) or set(value) != set(expected):
        raise PilotError(code)
    if any(type(value[key]) is not int or value[key] != expected[key] for key in expected):
        raise PilotError(code)


def validate_pilot_policy(seed: int, policy_version: str) -> None:
    if type(seed) is not int or seed != DEFAULT_SEED:
        raise PilotError("PILOT_SEED_FIXED")
    if policy_version != DEFAULT_POLICY_VERSION:
        raise PilotError("PILOT_POLICY_VERSION_FIXED")


@dataclass(frozen=True)
class PilotRow:
    pool_id: str
    row_uid: str
    sampling_group: str
    sampling_reason: str
    label_status: str
    platform: str
    source_row: str
    product_id: str
    review_id: str
    product_category_raw: str
    normalized_category: str
    content: str
    normalized_content_hash: str
    content_length: int
    duplicate_cluster_id: str
    candidate_sources: str
    original_candidate_member: str
    original_control_eligible: str
    seed: str
    policy_version: str

    @classmethod
    def from_mapping(cls, row: Mapping[str, str]) -> "PilotRow":
        try:
            content_length = int(row["content_length"])
            values = {field: str(row[field]) for field in POOL_FIELDS}
        except (KeyError, TypeError, ValueError) as exc:
            raise PilotError("POOL_ROW_SCHEMA_INVALID") from exc
        values["content_length"] = content_length
        return cls(**values)

    def as_pool_mapping(self) -> dict[str, object]:
        return {field: getattr(self, field) for field in POOL_FIELDS}


@dataclass(frozen=True)
class V2Exclusions:
    normalized_hashes: frozenset[str] = frozenset()
    review_keys: frozenset[tuple[str, str]] = frozenset()
    product_keys: frozenset[tuple[str, str]] = frozenset()
    lineage_links: tuple["V2LineageLink", ...] = ()


@dataclass(frozen=True)
class V2LineageLink:
    platform: str
    product_id: str
    parent_review_id: str
    parent_source_excel_row: str
    group_id: str
    split: str
    synthetic_family_id: str


@dataclass(frozen=True)
class VerifiedRelations:
    groups_by_row: Mapping[str, tuple[tuple[str, str], ...]]
    pending_count: int = 0
    status_counts: Mapping[str, int] | None = None


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def length_band(length: int) -> str:
    if length < 0:
        raise PilotError("NEGATIVE_CONTENT_LENGTH")
    if length < 20:
        return "<20"
    if length < 50:
        return "20-49"
    if length < 100:
        return "50-99"
    if length < 200:
        return "100-199"
    return "200+"


def _content_hash(content: str) -> tuple[str, int]:
    normalized = normalize_content(content)
    if normalized is None:
        raise PilotError("POOL_CONTENT_INVALID")
    return sha256(normalized.encode("utf-8")).hexdigest(), len(normalized)


def verify_and_load_pool(pool_csv: Path, success_path: Path) -> tuple[list[PilotRow], dict]:
    if not pool_csv.is_file() or not success_path.is_file():
        raise PilotError("POOL_INPUT_NOT_FOUND")
    before = (pool_csv.stat().st_size, pool_csv.stat().st_mtime_ns)
    try:
        contract = json.loads(success_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise PilotError("POOL_SUCCESS_INVALID") from exc
    if not isinstance(contract, dict) or contract.get("status") != "SUCCESS":
        raise PilotError("POOL_NOT_SUCCESSFUL")
    if type(contract.get("seed")) is not int or contract["seed"] != SOURCE_POOL_SEED:
        raise PilotError("POOL_SEED_MISMATCH")
    if contract.get("policy_version") != SOURCE_POOL_POLICY_VERSION:
        raise PilotError("POOL_POLICY_VERSION_MISMATCH")
    _validate_count_map(contract.get("targets"), SOURCE_POOL_TARGETS, "POOL_TARGET_COUNTS_MISMATCH")
    _validate_count_map(contract.get("selected"), SOURCE_POOL_TARGETS, "POOL_SELECTED_COUNTS_MISMATCH")
    materialization = contract.get("materialization")
    if not isinstance(materialization, dict):
        raise PilotError("POOL_MATERIALIZATION_CONTRACT_INVALID")
    if type(materialization.get("rows")) is not int or materialization["rows"] != SOURCE_POOL_ROWS:
        raise PilotError("POOL_MARKER_ROW_COUNT_MISMATCH")
    _validate_count_map(materialization.get("groups"), SOURCE_POOL_TARGETS, "POOL_MATERIALIZED_GROUPS_MISMATCH")
    if materialization.get("all_label_status_unlabeled") is not True:
        raise PilotError("POOL_UNLABELED_FLAG_INVALID")
    if materialization.get("linkage_verified") is not True:
        raise PilotError("POOL_LINKAGE_FLAG_INVALID")
    expected_hash = materialization.get("csv_sha256")
    if not isinstance(expected_hash, str) or not HEX_64.fullmatch(expected_hash):
        raise PilotError("POOL_SHA256_CONTRACT_INVALID")
    if file_sha256(pool_csv) != expected_hash:
        raise PilotError("POOL_SHA256_MISMATCH")

    rows: list[PilotRow] = []
    group_counts = Counter()
    label_counts = Counter()
    row_uids: set[str] = set()
    pool_ids: set[str] = set()
    with pool_csv.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != POOL_FIELDS:
            raise PilotError("POOL_HEADER_INVALID")
        for raw in reader:
            row = PilotRow.from_mapping(raw)
            if row.sampling_group not in DEFAULT_TARGETS or row.label_status != "UNLABELED":
                raise PilotError("POOL_GROUP_OR_LABEL_INVALID")
            for field in ("pool_id", "row_uid", "product_id", "review_id", "normalized_category"):
                _required_identifier(getattr(row, field), f"POOL_{field.upper()}_INVALID")
            if row.platform not in SOURCE_PLATFORMS:
                raise PilotError("POOL_PLATFORM_INVALID")
            try:
                if int(row.source_row) < 1 or str(int(row.source_row)) != row.source_row:
                    raise ValueError
            except ValueError as exc:
                raise PilotError("POOL_SOURCE_ROW_INVALID") from exc
            if row.seed != str(SOURCE_POOL_SEED) or row.policy_version != SOURCE_POOL_POLICY_VERSION:
                raise PilotError("POOL_ROW_POLICY_MISMATCH")
            if not HEX_64.fullmatch(row.normalized_content_hash):
                raise PilotError("POOL_CONTENT_HASH_FORMAT_INVALID")
            if row.row_uid in row_uids or row.pool_id in pool_ids:
                raise PilotError("POOL_IDENTITY_DUPLICATE")
            row_uids.add(row.row_uid)
            pool_ids.add(row.pool_id)
            digest, size = _content_hash(row.content)
            if digest != row.normalized_content_hash or size != row.content_length:
                raise PilotError("POOL_CONTENT_LINKAGE_MISMATCH")
            rows.append(row)
            group_counts[row.sampling_group] += 1
            label_counts[row.label_status] += 1
    after = (pool_csv.stat().st_size, pool_csv.stat().st_mtime_ns)
    if before != after:
        raise PilotError("POOL_CHANGED_DURING_READ")
    if len(rows) != SOURCE_POOL_ROWS:
        raise PilotError("POOL_ROW_COUNT_MISMATCH")
    if dict(group_counts) != SOURCE_POOL_TARGETS:
        raise PilotError("POOL_CSV_GROUP_COUNTS_MISMATCH")
    if dict(label_counts) != {"UNLABELED": SOURCE_POOL_ROWS}:
        raise PilotError("POOL_CSV_LABEL_COUNTS_MISMATCH")
    return rows, contract


def load_v2_exclusions(path: Path | None) -> V2Exclusions:
    if path is None:
        return V2Exclusions()
    if not path.is_file():
        raise PilotError("V2_DATASET_NOT_FOUND")
    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        sheet = workbook.active
        iterator = sheet.iter_rows(values_only=True)
        header = tuple(str(value) if value is not None else "" for value in next(iterator, ()))
        required = {
            "platform", "product_id", "review_id", "content", "label_origin",
            "group_id", "split", "source_excel_row", "parent_review_id",
            "parent_source_excel_row", "synthetic_family_id",
        }
        if not required.issubset(header):
            raise PilotError("V2_HEADER_INVALID")
        indexes = {name: header.index(name) for name in required}
        records = []
        for values in iterator:
            record = {name: values[indexes[name]] for name in required}
            record = {name: "" if value is None else str(int(value) if isinstance(value, float) and value.is_integer() else value) for name, value in record.items()}
            records.append(record)

        hashes: set[str] = set()
        reviews: set[tuple[str, str]] = set()
        products: set[tuple[str, str]] = set()
        real_by_review: dict[tuple[str, str], dict[str, str]] = {}
        real_by_source: dict[tuple[str, str], dict[str, str]] = {}
        for record in records:
            if record["label_origin"] == "synthetic":
                continue
            for field in ("platform", "product_id", "review_id", "group_id", "split", "source_excel_row"):
                _required_identifier(record[field], "V2_REAL_IDENTITY_INVALID")
            if record["split"] not in {"train", "validation", "test"}:
                raise PilotError("V2_SPLIT_INVALID")
            normalized = normalize_content(record["content"])
            if normalized is None:
                raise PilotError("V2_REAL_CONTENT_INVALID")
            digest = sha256(normalized.encode("utf-8")).hexdigest()
            review_key = (record["platform"], record["review_id"])
            source_key = (record["platform"], record["source_excel_row"])
            if review_key in real_by_review or source_key in real_by_source:
                raise PilotError("V2_REAL_IDENTITY_DUPLICATE")
            hashes.add(digest)
            reviews.add(review_key)
            products.add((record["platform"], record["product_id"]))
            record["normalized_content_hash"] = digest
            real_by_review[review_key] = record
            real_by_source[source_key] = record

        lineage_links = []
        for record in records:
            if record["label_origin"] != "synthetic":
                continue
            for field in (
                "platform", "product_id", "group_id", "split", "parent_review_id",
                "parent_source_excel_row", "synthetic_family_id",
            ):
                _required_identifier(record[field], "V2_SYNTHETIC_LINEAGE_INVALID")
            parent_by_review = real_by_review.get((record["platform"], record["parent_review_id"]))
            parent_by_source = real_by_source.get((record["platform"], record["parent_source_excel_row"]))
            if parent_by_review is None or parent_by_source is None or parent_by_review is not parent_by_source:
                raise PilotError("V2_SYNTHETIC_PARENT_UNRESOLVED")
            if record["group_id"] != parent_by_review["group_id"] or record["split"] != parent_by_review["split"]:
                raise PilotError("V2_SYNTHETIC_GROUP_OR_SPLIT_MISMATCH")
            if record["product_id"] != parent_by_review["product_id"]:
                raise PilotError("V2_SYNTHETIC_PRODUCT_MISMATCH")
            lineage_links.append(
                V2LineageLink(
                    platform=record["platform"],
                    product_id=record["product_id"],
                    parent_review_id=record["parent_review_id"],
                    parent_source_excel_row=record["parent_source_excel_row"],
                    group_id=record["group_id"],
                    split=record["split"],
                    synthetic_family_id=record["synthetic_family_id"],
                )
            )
        return V2Exclusions(
            frozenset(hashes), frozenset(reviews), frozenset(products), tuple(lineage_links)
        )
    finally:
        workbook.close()


def load_verified_relations(path: Path | None) -> VerifiedRelations:
    if path is None:
        return VerifiedRelations({}, 0, {})
    grouped: dict[str, list[tuple[str, str]]] = defaultdict(list)
    pending = 0
    status_counts = Counter()
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != RELATION_FIELDS:
            raise PilotError("RELATION_HEADER_INVALID")
        for row in reader:
            if row["relation_type"] not in ALLOWED_RELATION_TYPES:
                raise PilotError("RELATION_TYPE_INVALID")
            status = row["validation_status"]
            if status not in RELATION_STATUSES:
                raise PilotError("RELATION_STATUS_INVALID")
            status_counts[status] += 1
            if status != "VERIFIED":
                pending += 1
                continue
            if not row["row_uid"] or not row["group_id"]:
                raise PilotError("VERIFIED_RELATION_INVALID")
            grouped[row["row_uid"]].append((row["relation_type"], row["group_id"]))
    return VerifiedRelations(
        {key: tuple(sorted(set(value))) for key, value in grouped.items()},
        pending,
        dict(sorted(status_counts.items())),
    )


def _candidate_sources(row: PilotRow) -> tuple[str, ...]:
    return tuple(sorted({value for value in row.candidate_sources.split("|") if value}))


class SelectionState:
    def __init__(self, relations: VerifiedRelations):
        self.relations = relations
        self.row_uids: set[str] = set()
        self.hashes: set[str] = set()
        self.review_keys: set[tuple[str, str]] = set()
        self.products: set[tuple[str, str]] = set()
        self.clusters: set[str] = set()
        self.relation_groups: set[tuple[str, str]] = set()

    def rejection_reason(self, row: PilotRow) -> str | None:
        if row.row_uid in self.row_uids:
            return "ROW_UID_CAP"
        if row.normalized_content_hash in self.hashes:
            return "NORMALIZED_HASH_CAP"
        if (row.platform, row.review_id) in self.review_keys:
            return "PLATFORM_REVIEW_CAP"
        if (row.platform, row.product_id) in self.products:
            return "PLATFORM_PRODUCT_CAP"
        if row.duplicate_cluster_id and row.duplicate_cluster_id in self.clusters:
            return "DUPLICATE_CLUSTER_CAP"
        for relation in self.relations.groups_by_row.get(row.row_uid, ()):
            if relation in self.relation_groups:
                return f"VERIFIED_{relation[0]}_CAP"
        return None

    def add(self, row: PilotRow) -> None:
        reason = self.rejection_reason(row)
        if reason:
            raise PilotError("SELECTION_STATE_CONFLICT")
        self.row_uids.add(row.row_uid)
        self.hashes.add(row.normalized_content_hash)
        self.review_keys.add((row.platform, row.review_id))
        self.products.add((row.platform, row.product_id))
        if row.duplicate_cluster_id:
            self.clusters.add(row.duplicate_cluster_id)
        self.relation_groups.update(self.relations.groups_by_row.get(row.row_uid, ()))


def _feature_order(seed: int, policy_version: str, group: str, feature: str, values: Iterable[str]) -> list[str]:
    return sorted(
        set(values),
        key=lambda value: sha256(f"{seed}\x1f{policy_version}\x1f{group}\x1f{feature}\x1f{value}".encode("utf-8")).hexdigest(),
    )


def _annotation_id(row: PilotRow, seed: int, policy_version: str) -> str:
    return sha256(f"{policy_version}\x1f{seed}\x1f{row.row_uid}".encode("utf-8")).hexdigest()[:24]


def select_pilot_rows(
    rows: Sequence[PilotRow],
    *,
    seed: int = DEFAULT_SEED,
    policy_version: str = DEFAULT_POLICY_VERSION,
    targets: Mapping[str, int] = DEFAULT_TARGETS,
    v2_exclusions: V2Exclusions = V2Exclusions(),
    relations: VerifiedRelations = VerifiedRelations({}),
) -> tuple[list[tuple[PilotRow, str]], dict]:
    validate_pilot_policy(seed, policy_version)
    if dict(targets) != DEFAULT_TARGETS:
        raise PilotError("PILOT_TARGETS_MUST_BE_40_30_30")
    state = SelectionState(relations)
    all_selected: list[tuple[PilotRow, str]] = []
    group_reports = {}
    globally_rejected = Counter()

    for group in GROUP_ORDER:
        group_rows = [row for row in rows if row.sampling_group == group]
        priorities = {
            row.row_uid: stable_priority(seed, policy_version, group, row.row_uid)
            for row in group_rows
        }
        group_rows.sort(key=lambda row: (priorities[row.row_uid], row.row_uid))
        eligible = []
        excluded_v2 = Counter()
        for row in group_rows:
            if row.normalized_content_hash in v2_exclusions.normalized_hashes:
                excluded_v2["V2_EXACT"] += 1
            elif (row.platform, row.review_id) in v2_exclusions.review_keys:
                excluded_v2["V2_REVIEW"] += 1
            elif (row.platform, row.product_id) in v2_exclusions.product_keys:
                excluded_v2["V2_PRODUCT"] += 1
            else:
                eligible.append(row)

        selected: list[tuple[PilotRow, str]] = []
        selected_ids: set[str] = set()
        feature_counts = {
            "platform": Counter(),
            "category": Counter(),
            "length_band": Counter(),
            "candidate_source": Counter(),
        }

        def choose(row: PilotRow, reason: str) -> bool:
            if row.row_uid in selected_ids or len(selected) >= targets[group]:
                return False
            rejection = state.rejection_reason(row)
            if rejection:
                globally_rejected[rejection] += 1
                return False
            state.add(row)
            selected_ids.add(row.row_uid)
            selected.append((row, reason))
            feature_counts["platform"][row.platform] += 1
            feature_counts["category"][row.normalized_category] += 1
            feature_counts["length_band"][length_band(row.content_length)] += 1
            for source in _candidate_sources(row):
                feature_counts["candidate_source"][source] += 1
            return True

        phases: list[tuple[str, callable]] = []
        if group == "CANDIDATE":
            phases.append(("CANDIDATE_SOURCE", lambda row: _candidate_sources(row)))
        phases.extend(
            [
                ("PLATFORM", lambda row: (row.platform,)),
                ("CATEGORY", lambda row: (row.normalized_category,)),
                ("LENGTH_BAND", lambda row: (length_band(row.content_length),)),
            ]
        )
        for feature_name, getter in phases:
            values = _feature_order(
                seed, policy_version, group, feature_name,
                (value for row in eligible for value in getter(row)),
            )
            for value in values:
                candidates = [row for row in eligible if row.row_uid not in selected_ids and value in getter(row)]
                for row in candidates:
                    if choose(row, f"SOFT_COVERAGE_{feature_name}"):
                        break
                if len(selected) >= targets[group]:
                    break
            if len(selected) >= targets[group]:
                break

        while len(selected) < targets[group]:
            candidates = [
                row for row in eligible
                if row.row_uid not in selected_ids and state.rejection_reason(row) is None
            ]
            if not candidates:
                raise PilotError("PILOT_QUOTA_UNSATISFIED")

            def balance_key(row: PilotRow) -> tuple:
                sources = _candidate_sources(row)
                source_count = min((feature_counts["candidate_source"][source] for source in sources), default=0)
                return (
                    feature_counts["platform"][row.platform],
                    feature_counts["category"][row.normalized_category],
                    feature_counts["length_band"][length_band(row.content_length)],
                    source_count if group == "CANDIDATE" else 0,
                    priorities[row.row_uid],
                    row.row_uid,
                )

            choose(min(candidates, key=balance_key), "DETERMINISTIC_BALANCED_FILL")

        all_selected.extend(selected)
        group_reports[group] = {
            "target": targets[group],
            "selected": len(selected),
            "v2_excluded": dict(sorted(excluded_v2.items())),
            "platform": dict(sorted(feature_counts["platform"].items())),
            "normalized_category": dict(sorted(feature_counts["category"].items())),
            "length_band": dict(sorted(feature_counts["length_band"].items())),
            "candidate_source": dict(sorted(feature_counts["candidate_source"].items())),
            "selection_reason": dict(sorted(Counter(reason for _, reason in selected).items())),
        }

    report = {
        "status": "READY",
        "seed": seed,
        "policy_version": policy_version,
        "targets": dict(targets),
        "selected": dict(Counter(row.sampling_group for row, _ in all_selected)),
        "total_selected": len(all_selected),
        "groups": group_reports,
        "hard_constraint_rejection_attempts": dict(sorted(globally_rejected.items())),
        "verified_relation_rows": len(relations.groups_by_row),
        "pending_relation_rows_not_applied": relations.pending_count,
        "relation_status_counts": dict(relations.status_counts or {}),
        "v2_synthetic_lineage_links": len(v2_exclusions.lineage_links),
        "near_duplicate_policy": near_duplicate_policy_contract(),
    }
    return all_selected, report


def build_exclusion_rows(
    selected: Sequence[tuple[PilotRow, str]],
    *,
    seed: int,
    policy_version: str,
    relations: VerifiedRelations,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row, _ in selected:
        annotation_id = _annotation_id(row, seed, policy_version)
        group = joint_group_id(annotation_id)
        entities = [
            ("ROW_UID", (row.row_uid,), "PILOT_SOURCE_REVIEW"),
            ("NORMALIZED_CONTENT_HASH", (row.normalized_content_hash,), "PILOT_EXACT_CONTENT"),
            ("PLATFORM_REVIEW", (row.platform, row.review_id), "PILOT_REVIEW_ID"),
            ("PLATFORM_PRODUCT", (row.platform, row.product_id), "PILOT_PRODUCT"),
        ]
        if row.duplicate_cluster_id:
            entities.append(("DUPLICATE_CLUSTER", (row.duplicate_cluster_id,), "PILOT_DUPLICATE_CLUSTER"))
        for relation_type, group_id in relations.groups_by_row.get(row.row_uid, ()):
            entities.append((relation_type, (group_id,), f"VERIFIED_{relation_type}"))
        for entity_type, parts, reason in entities:
            rows.append(
                manifest_entry(
                    pilot_version=policy_version,
                    sampling_seed=seed,
                    annotation_id=annotation_id,
                    entity_type=entity_type,
                    entity_parts=parts,
                    exclusion_reason=reason,
                    group_id=group,
                )
            )
    validate_manifest_rows(rows)
    return rows


def validate_selected_rows(
    selected: Sequence[tuple[PilotRow, str]],
    *,
    relations: VerifiedRelations = VerifiedRelations({}),
) -> None:
    if Counter(row.sampling_group for row, _ in selected) != Counter(DEFAULT_TARGETS):
        raise PilotError("SELECTED_GROUP_COUNTS_INVALID")
    checks = {
        "row": [row.row_uid for row, _ in selected],
        "hash": [row.normalized_content_hash for row, _ in selected],
        "review": [(row.platform, row.review_id) for row, _ in selected],
        "product": [(row.platform, row.product_id) for row, _ in selected],
        "cluster": [row.duplicate_cluster_id for row, _ in selected if row.duplicate_cluster_id],
    }
    if any(len(values) != len(set(values)) for values in checks.values()):
        raise PilotError("SELECTED_HARD_CONSTRAINT_VIOLATION")
    relation_values = [
        relation
        for row, _ in selected
        for relation in relations.groups_by_row.get(row.row_uid, ())
    ]
    if len(relation_values) != len(set(relation_values)):
        raise PilotError("SELECTED_VERIFIED_RELATION_VIOLATION")


def _write_new_csv(path: Path, fields: Sequence[str], rows: Iterable[Mapping[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def _write_new_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def run_pipeline(
    pool_csv: Path,
    success_path: Path,
    output_dir: Path,
    *,
    v2_path: Path | None = None,
    verified_relations_path: Path | None = None,
    seed: int = DEFAULT_SEED,
    policy_version: str = DEFAULT_POLICY_VERSION,
    guideline_version: str = DEFAULT_GUIDELINE_VERSION,
    enforce_private_output: bool = True,
    require_v2_exclusions: bool = True,
) -> dict:
    validate_pilot_policy(seed, policy_version)
    if output_dir.exists():
        raise PilotError("OUTPUT_ALREADY_EXISTS")
    if enforce_private_output:
        try:
            assert_git_ignored(output_dir)
        except LargePoolError as exc:
            raise PilotError(exc.code) from exc
    staging = output_dir.parent / f".{output_dir.name}.staging-{uuid4().hex}"
    source_before = (file_sha256(pool_csv), pool_csv.stat().st_size, pool_csv.stat().st_mtime_ns)
    try:
        rows, pool_contract = verify_and_load_pool(pool_csv, success_path)
        if require_v2_exclusions and v2_path is None:
            raise PilotError("V2_DATASET_REQUIRED")
        v2_exclusions = load_v2_exclusions(v2_path)
        relations = load_verified_relations(verified_relations_path)
        selected, report = select_pilot_rows(
            rows,
            seed=seed,
            policy_version=policy_version,
            v2_exclusions=v2_exclusions,
            relations=relations,
        )
        validate_selected_rows(selected, relations=relations)
        staging.mkdir(parents=True)

        master_rows = []
        for row, selection_reason in selected:
            value = row.as_pool_mapping()
            value.update(
                {
                    "annotation_id": _annotation_id(row, seed, policy_version),
                    "length_band": length_band(row.content_length),
                    "pilot_selection_reason": selection_reason,
                    "pilot_seed": seed,
                    "pilot_policy_version": policy_version,
                }
            )
            master_rows.append(value)
        _write_new_csv(staging / "pilot_master_manifest.csv", MASTER_FIELDS, master_rows)
        exclusion_rows = build_exclusion_rows(
            selected, seed=seed, policy_version=policy_version, relations=relations
        )
        validate_manifest_completeness(master_rows, exclusion_rows)
        _write_new_csv(staging / "leakage_exclusion_manifest.csv", EXCLUSION_FIELDS, exclusion_rows)
        _write_new_json(staging / "sampling_report.json", report)
        _write_new_json(staging / "near_duplicate_policy.json", near_duplicate_policy_contract())
        write_blind_review_bundle(
            staging / "blind_review",
            master_rows,
            seed=seed,
            guideline_version=guideline_version,
        )
        source_after = (file_sha256(pool_csv), pool_csv.stat().st_size, pool_csv.stat().st_mtime_ns)
        if source_after != source_before:
            raise PilotError("POOL_CHANGED_DURING_PIPELINE")
        success = {
            "status": "SUCCESS",
            "seed": seed,
            "policy_version": policy_version,
            "guideline_version": guideline_version,
            "selected": report["selected"],
            "pool_sha256": source_before[0],
            "pool_contract_sha256": pool_contract["materialization"]["csv_sha256"],
            "near_duplicate_exclusion": "VERIFIED_RELATIONS_ONLY",
            "automatic_labels_assigned": False,
        }
        _write_new_json(staging / "SUCCESS.json", success)
        staging.rename(output_dir)
        return success
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        raise


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the fixed P_text 100-row pilot")
    parser.add_argument("--pool-csv", type=Path, default=DEFAULT_POOL_CSV)
    parser.add_argument("--success", type=Path, default=DEFAULT_SUCCESS)
    parser.add_argument("--v2", type=Path, default=DEFAULT_V2)
    parser.add_argument("--verified-relations", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--policy-version", default=DEFAULT_POLICY_VERSION)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = run_pipeline(
            args.pool_csv,
            args.success,
            args.output,
            v2_path=args.v2,
            verified_relations_path=args.verified_relations,
            seed=args.seed,
            policy_version=args.policy_version,
        )
    except (PilotError, OSError, ValueError) as exc:
        code = exc.code if isinstance(exc, PilotError) else "PILOT_PIPELINE_FAILED"
        print(json.dumps({"status": "FAILED", "error_code": code}, sort_keys=True))
        return 2
    print(json.dumps({"status": "SUCCESS", "selected": result["selected"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

