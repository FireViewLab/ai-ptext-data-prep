"""Pure V2 human-review pool tests; production source CSV stays read-only."""

import csv
from hashlib import sha256
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_description_human_review_pool_v2 as builder


HIGH_TEXT = (
    "21종 핵심 성분을 포함한 두피 전문 샴푸입니다. 젤 제형이며 "
    "모발을 적신 후 적당량을 도포해 마사지하고 피부 개선에 도움을 줍니다."
)
MEDIUM_TEXT = "욕실 도구 4종 세트로 구성되어 청소하기 편리한 실속형 세트입니다."
PERSONAL_TEXT = (
    "21종 핵심 성분을 포함한 두피 전문 샴푸입니다. 젤 제형이며 "
    "적당량을 도포하면 피부 개선에 도움을 줍니다. 체험단으로 일주일 사용해봤어요."
)


def source_row(candidate_id, content, tier="HIGH", platform="shop",
               product_id="00123", review_id="00456"):
    normalized = builder.normalize_content(content)
    return {
        "candidate_id": candidate_id,
        "content_sha256": sha256(normalized.encode("utf-8")).hexdigest(),
        "tier": tier,
        "platform": platform,
        "product_id": product_id,
        "review_id": review_id,
        "content": content,
        "baseline_content_overlap": "False",
    }


def write_source(path, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=builder.SOURCE_REQUIRED_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def test_only_v2_candidates_are_included_and_identity_is_preserved():
    rows = [
        source_row("NEW-DESC-000003", MEDIUM_TEXT, tier="MEDIUM"),
        source_row("NEW-DESC-000001", HIGH_TEXT),
        source_row("NEW-DESC-000002", PERSONAL_TEXT),
    ]
    records, evaluations = builder.evaluate_rows(rows)
    assert [record["candidate_id"] for record in records] == [
        "NEW-DESC-000001", "NEW-DESC-000003",
    ]
    assert [record["v2_tier"] for record in records] == [builder.HIGH, builder.MEDIUM]
    assert evaluations["NEW-DESC-000002"]["v2_tier"] == builder.NOT_CANDIDATE
    assert records[0]["product_id"] == "00123"
    assert records[0]["review_id"] == "00456"
    assert records[0]["content"] == HIGH_TEXT


def test_order_is_deterministic_and_existing_candidate_ids_are_preserved():
    rows = [
        source_row("NEW-DESC-000020", MEDIUM_TEXT, tier="MEDIUM"),
        source_row("NEW-DESC-000010", HIGH_TEXT),
        source_row("NEW-DESC-000005", MEDIUM_TEXT, tier="MEDIUM"),
    ]
    forward, _ = builder.evaluate_rows(rows)
    backward, _ = builder.evaluate_rows(list(reversed(rows)))
    assert builder.public_records(forward) == builder.public_records(backward)
    assert [record["candidate_id"] for record in forward] == [
        "NEW-DESC-000010", "NEW-DESC-000005", "NEW-DESC-000020",
    ]


def test_duplicate_candidate_id_is_rejected():
    rows = [
        source_row("NEW-DESC-000001", HIGH_TEXT),
        source_row("NEW-DESC-000001", MEDIUM_TEXT),
    ]
    with pytest.raises(ValueError, match="중복 candidate_id"):
        builder.evaluate_rows(rows)


def test_duplicate_normalized_content_is_rejected_by_consistency_check(tmp_path):
    spaced = HIGH_TEXT.replace(" ", "  ")
    rows = [
        source_row("NEW-DESC-000001", HIGH_TEXT),
        source_row("NEW-DESC-000002", spaced),
    ]
    records, evaluations = builder.evaluate_rows(rows)
    summary = builder.build_summary(tmp_path / "source.csv", "digest", rows, records, evaluations)
    with pytest.raises(AssertionError):
        builder.validate_consistency(rows, records, summary)


def test_human_review_fields_are_blank():
    records, _ = builder.evaluate_rows([source_row("NEW-DESC-000001", HIGH_TEXT)])
    record = records[0]
    assert record["human_label"] == ""
    assert record["pattern_type"] == ""
    assert record["review_note"] == ""


def test_source_csv_is_not_modified_and_outputs_are_consistent(tmp_path):
    source = tmp_path / "source.csv"
    csv_path = tmp_path / "review.csv"
    json_path = tmp_path / "report.json"
    markdown_path = tmp_path / "report.md"
    rows = [
        source_row("NEW-DESC-000001", HIGH_TEXT),
        source_row("NEW-DESC-000002", MEDIUM_TEXT, tier="MEDIUM", platform="other"),
        source_row("NEW-DESC-000003", PERSONAL_TEXT),
    ]
    write_source(source, rows)
    before = source.read_bytes()
    source_rows = builder.read_source(source)
    records, evaluations = builder.evaluate_rows(source_rows)
    summary = builder.build_summary(
        source, builder.file_sha256(source), source_rows, records, evaluations
    )
    builder.validate_consistency(source_rows, records, summary)
    builder.write_outputs(records, summary, csv_path, json_path, markdown_path)
    builder.validate_written_outputs(csv_path, json_path, markdown_path, summary)
    assert source.read_bytes() == before


def test_known_removed_regression_ids_are_excluded():
    rows = [
        source_row("NEW-DESC-000005", PERSONAL_TEXT),
        source_row("NEW-DESC-000026", PERSONAL_TEXT),
        source_row("NEW-DESC-000047", PERSONAL_TEXT),
        source_row("NEW-DESC-000100", HIGH_TEXT),
    ]
    records, evaluations = builder.evaluate_rows(rows)
    summary = builder.build_summary(Path("source.csv"), "digest", rows, records, evaluations)
    ids = {record["candidate_id"] for record in records}
    assert not ids.intersection(builder.KNOWN_REMOVED_REGRESSIONS)
    assert all(
        item["excluded_from_review_pool"]
        for item in summary["regression_sanity"].values()
    )
