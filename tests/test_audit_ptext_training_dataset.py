"""Small in-memory tests; never touch actual dataset or labels."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_ptext_training_dataset import conflicts, deterministic_samples, document_phrases, exact_stats
from generate_ptext_synthetic import TYPES


def test_exact_counts_and_label_conflicts_preserve_whitespace():
    rows = [{"content": text, "label": label} for text, label in [
        ("동일", "NORMAL"), ("동일", "NORMAL"), ("동일", "SUSPICIOUS"),
        ("동일 ", "SUSPICIOUS"), ("다름", "NORMAL"),
    ]]
    assert exact_stats(rows) == {"groups": 1, "participating_rows": 3, "extra_rows": 2}
    assert len(conflicts(rows)) == 1
    assert len(conflicts(rows)[0]) == 3


def test_review_samples_reproducible_without_replacement():
    rows = []
    for kind in TYPES:
        for index in range(12):
            rows.append({"dataset_excel_row": len(rows) + 2, "synthetic_type": kind,
                         "label_origin": "synthetic", "label": "SUSPICIOUS"})
    for origin, label, count in (("sampled_non_candidate", "NORMAL", 35),
                                 ("human_candidate_review", "NORMAL", 25), ("human_suspicious", "SUSPICIOUS", 1)):
        for _ in range(count):
            rows.append({"dataset_excel_row": len(rows) + 2, "synthetic_type": None,
                         "label_origin": origin, "label": label})
    first = deterministic_samples(rows)
    assert first == deterministic_samples(list(reversed(rows)))
    assert sum(map(len, first.values())) == 101
    assert all(len(first[kind]) == 10 for kind in TYPES)
    selected = [r["dataset_excel_row"] for members in first.values() for r in members]
    assert len(set(selected)) == 101


def test_expression_counts_are_document_frequency():
    rows = [{"content": "좋은 선택을 권해요 좋은 선택을 권해요"}, {"content": "좋은 선택을 권해요"}]
    counts = dict(document_phrases(rows))
    assert counts["좋은 선택을 권해요"] == 2
