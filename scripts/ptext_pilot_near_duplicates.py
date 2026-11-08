"""Candidate-only near-duplicate utilities for the P_text pilot.

This module deliberately does not decide which reviews are duplicates.  It
normalizes text, produces deterministic MinHash/LSH candidates, and exposes an
exact Jaccard diagnostic so a threshold can be calibrated on synthetic and
human-reviewed pairs before any real review is excluded.
"""

from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import re
import unicodedata
from typing import Iterable, Mapping, Sequence


POLICY_VERSION = "ptext-near-duplicate-candidate-v1"
DEFAULT_SHINGLE_SIZE = 5
DEFAULT_NUM_PERMUTATIONS = 128
DEFAULT_BANDS = 32
DEFAULT_ROWS_PER_BAND = 4


def normalize_for_near_duplicate(value: str) -> str:
    """Return the comparison copy; never use it to replace source content."""

    normalized = unicodedata.normalize("NFKC", str(value))
    normalized = normalized.casefold()
    return re.sub(r"\s+", " ", normalized).strip()


def character_shingles(value: str, size: int = DEFAULT_SHINGLE_SIZE) -> frozenset[str]:
    if size < 1:
        raise ValueError("shingle size must be positive")
    normalized = normalize_for_near_duplicate(value)
    if not normalized:
        return frozenset()
    if len(normalized) <= size:
        return frozenset({normalized})
    return frozenset(normalized[index:index + size] for index in range(len(normalized) - size + 1))


def jaccard_similarity(left: Iterable[str], right: Iterable[str]) -> float:
    a, b = set(left), set(right)
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def minhash_signature(
    tokens: Iterable[str],
    *,
    seed: int,
    permutations: int = DEFAULT_NUM_PERMUTATIONS,
) -> tuple[int, ...]:
    """Build a deterministic signature suitable for candidate generation."""

    values = tuple(sorted(set(tokens)))
    if permutations < 1:
        raise ValueError("permutations must be positive")
    if not values:
        return tuple((1 << 256) - 1 for _ in range(permutations))
    result = []
    for permutation in range(permutations):
        prefix = f"{seed}\x1f{permutation}\x1f".encode("utf-8")
        result.append(min(int.from_bytes(sha256(prefix + value.encode("utf-8")).digest(), "big") for value in values))
    return tuple(result)


def lsh_candidate_pairs(
    documents: Mapping[str, str],
    *,
    seed: int,
    blocks: Mapping[str, str] | None = None,
    shingle_size: int = DEFAULT_SHINGLE_SIZE,
    bands: int = DEFAULT_BANDS,
    rows_per_band: int = DEFAULT_ROWS_PER_BAND,
) -> set[tuple[str, str]]:
    """Return candidates only; callers must not treat these pairs as exclusions."""

    if bands < 1 or rows_per_band < 1:
        raise ValueError("bands and rows_per_band must be positive")
    permutations = bands * rows_per_band
    if blocks is not None and set(blocks) != set(documents):
        raise ValueError("blocks must have exactly the document IDs")
    buckets: dict[tuple[str, int, tuple[int, ...]], list[str]] = defaultdict(list)
    for document_id in sorted(documents):
        tokens = character_shingles(documents[document_id], shingle_size)
        if not tokens:
            continue
        signature = minhash_signature(
            tokens,
            seed=seed,
            permutations=permutations,
        )
        block = blocks[document_id] if blocks is not None else "ALL"
        for band in range(bands):
            start = band * rows_per_band
            buckets[(block, band, signature[start:start + rows_per_band])].append(document_id)

    pairs: set[tuple[str, str]] = set()
    for members in buckets.values():
        unique = sorted(set(members))
        for left_index, left in enumerate(unique):
            for right in unique[left_index + 1:]:
                pairs.add((left, right))
    return pairs


def score_candidate_pairs(
    documents: Mapping[str, str],
    pairs: Iterable[tuple[str, str]],
    *,
    shingle_size: int = DEFAULT_SHINGLE_SIZE,
) -> list[dict[str, object]]:
    """Score candidates for calibration without assigning duplicate labels."""

    tokenized = {
        document_id: character_shingles(text, shingle_size)
        for document_id, text in documents.items()
    }
    return [
        {
            "left_id": left,
            "right_id": right,
            "jaccard": jaccard_similarity(tokenized[left], tokenized[right]),
            "decision": "UNREVIEWED",
        }
        for left, right in sorted(set(pairs))
    ]


def policy_contract() -> dict[str, object]:
    return {
        "policy_version": POLICY_VERSION,
        "status": "CANDIDATE_GENERATION_ONLY",
        "normalization": "Unicode NFKC, casefold, whitespace collapse, source text unchanged",
        "shingle_type": "character",
        "shingle_size": DEFAULT_SHINGLE_SIZE,
        "num_permutations": DEFAULT_NUM_PERMUTATIONS,
        "bands": DEFAULT_BANDS,
        "rows_per_band": DEFAULT_ROWS_PER_BAND,
        "real_data_blocking": "required: length band plus approved language/category key",
        "exclusion_threshold": None,
        "required_before_exclusion": [
            "synthetic perturbation recall/false-candidate evaluation",
            "bounded human adjudication sample",
            "threshold and policy version approval",
        ],
    }

