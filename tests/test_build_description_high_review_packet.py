import csv
import hashlib
from pathlib import Path

import pytest

from scripts.build_description_high_review_packet import (
    HUMAN_FIELDS,
    ReviewPacketError,
    build_packet,
    build_packet_file,
    select_high_rows,
    validate_packet,
)


def annotation_rows() -> list[dict[str, str]]:
    common = {
        "platform": "elevenst",
        "description_signal_count": "3",
        "description_signals": "ingredient_or_spec|product_description|benefit_claim",
        "candidate_reason": "description_signals>=3_and_no_personal_experience",
        "human_label": "",
        "pattern_type": "",
        "review_note": "",
    }
    return [
        {
            **common,
            "candidate_id": "NEW-DESC-000003",
            "v2_tier": "HIGH",
            "product_id": "00123",
            "review_id": "00045",
            "content": "첫 줄  \r\n## Markdown 원문 😊\n끝 공백   ",
        },
        {
            **common,
            "candidate_id": "NEW-DESC-000004",
            "v2_tier": "HIGH",
            "product_id": "00124",
            "review_id": "00046",
            "content": "두 번째 원문",
        },
        {
            **common,
            "candidate_id": "NEW-DESC-000005",
            "v2_tier": "MEDIUM",
            "product_id": "00125",
            "review_id": "00047",
            "content": "패킷에 포함되면 안 되는 MEDIUM 원문",
        },
    ]


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def select_test_high_rows(rows: list[dict[str, str]]):
    return select_high_rows(
        rows, expected_total_count=None, expected_high_count=2
    )


def validate_test_packet(rows: list[dict[str, str]], packet: str):
    return validate_packet(
        rows,
        packet,
        expected_total_count=None,
        expected_high_count=2,
    )


def test_selects_only_high_rows_in_original_csv_order():
    rows = annotation_rows()
    high_rows = select_test_high_rows(rows)

    assert [row["candidate_id"] for row in high_rows] == [
        "NEW-DESC-000003",
        "NEW-DESC-000004",
    ]
    assert all(row["v2_tier"] == "HIGH" for row in high_rows)


def test_packet_preserves_identity_and_content_verbatim():
    rows = annotation_rows()
    packet = build_packet(select_test_high_rows(rows))

    assert "- product_id: 00123" in packet
    assert "- review_id: 00045" in packet
    assert rows[0]["content"] in packet
    assert "끝 공백   \n\n### Human decision" in packet
    assert "패킷에 포함되면 안 되는 MEDIUM 원문" not in packet


def test_each_high_candidate_has_exactly_one_detailed_section():
    rows = annotation_rows()
    packet = build_packet(select_test_high_rows(rows))
    summary = validate_test_packet(rows, packet)

    assert summary.high_count == 2
    assert summary.medium_included_count == 0
    assert packet.count("## 01. NEW-DESC-000003\n") == 1
    assert packet.count("## 02. NEW-DESC-000004\n") == 1


def test_human_decision_fields_are_all_blank():
    rows = annotation_rows()
    packet = build_packet(select_test_high_rows(rows))

    assert packet.count("- human_label:\n") == 2
    assert packet.count("- pattern_type:\n") == 2
    assert packet.count("- review_note:\n") == 2
    validate_test_packet(rows, packet)


def test_duplicate_high_candidate_id_is_rejected():
    rows = annotation_rows()
    rows[1]["candidate_id"] = rows[0]["candidate_id"]

    with pytest.raises(ReviewPacketError, match="Duplicate candidate_id"):
        select_test_high_rows(rows)


@pytest.mark.parametrize("field", HUMAN_FIELDS)
def test_nonblank_human_field_is_rejected(field: str):
    rows = annotation_rows()
    rows[0][field] = "must not be copied"

    with pytest.raises(ReviewPacketError, match="nonblank human fields"):
        select_test_high_rows(rows)


def test_changed_packet_identity_or_content_is_rejected():
    rows = annotation_rows()
    packet = build_packet(select_test_high_rows(rows))
    changed = packet.replace("00123", "123", 1)

    with pytest.raises(ReviewPacketError, match="does not exactly match"):
        validate_test_packet(rows, changed)


def test_build_file_does_not_modify_annotation_and_refuses_overwrite(
    tmp_path: Path,
):
    rows = annotation_rows()
    input_path = tmp_path / "annotation.csv"
    output_path = tmp_path / "packet.md"
    write_rows(input_path, rows)
    source_hash = hashlib.sha256(input_path.read_bytes()).hexdigest()

    # Exercise the file API with a production-shaped fixture.
    production_rows = []
    for index in range(26):
        source = rows[index % 2].copy()
        source["candidate_id"] = f"NEW-DESC-{index + 1:06d}"
        source["review_id"] = f"{index + 1:05d}"
        source["content"] = f'{source["content"]}-{index}'
        production_rows.append(source)
    for index in range(361):
        source = rows[2].copy()
        source["candidate_id"] = f"NEW-DESC-{index + 27:06d}"
        source["review_id"] = f"{index + 27:05d}"
        source["content"] = f'{source["content"]}-{index}'
        production_rows.append(source)
    write_rows(input_path, production_rows)
    source_hash = hashlib.sha256(input_path.read_bytes()).hexdigest()

    summary, before_hash, after_hash = build_packet_file(input_path, output_path)

    assert summary.high_count == 26
    assert before_hash == after_hash == source_hash
    assert hashlib.sha256(input_path.read_bytes()).hexdigest() == source_hash
    with pytest.raises(FileExistsError, match="Refusing to overwrite"):
        build_packet_file(input_path, output_path)
