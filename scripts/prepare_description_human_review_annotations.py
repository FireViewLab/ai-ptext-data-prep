"""Prepare and validate a human-only annotation CSV for V2 candidates.

This script never assigns labels. It copies the immutable candidate identity and
review fields into a Git-trackable annotation file, leaving all human fields
blank. Validation can then be run before and after manual review.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = PROJECT_ROOT / "outputs" / "description_human_review_pool_v2_20261021.csv"
DEFAULT_ANNOTATION = PROJECT_ROOT / "annotations" / "description_human_review_v1.csv"
EXPECTED_ROW_COUNT = 387

PRESERVED_COLUMNS = (
    "candidate_id",
    "v2_tier",
    "platform",
    "product_id",
    "review_id",
    "content",
    "description_signal_count",
    "description_signals",
    "candidate_reason",
)
HUMAN_COLUMNS = ("human_label", "pattern_type", "review_note")
ANNOTATION_COLUMNS = PRESERVED_COLUMNS + HUMAN_COLUMNS

ALLOWED_HUMAN_LABELS = frozenset({"", "SUSPICIOUS", "NORMAL", "UNCERTAIN"})
ALLOWED_PATTERN_TYPES = frozenset(
    {"", "PRODUCT_DESCRIPTION_REPLACEMENT", "OTHER", "UNKNOWN"}
)


class AnnotationValidationError(ValueError):
    """Raised when an annotation file no longer matches its source pool."""


@dataclass(frozen=True)
class ValidationSummary:
    row_count: int
    high_count: int
    medium_count: int
    duplicate_candidate_id_count: int
    duplicate_normalized_content_count: int
    blank_human_label_count: int
    blank_pattern_type_count: int
    blank_review_note_count: int


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise AnnotationValidationError(f"CSV header is missing: {path}")
        return list(reader.fieldnames), list(reader)


def normalize_content(value: str) -> str:
    """Normalize spacing only, matching the pool's exact-duplicate diagnostic."""

    return re.sub(r"\s+", " ", value).strip()


