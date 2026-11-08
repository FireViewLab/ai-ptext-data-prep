import csv

import pytest

from scripts import ptext_pilot_review as review


@pytest.mark.parametrize(
    ("status", "decision", "types"),
    [
        ("SUFFICIENT", "PRESENT", "PRODUCT_DESCRIPTION_LIKE"),
        ("SUFFICIENT", "PRESENT", "PRODUCT_DESCRIPTION_LIKE|WITHIN_REVIEW_REPETITION"),
        ("SUFFICIENT", "ABSENT", ""),
        ("SUFFICIENT", "UNCERTAIN", ""),
        ("SUFFICIENT", "UNCERTAIN", "PROMOTIONAL_OR_SALES_LANGUAGE"),
        ("INSUFFICIENT", "NOT_ASSESSED", ""),
        ("INVALID", "NOT_ASSESSED", ""),
    ],
)
def test_allowed_label_combinations(status, decision, types):
    review.validate_label_combination(status, decision, types)


@pytest.mark.parametrize(
    ("status", "decision", "types", "code"),
    [
        ("SUFFICIENT", "PRESENT", "", "PRESENT_REQUIRES_SIGNAL_TYPE"),
        ("SUFFICIENT", "ABSENT", "PRODUCT_DESCRIPTION_LIKE", "ABSENT_FORBIDS_SIGNAL_TYPE"),
        ("INSUFFICIENT", "ABSENT", "", "UNASSESSED_STATUS_REQUIRES_EMPTY_SIGNALS"),
        ("INVALID", "PRESENT", "WITHIN_REVIEW_REPETITION", "UNASSESSED_STATUS_REQUIRES_EMPTY_SIGNALS"),
        ("SUFFICIENT", "NOT_ASSESSED", "", "INVALID_STATUS_DECISION_COMBINATION"),
    ],
)
def test_invalid_label_combinations_are_rejected(status, decision, types, code):
    with pytest.raises(review.AnnotationValidationError, match=code):
        review.validate_label_combination(status, decision, types)


def test_unknown_and_duplicate_signal_types_are_rejected():
    with pytest.raises(review.AnnotationValidationError, match="UNKNOWN_SIGNAL_TYPE"):
        review.parse_signal_types("NOT_A_SIGNAL")
    with pytest.raises(review.AnnotationValidationError, match="DUPLICATE_SIGNAL_TYPE"):
        review.parse_signal_types("PRODUCT_DESCRIPTION_LIKE|PRODUCT_DESCRIPTION_LIKE")


def test_final_adjudication_uses_same_two_axis_contract():
    row = {
        "annotation_id": "annotation-1",
        "adjudicator_id": "adjudicator",
        "final_text_status": "SUFFICIENT",
        "final_signal_decision": "PRESENT",
        "final_signal_types": "PRODUCT_DESCRIPTION_LIKE|WITHIN_REVIEW_REPETITION",
        "adjudication_note": "synthetic fixture note",
        "adjudicated_at": "2026-11-08T00:00:00+09:00",
    }
    review.validate_adjudication_row(row)
    row["final_signal_types"] = ""
    with pytest.raises(review.AnnotationValidationError, match="PRESENT_REQUIRES_SIGNAL_TYPE"):
        review.validate_adjudication_row(row)


def test_blind_bundle_has_independent_reviewers_and_separate_adjudication(tmp_path):
    rows = [
        {"annotation_id": f"annotation-{index}", "content": f"synthetic review {index}"}
        for index in range(30)
    ]
    root = tmp_path / "blind"
    orders = review.write_blind_review_bundle(
        root,
        rows,
        seed=20261108,
        guideline_version="v0.2",
    )
    assert set(orders) == {"reviewer_a", "reviewer_b"}
    assert set(orders["reviewer_a"]) == set(orders["reviewer_b"])
    assert orders["reviewer_a"] != orders["reviewer_b"]

    for reviewer_id in orders:
        packet_path = root / "reviewer_packets" / f"{reviewer_id}.csv"
        annotation_path = root / "annotations" / f"{reviewer_id}_round1.csv"
        with packet_path.open("r", encoding="utf-8-sig", newline="") as handle:
            packet = csv.DictReader(handle)
            review.validate_packet_schema(packet.fieldnames)
            assert not (set(packet.fieldnames) & review.FORBIDDEN_PACKET_FIELDS)
        with annotation_path.open("r", encoding="utf-8-sig", newline="") as handle:
            annotations = list(csv.DictReader(handle))
        assert {row["annotator_id"] for row in annotations} == {reviewer_id}
        assert all(row["text_status"] == "" for row in annotations)

    assert (root / "adjudication" / "final_labels.csv").is_file()
    with pytest.raises(FileExistsError, match="REVIEW_BUNDLE_ALREADY_EXISTS"):
        review.write_blind_review_bundle(root, rows, seed=20261108, guideline_version="v0.2")

