import csv
import hashlib
from pathlib import Path

import pytest

from scripts.prepare_description_human_review_annotations import (
    ANNOTATION_COLUMNS,
    HUMAN_COLUMNS,
    AnnotationValidationError,
    build_blank_annotation_rows,
    create_annotation_file,
    validate_annotation_rows,
)


def source_rows() -> list[dict[str, str]]:
    return [
        {
            "candidate_id": "NEW-DESC-000001",
            "v2_tier": "HIGH",
            "platform": "elevenst",
            "product_id": "00123",
            "review_id": "00045",
            "content": "성분과 사용 방법을 설명하는 첫 리뷰",
            "description_signal_count": "3",
            "description_signals": "ingredient_or_spec|usage_instruction|benefit_claim",
            "candidate_reason": "manual_review_candidate",
        },
        {
            "candidate_id": "NEW-DESC-000002",
            "v2_tier": "MEDIUM",
            "platform": "ohouse",
            "product_id": "P-2",
            "review_id": "R-2",
            "content": "제품 기능을 설명하는 둘째 리뷰",
            "description_signal_count": "2",
            "description_signals": "product_description|benefit_claim",
            "candidate_reason": "manual_review_candidate",
        },
    ]


def write_source(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = list(rows[0])
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_build_preserves_order_identity_content_and_leaves_human_fields_blank():
    source = source_rows()
    annotations = build_blank_annotation_rows(source)

    assert [row["candidate_id"] for row in annotations] == [
        "NEW-DESC-000001",
        "NEW-DESC-000002",
    ]
    assert annotations[0]["product_id"] == "00123"
    assert annotations[0]["review_id"] == "00045"
    assert annotations[0]["content"] == source[0]["content"]
    assert all(row[field] == "" for row in annotations for field in HUMAN_COLUMNS)

    summary = validate_annotation_rows(
        source, annotations, require_blank=True, expected_row_count=None
    )
    assert summary.row_count == 2
    assert summary.high_count == 1
    assert summary.medium_count == 1


def test_duplicate_candidate_id_is_rejected():
    source = source_rows()
    annotations = build_blank_annotation_rows(source)
    annotations[1]["candidate_id"] = annotations[0]["candidate_id"]

    with pytest.raises(AnnotationValidationError, match="Duplicate candidate_id"):
        validate_annotation_rows(source, annotations, expected_row_count=None)


def test_duplicate_normalized_content_is_rejected():
    source = source_rows()
    source[1]["content"] = "성분과  사용 방법을 설명하는 첫 리뷰"
    annotations = build_blank_annotation_rows(source)

    with pytest.raises(AnnotationValidationError, match="Duplicate normalized content"):
        validate_annotation_rows(source, annotations, expected_row_count=None)


@pytest.mark.parametrize("field", ["candidate_id", "product_id", "review_id", "content"])
def test_changed_identity_or_content_is_rejected(field: str):
    source = source_rows()
    annotations = build_blank_annotation_rows(source)
    annotations[0][field] += "-changed"

    with pytest.raises(AnnotationValidationError, match="changed preserved field"):
        validate_annotation_rows(source, annotations, expected_row_count=None)


def test_invalid_human_label_is_rejected():
    source = source_rows()
    annotations = build_blank_annotation_rows(source)
    annotations[0]["human_label"] = "MAYBE"

    with pytest.raises(AnnotationValidationError, match="invalid human_label"):
        validate_annotation_rows(source, annotations, expected_row_count=None)


def test_invalid_pattern_type_is_rejected():
    source = source_rows()
    annotations = build_blank_annotation_rows(source)
    annotations[0]["pattern_type"] = "ADVERTISEMENT"

    with pytest.raises(AnnotationValidationError, match="invalid pattern_type"):
        validate_annotation_rows(source, annotations, expected_row_count=None)


def test_documented_human_values_are_allowed_after_initial_setup():
    source = source_rows()
    annotations = build_blank_annotation_rows(source)
    annotations[0].update(
        {
            "human_label": "SUSPICIOUS",
            "pattern_type": "PRODUCT_DESCRIPTION_REPLACEMENT",
            "review_note": "manual note",
        }
    )

    summary = validate_annotation_rows(source, annotations, expected_row_count=None)
    assert summary.blank_human_label_count == 1

    with pytest.raises(AnnotationValidationError, match="nonblank initial human fields"):
        validate_annotation_rows(
            source, annotations, require_blank=True, expected_row_count=None
        )


def test_create_file_does_not_modify_source_and_refuses_overwrite(tmp_path: Path):
    source_path = tmp_path / "source.csv"
    annotation_path = tmp_path / "annotations" / "review.csv"
    write_source(source_path, source_rows())
    source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()

    summary = create_annotation_file(
        source_path, annotation_path, expected_row_count=None
    )

    assert summary.row_count == 2
    assert hashlib.sha256(source_path.read_bytes()).hexdigest() == source_hash
    with annotation_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        assert tuple(reader.fieldnames or ()) == ANNOTATION_COLUMNS
    assert rows[0]["product_id"] == "00123"
    assert rows[0]["review_id"] == "00045"

    with pytest.raises(FileExistsError, match="Refusing to overwrite"):
        create_annotation_file(source_path, annotation_path, expected_row_count=None)
