"""Pure extractor tests; no external raw CSV is opened or modified."""

import csv
from io import StringIO
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import extract_new_description_candidates as extractor


HEADERS = ["platform", "product_id", "review_id", "content"]
HIGH_TEXT = (
    "21종 핵심 성분을 포함한 두피 전문 샴푸입니다. 젤 제형이며 "
    "모발을 적신 후 적당량을 도포해 마사지하고 피부 개선에 도움을 줍니다."
)
MEDIUM_TEXT = "욕실 도구 4종 세트로 구성되어 청소하기 편리한 실속형 세트입니다."
NORMAL_TEXT = "일주일 사용해 보니 편하고 만족스럽습니다."


def reader(records):
    stream = StringIO()
    writer = csv.DictWriter(stream, fieldnames=HEADERS)
    writer.writeheader()
    writer.writerows(records)
    stream.seek(0)
    return csv.DictReader(stream)


def scan(records, baseline=()):
    rows = reader(records)
    state = extractor.ExtractionState()
    extractor.process_rows(state, "shop", rows.fieldnames, rows, set(baseline))
    return state


def row(product_id, review_id, content=HIGH_TEXT, platform="shop"):
    return {
        "platform": platform, "product_id": product_id,
        "review_id": review_id, "content": content,
    }


def test_only_high_and_medium_are_collected():
    state = scan([row("p1", "r1"), row("p2", "r2", MEDIUM_TEXT), row("p3", "r3", NORMAL_TEXT)])
    assert state.scanned_rows == 3
    assert state.raw_by_tier[extractor.HIGH] == 1
    assert state.raw_by_tier[extractor.MEDIUM] == 1
    assert len(state.candidates_by_content) == 2


def test_normalized_content_dedup_uses_deterministic_canonical_row():
    spaced = HIGH_TEXT.replace(" ", "  ")
    first = scan([row("z-product", "z-review", HIGH_TEXT), row("a-product", "a-review", spaced)])
    second = scan([row("a-product", "a-review", spaced), row("z-product", "z-review", HIGH_TEXT)])
    candidate_a = next(iter(first.candidates_by_content.values()))
    candidate_b = next(iter(second.candidates_by_content.values()))
    assert candidate_a.product_id == candidate_b.product_id == "a-product"
    assert candidate_a.review_id == candidate_b.review_id == "a-review"
    assert first.raw_by_tier[extractor.HIGH] == 2


def test_candidate_order_and_ids_are_stable():
    records = [row("p2", "r2", MEDIUM_TEXT), row("p1", "r1", HIGH_TEXT)]
    forward = extractor.candidate_records(scan(records))
    backward = extractor.candidate_records(scan(list(reversed(records))))
    assert forward == backward
    assert [item["candidate_id"] for item in forward] == ["NEW-DESC-000001", "NEW-DESC-000002"]
    assert [item["tier"] for item in forward] == [extractor.HIGH, extractor.MEDIUM]


def test_identity_strings_and_leading_zero_are_preserved():
    record = extractor.candidate_records(scan([row("00123", "00456")]))[0]
    assert record["platform"] == "shop"
    assert record["product_id"] == "00123"
    assert record["review_id"] == "00456"


def test_baseline_content_overlap_is_recorded_not_removed():
    normalized = extractor.normalize_content(HIGH_TEXT)
    record = extractor.candidate_records(scan([row("p1", "r1")], baseline={normalized}))[0]
    assert record["baseline_content_overlap"] is True
    assert record["human_label"] == ""
    assert record["review_note"] == ""
