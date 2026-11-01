import csv
from hashlib import sha256
from pathlib import Path
import sqlite3

from scripts.verify_raw_review_source_integrity import content_fingerprint, verify_platform


def test_content_fingerprint_matches_manifest_normalization():
    digest, length = content_fingerprint("  hello\n world  ")
    assert digest == sha256("hello world".encode()).hexdigest()
    assert length == 11


def test_verify_platform_matches_tiny_read_only_manifest(tmp_path: Path):
    base = tmp_path / "export"; nested = base / "reviews_shop.csv"; nested.mkdir(parents=True)
    raw = nested / "reviews_shop.csv"
    fields = ["platform", "product_id", "review_id", "content", "product_category", "rating"]
    with raw.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader()
        writer.writerow({"platform":"shop","product_id":"001","review_id":"0001","content":"hello  world","product_category":"cat","rating":"5"})
    digest, length = content_fingerprint("hello  world")
    database = tmp_path / "manifest.sqlite3"
    with sqlite3.connect(database) as db:
        db.execute("CREATE TABLE review_index(source_row INTEGER,platform TEXT,product_id TEXT,review_id TEXT,product_category_raw TEXT,normalized_content_hash TEXT,content_length INTEGER)")
        db.execute("INSERT INTO review_index VALUES(2,'shop','001','0001','cat',?,?)", (digest,length))
    stat = raw.stat(); stored = {"size":stat.st_size,"mtime_ns":stat.st_mtime_ns}
    with sqlite3.connect(f"file:{database.as_posix()}?mode=ro", uri=True) as db:
        result = verify_platform(db, base, "shop", stored, 1)
    assert result["analysis_fields_exact_match"] is True
    assert result["signature_match"]["all_stored_fields"] is True
    assert result["unchanged_during_verification"] is True
