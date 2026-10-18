"""Small synthetic tests only; external CSV files are never opened."""

import csv
from io import StringIO
from pathlib import Path
import sqlite3
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import analyze_new_review_inventory as inventory


FIELDS = ["platform", "product_id", "review_id", "content", "rating"]


def rows(text):
    return csv.DictReader(StringIO(text))


def connection():
    result = sqlite3.connect(":memory:")
    inventory.create_schema(result)
    return result


def test_whitespace_normalization_is_conservative():
    assert inventory.normalize_content("  한글\n English  123!  ") == "한글 English 123!"
    assert inventory.normalize_content("문장. 문장?") == "문장. 문장?"


def test_identifier_policy_prevents_numeric_dot_zero_and_preserves_strings():
    assert inventory.canonical_identifier(12345.0) == "12345"
    assert inventory.canonical_identifier("12345.0") == "12345.0"
    assert inventory.canonical_identifier("0012345") == "0012345"


def test_duplicate_blank_and_same_review_id_different_product():
    db = connection()
    try:
        reader = rows(
            "platform,product_id,review_id,content,rating\n"
            "shop,p1,r1,같은 글,5\n"
            "shop,p1,r1,같은   글,5\n"
            "shop,p2,r1,,\n"
        )
        scan = inventory.process_rows(db, "shop", "synthetic.csv", reader.fieldnames, reader)
        metrics = inventory.source_metrics(db, scan)
        assert metrics["blank_content"] == 1
        assert metrics["normalized_content_duplicates"]["extra_rows"] == 1
        assert metrics["duplicate_review_id"]["extra_rows"] == 2
        assert metrics["review_ids_across_multiple_products"] == 1
        assert metrics["unique_product_id_review_id"] == 2
    finally:
        db.close()


def test_identity_overlap_requires_product_and_platform():
    db = connection()
    try:
        db.execute("INSERT INTO base_identity VALUES ('shop', 'p1', 'r1')")
        db.execute("INSERT INTO base_review_id VALUES ('shop', 'r1')")
        reader = rows(
            "platform,product_id,review_id,content,rating\n"
            "shop,p1,r1,첫 글,5\n"
            "shop,p2,r1,둘째 글,5\n"
            "other,p1,r1,셋째 글,5\n"
        )
        scan = inventory.process_rows(db, "shop", "synthetic.csv", reader.fieldnames, reader)
        metrics = inventory.source_metrics(db, scan)
        assert metrics["identity_overlap_rows"] == 1
        assert metrics["review_id_overlap_rows"] == 2
        assert metrics["new_identity_rows"] == 2
    finally:
        db.close()


def test_same_content_different_platform_is_cross_platform_duplicate():
    db = connection()
    try:
        left = rows("platform,product_id,review_id,content,rating\na,p1,r1,동일 문장,5\n")
        right = rows("platform,product_id,review_id,content,rating\nb,p2,r2,동일  문장,4\n")
        scan_a = inventory.process_rows(db, "a", "a.csv", left.fieldnames, left)
        scan_b = inventory.process_rows(db, "b", "b.csv", right.fieldnames, right)
        per_source = {
            "a": inventory.source_metrics(db, scan_a),
            "b": inventory.source_metrics(db, scan_b),
        }
        combined = inventory.combined_metrics(db, per_source)
        assert combined["cross_platform_normalized_content_duplicate_groups"] == 1
        assert combined["cross_platform_normalized_content_participating_rows"] == 2
        assert combined["incoming_unique_normalized_contents"] == 1
    finally:
        db.close()
