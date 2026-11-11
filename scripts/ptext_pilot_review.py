"""Blind-review packet and two-axis annotation support for the P_text pilot."""

from __future__ import annotations

import csv
from hashlib import sha256
from pathlib import Path
from typing import Iterable, Mapping, Sequence


TEXT_STATUSES = frozenset({"SUFFICIENT", "INSUFFICIENT", "INVALID"})
SIGNAL_DECISIONS = frozenset({"PRESENT", "ABSENT", "UNCERTAIN", "NOT_ASSESSED"})
SIGNAL_TYPES = frozenset(
    {
        "PRODUCT_DESCRIPTION_LIKE",
        "NO_USE_ASSERTIVE_CLAIM",
        "PROMOTIONAL_OR_SALES_LANGUAGE",
        "HIGH_CERTAINTY_EFFICACY_CLAIM",
        "WITHIN_REVIEW_REPETITION",
    }
)
FORBIDDEN_PACKET_FIELDS = frozenset(
    {
        "sampling_group",
        "sampling_reason",
        "candidate_sources",
        "model_prediction",
        "model_score",
        "rating",
        "image_count",
        "other_reviewer_label",
    }
)
PACKET_FIELDS = ("annotation_id", "display_order", "content")
ANNOTATION_FIELDS = (
    "annotation_id",
    "annotator_id",
    "text_status",
    "signal_decision",
    "signal_types",
    "rationale_codes",
    "rationale_note",
    "guideline_version",
    "annotation_round",
    "annotated_at",
)
ADJUDICATION_FIELDS = (
    "annotation_id",
    "adjudicator_id",
    "final_text_status",
    "final_signal_decision",
    "final_signal_types",
    "adjudication_note",
    "adjudicated_at",
)


class AnnotationValidationError(ValueError):
    """A validation error whose message never includes review text or identifiers."""


def parse_signal_types(value: str | Iterable[str]) -> tuple[str, ...]:
    if isinstance(value, str):
        items = [item.strip() for item in value.split("|") if item.strip()]
    else:
        items = [str(item).strip() for item in value if str(item).strip()]
    if len(items) != len(set(items)):
        raise AnnotationValidationError("DUPLICATE_SIGNAL_TYPE")
    unknown = set(items) - SIGNAL_TYPES
    if unknown:
        raise AnnotationValidationError("UNKNOWN_SIGNAL_TYPE")
    return tuple(sorted(items))


def validate_label_combination(
    text_status: str,
    signal_decision: str,
    signal_types: str | Iterable[str],
) -> tuple[str, ...]:
    if text_status not in TEXT_STATUSES:
        raise AnnotationValidationError("UNKNOWN_TEXT_STATUS")
    if signal_decision not in SIGNAL_DECISIONS:
        raise AnnotationValidationError("UNKNOWN_SIGNAL_DECISION")
    types = parse_signal_types(signal_types)
    if text_status == "SUFFICIENT":
        if signal_decision not in {"PRESENT", "ABSENT", "UNCERTAIN"}:
            raise AnnotationValidationError("INVALID_STATUS_DECISION_COMBINATION")
        if signal_decision == "PRESENT" and not types:
            raise AnnotationValidationError("PRESENT_REQUIRES_SIGNAL_TYPE")
        if signal_decision == "ABSENT" and types:
            raise AnnotationValidationError("ABSENT_FORBIDS_SIGNAL_TYPE")
    else:
        if signal_decision != "NOT_ASSESSED" or types:
            raise AnnotationValidationError("UNASSESSED_STATUS_REQUIRES_EMPTY_SIGNALS")
    return types


def validate_annotation_row(row: Mapping[str, str], *, allow_blank: bool = False) -> None:
    if tuple(row.keys()) != ANNOTATION_FIELDS:
        raise AnnotationValidationError("ANNOTATION_SCHEMA_MISMATCH")
    if not row["annotation_id"] or not row["annotator_id"]:
        raise AnnotationValidationError("ANNOTATION_IDENTITY_MISSING")
    label_fields = (row["text_status"], row["signal_decision"], row["signal_types"])
    if allow_blank and not any(label_fields):
        return
    if not all((row["text_status"], row["signal_decision"])):
        raise AnnotationValidationError("PARTIAL_LABEL")
    validate_label_combination(*label_fields)


