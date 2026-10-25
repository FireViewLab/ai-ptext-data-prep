"""Build a Markdown packet for manual review of HIGH description candidates.

The input annotation CSV is treated as immutable. This script only selects rows
whose ``v2_tier`` is ``HIGH`` and never assigns or recommends a human decision.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "annotations" / "description_human_review_v1.csv"
DEFAULT_OUTPUT = (
    PROJECT_ROOT / "reports" / "description_high_human_review_packet_v1.md"
)
EXPECTED_TOTAL_COUNT = 387
EXPECTED_HIGH_COUNT = 26
HUMAN_FIELDS = ("human_label", "pattern_type", "review_note")
PACKET_FIELDS = (
    "candidate_id",
    "v2_tier",
    "platform",
    "product_id",
    "review_id",
    "content",
    "description_signal_count",
    "description_signals",
    "candidate_reason",
) + HUMAN_FIELDS


class ReviewPacketError(ValueError):
    """Raised when packet input or output fails an integrity check."""


@dataclass(frozen=True)
class PacketSummary:
    total_count: int
    high_count: int
    medium_included_count: int
    candidate_ids: tuple[str, ...]
    blank_human_label_count: int
    blank_pattern_type_count: int
    blank_review_note_count: int


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_annotation_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ReviewPacketError(f"CSV header is missing: {path}")
        missing = [field for field in PACKET_FIELDS if field not in reader.fieldnames]
        if missing:
            raise ReviewPacketError(f"CSV is missing required fields: {missing!r}")
        return list(reader)


def read_text_exact(path: Path) -> str:
    """Read text without universal-newline conversion."""

    with path.open("r", encoding="utf-8", newline="") as handle:
        return handle.read()


def select_high_rows(
    rows: Sequence[Mapping[str, str]],
    *,
    expected_total_count: int | None = EXPECTED_TOTAL_COUNT,
    expected_high_count: int = EXPECTED_HIGH_COUNT,
) -> list[Mapping[str, str]]:
    if expected_total_count is not None and len(rows) != expected_total_count:
        raise ReviewPacketError(
            f"Annotation row count is {len(rows)}; expected {expected_total_count}."
        )

    high_rows = [row for row in rows if row["v2_tier"] == "HIGH"]
    if len(high_rows) != expected_high_count:
        raise ReviewPacketError(
            f"HIGH row count is {len(high_rows)}; expected {expected_high_count}."
        )

    candidate_ids = [row["candidate_id"] for row in high_rows]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ReviewPacketError("Duplicate candidate_id found among HIGH rows.")

    for csv_row_number, row in enumerate(rows, start=2):
        nonblank = [field for field in HUMAN_FIELDS if row[field] != ""]
        if nonblank:
            raise ReviewPacketError(
                f"CSV row {csv_row_number} has nonblank human fields: {nonblank!r}."
            )

    return high_rows


def _header(high_rows: Sequence[Mapping[str, str]]) -> str:
    lines = [
        "# P_text Description HIGH Human Review Packet V1",
        "",
        "## Human Review 안내",
        "",
        "### 목적",
        "",
        "HIGH는 suspicious 확정 라벨이 아니라",
        "사람이 우선 검토할 candidate tier이다.",
        "",
        "### human_label 허용값",
        "",
        "- SUSPICIOUS",
        "- NORMAL",
        "- UNCERTAIN",
        "",
        "### 기본 판정 원칙",
        "",
        "SUSPICIOUS:",
        "리뷰라기보다 상품 상세설명, 홍보문, 스펙/효능/사용법 복사문처럼 보이며",
        "실제 개인 사용 경험의 근거가 부족한 경우.",
        "",
        "NORMAL:",
        "상품 설명 요소가 포함되어 있더라도",
        "구매·사용·착용·섭취·배송·체감 등",
        "실제 개인 경험이 자연스럽고 구체적으로 확인되는 경우.",
        "",
        "UNCERTAIN:",
        "본문만으로 실제 경험 여부 또는",
        "상품 상세설명 대체 패턴 여부를 확신하기 어려운 경우.",
        "",
        "주의:",
        "위 기준은 사람이 판단하기 위한 가이드일 뿐,",
        "스크립트가 자동 판정해서는 안 된다.",
        "",
        "## Review progress",
        "",
        "| candidate_id | reviewed | human_label |",
        "| --- | --- | --- |",
    ]
    lines.extend(
        f'| {row["candidate_id"]} | [ ] | |' for row in high_rows
    )
    lines.extend(["", "---", ""])
    return "\n".join(lines)


def _candidate_section(index: int, row: Mapping[str, str]) -> str:
    # Do not strip, normalize, escape, or otherwise transform row["content"].
    prefix = "\n".join(
        [
            f'## {index:02d}. {row["candidate_id"]}',
            "",
            f'- candidate_id: {row["candidate_id"]}',
            f'- tier: {row["v2_tier"]}',
            f'- platform: {row["platform"]}',
            f'- product_id: {row["product_id"]}',
            f'- review_id: {row["review_id"]}',
            f'- description_signal_count: {row["description_signal_count"]}',
            f'- description_signals: {row["description_signals"]}',
            f'- candidate_reason: {row["candidate_reason"]}',
            "",
            "### Review text",
            "",
        ]
    )
    suffix = "\n".join(
        [
            "",
            "",
            "### Human decision",
            "",
            "- human_label:",
            "- pattern_type:",
            "- review_note:",
            "",
            "---",
            "",
        ]
    )
    return prefix + row["content"] + suffix


def build_packet(high_rows: Sequence[Mapping[str, str]]) -> str:
    return _header(high_rows) + "".join(
        _candidate_section(index, row)
        for index, row in enumerate(high_rows, start=1)
    )


def validate_packet(
    rows: Sequence[Mapping[str, str]],
    packet: str,
    *,
    expected_total_count: int | None = EXPECTED_TOTAL_COUNT,
    expected_high_count: int = EXPECTED_HIGH_COUNT,
) -> PacketSummary:
    high_rows = select_high_rows(
        rows,
        expected_total_count=expected_total_count,
        expected_high_count=expected_high_count,
    )
    expected_packet = build_packet(high_rows)
    if packet != expected_packet:
        raise ReviewPacketError(
            "Packet does not exactly match the ordered HIGH rows and original content."
        )

    section_ids = re.findall(r"(?m)^## \d{2}\. (NEW-DESC-[^\r\n]+)$", packet)
    expected_ids = [row["candidate_id"] for row in high_rows]
    if section_ids != expected_ids:
        raise ReviewPacketError("Detailed candidate sections are missing or out of order.")
    if any(section_ids.count(candidate_id) != 1 for candidate_id in expected_ids):
        raise ReviewPacketError("A HIGH candidate detailed section is not unique.")

    decision_block = (
        "### Human decision\n\n"
        "- human_label:\n"
        "- pattern_type:\n"
        "- review_note:"
    )
    if packet.count(decision_block) != expected_high_count:
        raise ReviewPacketError("Human decision fields are not all blank.")

    return PacketSummary(
        total_count=len(rows),
        high_count=len(high_rows),
        medium_included_count=sum(
            row["v2_tier"] == "MEDIUM" for row in high_rows
        ),
        candidate_ids=tuple(expected_ids),
        blank_human_label_count=len(high_rows),
        blank_pattern_type_count=len(high_rows),
        blank_review_note_count=len(high_rows),
    )


def build_packet_file(
    input_path: Path,
    output_path: Path,
) -> tuple[PacketSummary, str, str]:
    if output_path.exists():
        raise FileExistsError(f"Refusing to overwrite existing packet: {output_path}")

    source_hash_before = file_sha256(input_path)
    rows = read_annotation_rows(input_path)
    high_rows = select_high_rows(rows)
    packet = build_packet(high_rows)
    summary = validate_packet(rows, packet)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("x", encoding="utf-8", newline="") as handle:
        handle.write(packet)

    source_hash_after = file_sha256(input_path)
    if source_hash_after != source_hash_before:
        raise ReviewPacketError("Annotation CSV changed while building the packet.")

    written_packet = read_text_exact(output_path)
    validate_packet(rows, written_packet)
    return summary, source_hash_before, source_hash_after


def validate_packet_file(input_path: Path, output_path: Path) -> PacketSummary:
    source_hash_before = file_sha256(input_path)
    rows = read_annotation_rows(input_path)
    packet = read_text_exact(output_path)
    summary = validate_packet(rows, packet)
    if file_sha256(input_path) != source_hash_before:
        raise ReviewPacketError("Annotation CSV changed during packet validation.")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build or validate a Markdown packet for human review of HIGH rows. "
            "No human decisions are assigned."
        )
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate an existing packet instead of creating one.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.check:
        source_hash_before = file_sha256(args.input)
        summary = validate_packet_file(args.input, args.output)
        source_hash_after = file_sha256(args.input)
        status = "validated"
    else:
        summary, source_hash_before, source_hash_after = build_packet_file(
            args.input, args.output
        )
        status = "created"

    print("HIGH HUMAN REVIEW PACKET - no automatic decisions assigned")
    print(f"status={status}")
    print(f"output={args.output}")
    print(f"high_count={summary.high_count}")
    print(f"medium_included_count={summary.medium_included_count}")
    print(
        "blank_human_fields="
        f"human_label:{summary.blank_human_label_count},"
        f"pattern_type:{summary.blank_pattern_type_count},"
        f"review_note:{summary.blank_review_note_count}"
    )
    print(f"annotation_sha256_before={source_hash_before}")
    print(f"annotation_sha256_after={source_hash_after}")
    print("candidate_ids=" + ",".join(summary.candidate_ids))
    print("integrity=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