def build_blank_annotation_rows(
    source_rows: Iterable[Mapping[str, str]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for source_row in source_rows:
        row = {column: source_row[column] for column in PRESERVED_COLUMNS}
        row.update({column: "" for column in HUMAN_COLUMNS})
        rows.append(row)
    return rows


def _duplicates(values: Iterable[str]) -> set[str]:
    counts = Counter(values)
    return {value for value, count in counts.items() if count > 1}


def validate_annotation_rows(
    source_rows: Sequence[Mapping[str, str]],
    annotation_rows: Sequence[Mapping[str, str]],
    *,
    require_blank: bool = False,
    expected_row_count: int | None = EXPECTED_ROW_COUNT,
) -> ValidationSummary:
    if expected_row_count is not None and len(source_rows) != expected_row_count:
        raise AnnotationValidationError(
            f"Source row count is {len(source_rows)}; expected {expected_row_count}."
        )
    if len(annotation_rows) != len(source_rows):
        raise AnnotationValidationError(
            f"Annotation row count is {len(annotation_rows)}; source has {len(source_rows)}."
        )

    duplicate_ids = _duplicates(row["candidate_id"] for row in annotation_rows)
    if duplicate_ids:
        raise AnnotationValidationError(
            f"Duplicate candidate_id values: {sorted(duplicate_ids)!r}"
        )

    normalized_contents = [normalize_content(row["content"]) for row in annotation_rows]
    duplicate_contents = _duplicates(normalized_contents)
    if duplicate_contents:
        raise AnnotationValidationError(
            f"Duplicate normalized content found in {len(duplicate_contents)} group(s)."
        )

    for row_number, (source_row, annotation_row) in enumerate(
        zip(source_rows, annotation_rows), start=2
    ):
        for column in PRESERVED_COLUMNS:
            if annotation_row[column] != source_row[column]:
                raise AnnotationValidationError(
                    f"Row {row_number} changed preserved field {column!r}."
                )

        human_label = annotation_row["human_label"]
        if human_label not in ALLOWED_HUMAN_LABELS:
            raise AnnotationValidationError(
                f"Row {row_number} has invalid human_label {human_label!r}."
            )

        pattern_type = annotation_row["pattern_type"]
        if pattern_type not in ALLOWED_PATTERN_TYPES:
            raise AnnotationValidationError(
                f"Row {row_number} has invalid pattern_type {pattern_type!r}."
            )

        if require_blank:
            nonblank = [
                column for column in HUMAN_COLUMNS if annotation_row[column] != ""
            ]
            if nonblank:
                raise AnnotationValidationError(
                    f"Row {row_number} has nonblank initial human fields: {nonblank!r}"
                )

    tiers = Counter(row["v2_tier"] for row in annotation_rows)
    return ValidationSummary(
        row_count=len(annotation_rows),
        high_count=tiers["HIGH"],
        medium_count=tiers["MEDIUM"],
        duplicate_candidate_id_count=0,
        duplicate_normalized_content_count=0,
        blank_human_label_count=sum(row["human_label"] == "" for row in annotation_rows),
        blank_pattern_type_count=sum(row["pattern_type"] == "" for row in annotation_rows),
        blank_review_note_count=sum(row["review_note"] == "" for row in annotation_rows),
    )


def validate_annotation_file(
    source_path: Path,
    annotation_path: Path,
    *,
    require_blank: bool = False,
    expected_row_count: int | None = EXPECTED_ROW_COUNT,
) -> ValidationSummary:
    source_header, source_rows = read_csv_rows(source_path)
    missing_source_columns = [
        column for column in PRESERVED_COLUMNS if column not in source_header
    ]
    if missing_source_columns:
        raise AnnotationValidationError(
            f"Source is missing required columns: {missing_source_columns!r}"
        )

    annotation_header, annotation_rows = read_csv_rows(annotation_path)
    if tuple(annotation_header) != ANNOTATION_COLUMNS:
        raise AnnotationValidationError(
            "Annotation columns or order changed: "
            f"expected {list(ANNOTATION_COLUMNS)!r}, got {annotation_header!r}."
        )

    return validate_annotation_rows(
        source_rows,
        annotation_rows,
        require_blank=require_blank,
        expected_row_count=expected_row_count,
    )


def create_annotation_file(
    source_path: Path,
    annotation_path: Path,
    *,
    expected_row_count: int | None = EXPECTED_ROW_COUNT,
) -> ValidationSummary:
    if annotation_path.exists():
        raise FileExistsError(
            f"Refusing to overwrite existing annotation file: {annotation_path}"
        )

    source_hash_before = file_sha256(source_path)
    source_header, source_rows = read_csv_rows(source_path)
    missing_source_columns = [
        column for column in PRESERVED_COLUMNS if column not in source_header
    ]
    if missing_source_columns:
        raise AnnotationValidationError(
            f"Source is missing required columns: {missing_source_columns!r}"
        )

    annotation_rows = build_blank_annotation_rows(source_rows)
    validate_annotation_rows(
        source_rows,
        annotation_rows,
        require_blank=True,
        expected_row_count=expected_row_count,
    )

    annotation_path.parent.mkdir(parents=True, exist_ok=True)
    with annotation_path.open("x", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ANNOTATION_COLUMNS)
        writer.writeheader()
        writer.writerows(annotation_rows)

    if file_sha256(source_path) != source_hash_before:
        raise AnnotationValidationError("Source pool changed while creating annotations.")

    return validate_annotation_file(
        source_path,
        annotation_path,
        require_blank=True,
        expected_row_count=expected_row_count,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create or validate a human-review annotation CSV. "
            "No labels are assigned automatically."
        )
    )
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--annotation", type=Path, default=DEFAULT_ANNOTATION)
    parser.add_argument(
        "--create",
        action="store_true",
        help="Create a new blank annotation CSV; refuses to overwrite.",
    )
    parser.add_argument(
        "--require-blank",
        action="store_true",
        help="Require all human fields to be blank (initial setup validation).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.create:
        summary = create_annotation_file(args.source, args.annotation)
        action = "created"
    else:
        summary = validate_annotation_file(
            args.source, args.annotation, require_blank=args.require_blank
        )
        action = "validated"

    print("HUMAN ANNOTATION WORKFLOW - no automatic labels assigned")
    print(f"annotation_file={args.annotation}")
    print(f"status={action}")
    print(f"rows={summary.row_count}")
    print(f"tiers=HIGH:{summary.high_count},MEDIUM:{summary.medium_count}")
    print(
        "blank_human_fields="
        f"human_label:{summary.blank_human_label_count},"
        f"pattern_type:{summary.blank_pattern_type_count},"
        f"review_note:{summary.blank_review_note_count}"
    )
    print("integrity=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