def validate_adjudication_row(row: Mapping[str, str], *, allow_blank: bool = False) -> None:
    if tuple(row.keys()) != ADJUDICATION_FIELDS:
        raise AnnotationValidationError("ADJUDICATION_SCHEMA_MISMATCH")
    if not row["annotation_id"]:
        raise AnnotationValidationError("ADJUDICATION_IDENTITY_MISSING")
    label_fields = (
        row["final_text_status"],
        row["final_signal_decision"],
        row["final_signal_types"],
    )
    if allow_blank and not any(label_fields):
        return
    if not row["adjudicator_id"]:
        raise AnnotationValidationError("ADJUDICATOR_ID_MISSING")
    if not all((row["final_text_status"], row["final_signal_decision"])):
        raise AnnotationValidationError("PARTIAL_FINAL_LABEL")
    validate_label_combination(*label_fields)


def _write_new_csv(path: Path, fields: Sequence[str], rows: Iterable[Mapping[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def _reviewer_priority(seed: int, reviewer_id: str, annotation_id: str) -> str:
    payload = f"{seed}\x1f{reviewer_id}\x1f{annotation_id}".encode("utf-8")
    return sha256(payload).hexdigest()


def build_reviewer_rows(
    master_rows: Sequence[Mapping[str, str]],
    *,
    reviewer_id: str,
    seed: int,
    guideline_version: str,
) -> tuple[list[dict[str, object]], list[dict[str, str]]]:
    ordered = sorted(
        master_rows,
        key=lambda row: (_reviewer_priority(seed, reviewer_id, row["annotation_id"]), row["annotation_id"]),
    )
    packet = [
        {
            "annotation_id": row["annotation_id"],
            "display_order": index,
            "content": row["content"],
        }
        for index, row in enumerate(ordered, start=1)
    ]
    annotations = [
        {
            "annotation_id": row["annotation_id"],
            "annotator_id": reviewer_id,
            "text_status": "",
            "signal_decision": "",
            "signal_types": "",
            "rationale_codes": "",
            "rationale_note": "",
            "guideline_version": guideline_version,
            "annotation_round": "pilot_round_1",
            "annotated_at": "",
        }
        for row in ordered
    ]
    return packet, annotations


def validate_packet_schema(fields: Iterable[str]) -> None:
    values = tuple(fields)
    if values != PACKET_FIELDS:
        raise AnnotationValidationError("REVIEW_PACKET_SCHEMA_MISMATCH")
    if set(values) & FORBIDDEN_PACKET_FIELDS:
        raise AnnotationValidationError("REVIEW_PACKET_FORBIDDEN_FIELD")


def write_blind_review_bundle(
    root: Path,
    master_rows: Sequence[Mapping[str, str]],
    *,
    seed: int,
    guideline_version: str,
    reviewer_ids: Sequence[str] = ("reviewer_a", "reviewer_b"),
) -> dict[str, list[str]]:
    if root.exists():
        raise FileExistsError("REVIEW_BUNDLE_ALREADY_EXISTS")
    if len(reviewer_ids) != 2 or len(set(reviewer_ids)) != 2:
        raise AnnotationValidationError("TWO_DISTINCT_REVIEWERS_REQUIRED")
    annotation_ids = [row["annotation_id"] for row in master_rows]
    if len(annotation_ids) != len(set(annotation_ids)):
        raise AnnotationValidationError("DUPLICATE_ANNOTATION_ID")

    written: dict[str, list[str]] = {}
    for reviewer_id in reviewer_ids:
        packet, annotations = build_reviewer_rows(
            master_rows,
            reviewer_id=reviewer_id,
            seed=seed,
            guideline_version=guideline_version,
        )
        validate_packet_schema(packet[0].keys() if packet else PACKET_FIELDS)
        for row in annotations:
            validate_annotation_row(row, allow_blank=True)
        _write_new_csv(root / "reviewer_packets" / f"{reviewer_id}.csv", PACKET_FIELDS, packet)
        _write_new_csv(root / "annotations" / f"{reviewer_id}_round1.csv", ANNOTATION_FIELDS, annotations)
        written[reviewer_id] = [row["annotation_id"] for row in packet]

    adjudication_rows = [
        {
            "annotation_id": annotation_id,
            "adjudicator_id": "",
            "final_text_status": "",
            "final_signal_decision": "",
            "final_signal_types": "",
            "adjudication_note": "",
            "adjudicated_at": "",
        }
        for annotation_id in sorted(annotation_ids)
    ]
    for row in adjudication_rows:
        validate_adjudication_row(row, allow_blank=True)
    _write_new_csv(root / "adjudication" / "final_labels.csv", ADJUDICATION_FIELDS, adjudication_rows)
    return written

