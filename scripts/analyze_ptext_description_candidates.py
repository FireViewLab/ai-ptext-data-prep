"""Explore product-description-like reviews for human review only.

This shadow analysis is deliberately separate from
``extract_ptext_candidates.py``.  It does not change the existing candidate
rules, write an output workbook, or assign SUSPICIOUS/NORMAL labels.  The
signals below are text-only heuristics for finding records that a person may
want to inspect.
"""

import argparse
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import re
import sys

from inspect_reviews import PROJECT_ROOT, is_blank, read_reviews


DESCRIPTION_SIGNALS = (
    "ingredient_or_spec",
    "product_description",
    "usage_instruction",
    "benefit_claim",
)
PERSONAL_EXPERIENCE = "personal_experience"
SIGNAL_ORDER = (*DESCRIPTION_SIGNALS, PERSONAL_EXPERIENCE)

# Precision-first text evidence.  Generic words such as 제품입니다, 기능, 효과,
# 해결, 추천 are intentionally not standalone description signals.
SIGNAL_PATTERNS = {
    "ingredient_or_spec": (
        re.compile(
            r"(?:핵심|주요|유효)\s*(?:성분|원료)"
            r"|(?:성분|원료|추출물).{0,24}(?:함유|포함|배합)"
            r"|(?:함유|포함|배합)(?:하|되|된|한|하여|해|했|시킨|시켜)?.{0,24}(?:성분|원료|추출물)"
        ),
        re.compile(
            r"(?:용량|중량|규격|사이즈|색상|원산지|제조국|함량|농도|순도)\s*[:：]\s*\S+"
        ),
        re.compile(
            r"\b\d+(?:[.,]\d+)?\s*(?:%|퍼센트|ml|mL|L|g|kg|mg|cm|mm|W|V|mAh|Hz|GB|종)(?![A-Za-z0-9])",
            re.IGNORECASE,
        ),
        re.compile(r"(?:재질|소재)\s*(?:은|는|:|：)\s*.{1,30}(?:입니다|사용|적용|구성)"),
    ),
    "product_description": (
        re.compile(
            r"(?:개발|설계|제작|구성|적용|완성)(?:되|된|되어|한|하여)"
        ),
        re.compile(
            r"(?:젤|크림|액상|파우더|스틱|오일|워터)\s*(?:제형|텍스처)"
            r"|(?:제형|텍스처)(?:은|는|이|가)\s*.{1,30}(?:형태|타입|구조)"
        ),
        re.compile(r"(?:제품\s*(?:특징|특장점|소개)|\[(?:특징|제품\s*정보)\]|홈케어\s*제품)"),
        re.compile(
            r"(?:두피|피부|모발|구강|관절|영양)\s*전문\s*(?:제품|샴푸|크림|세럼|솔루션)"
            r"|(?:분들|사람|피부|두피)(?:에게|에)\s*(?:적합|권장)(?:한|합니다|됩니다)?"
        ),
    ),
    "usage_instruction": (
        re.compile(r"(?:사용|이용|복용|섭취|보관)\s*(?:방법|방법은|법)\b|주의\s*사항"),
        re.compile(
            r"(?:적당량|적정량|소량)을?\s*(?:덜어|취해|도포|바르|발라|뿌리|넣)"
        ),
        re.compile(
            r"(?:적신|씻은|세안한|흔든|개봉한)\s*후.{0,35}"
            r"(?:도포|바르|마사지|헹구|섭취|복용|사용)"
            r"|(?:도포해|마사지하고|헹궈내는\s*방식|복용하세요|섭취하세요)"
        ),
        re.compile(
            r"사용\s*전에?.{0,30}(?:흔들|세안|확인|세척|제거|준비)(?:어|해|하|하세요|합니다|십시오)"
        ),
    ),
    "benefit_claim": (
        re.compile(
            r"(?:개선|완화|예방|해결)(?:해|하여)?\s*(?:주|줍|주는|도와|돕)"
            r"|(?:도움을\s*(?:줍니다|주는|주며|줘|줄\s*수)|효능이\s*(?:있|뛰어나)|효과가\s*(?:있|좋|뛰어나))"
        ),
        re.compile(
            r"(?:보습|진정|세정|영양|탄력|윤기|광채|장벽|두피|모발|피부|주름|미백)"
            r"(?:을|를|에|이|가|까지|과)?\s*(?:케어|관리|보호|강화|유지|회복|공급|부여|개선|완화|도와|돕)"
        ),
        re.compile(r"(?:건강|청결|촉촉|매끈|부드럽|산뜻)\S{0,8}(?:유지|관리|가꾸|만들어|해\s*주|도와)"),
    ),
    "personal_experience": (
        re.compile(
            r"(?:처음\s*)?(?:사용|써|쓰|먹어|입어|발라|신어|착용)\s*(?:해\s*)?"
            r"(?:보니|보았|보았습니다|봤|본|보고|봤는데|해봤|했더니|했는데|했어요|했습니다|중이|중인|하고\s*있|자마자)"
        ),
        re.compile(
            r"(?:\d+\s*년|몇\s*달|한\s*달|두\s*달|일주일|오래)\s*(?:동안|째|쯤)?\s*"
            r"(?:실\s*)?(?:사용|써|쓰|먹어|복용|착용)(?:한|하고|해|\s*후)?"
        ),
        re.compile(
            r"(?:사용|써|쓰|바른|먹은|입은|신은)\s*후(?:에|에도|에는)?\s*.{0,45}"
            r"(?:만족|느낌|느꼈|좋|나아|편|산뜻|상쾌|달라|변화|아쉽)"
            r"|(?:쓰|사용하)고\s*나서(?:는|부터)?.{0,45}(?:느꼈|좋|나아|줄|덜|달라|변화)"
        ),
        re.compile(r"(?:제가|저는|나는|내가|저한테|제\s*(?:피부|두피)|우리\s*집)\s*.{0,55}(?:사용|써|쓰|먹어|입어|발라|느끼|느꼈|좋|편|만족|아쉽)"),
        re.compile(r"(?:사용감|착용감|발림성|세정력|흡수력)(?:은|이|도|을)?\s*.{0,20}(?:좋|편|부드럽|산뜻|만족|아쉽)"),
        re.compile(
            r"(?:꾸준히|계속|오래|항상|매번)\s*(?:구매|사|사용|쓰)"
            r"|(?:재구매|추가\s*구매|또\s*샀|몇\s*번째\s*(?:구매|사용))"
            r"|(?:잘\s*(?:쓰|사용하|먹))(?:고|는|했|합니다|해요|중)?"
        ),
        re.compile(r"(?:\d+\s*회)\s*(?:직접\s*)?(?:사용|복용|착용)(?:해|했|후|하고)"),
        re.compile(
            r"(?:구매|주문)(?:해\s*)?(?:봤|했|했던|했습니다|했어요|했는데)"
            r"|실제로?\s*(?:받아|써|사용해)\s*보니"
            r"|(?:직접\s*)?경험(?:했|했습니다|해봤)"
        ),
        re.compile(
            r"(?:좋았어요|만족스러(?:웠|워|운|웠습니다)|만족스럽(?:습니다|네요|어요)|마음에\s*들(?:어요|었습니다)|잘\s*산\s*것)"
        ),
    ),
}

HIGH = "HIGH"
MEDIUM = "MEDIUM"
NOT_CANDIDATE = "NOT_CANDIDATE"


@dataclass(frozen=True)
class TextAnalysis:
    """Text-only review hints; never a final review label."""

    matches: dict[str, tuple[str, ...]]

    @property
    def description_signals(self):
        return tuple(name for name in DESCRIPTION_SIGNALS if self.matches.get(name))

    @property
    def has_personal_experience(self):
        return bool(self.matches.get(PERSONAL_EXPERIENCE))

    @property
    def personal_experience_signals(self):
        return self.matches.get(PERSONAL_EXPERIENCE, ())

    @property
    def description_signal_count(self):
        return len(self.description_signals)

    @property
    def personal_experience_signal_count(self):
        return len(self.personal_experience_signals)

    @property
    def candidate_tier(self):
        if self.has_personal_experience or self.description_signal_count < 2:
            return NOT_CANDIDATE
        return HIGH if self.description_signal_count >= 3 else MEDIUM

    @property
    def candidate_reasons(self):
        if self.has_personal_experience:
            return ("명시적인 개인 사용 경험 신호가 있어 high-confidence 후보에서 제외",)
        if self.candidate_tier == HIGH:
            return ("독립적인 설명 신호 3개 이상이며 개인 사용 경험 신호 없음",)
        if self.candidate_tier == MEDIUM:
            return ("독립적인 설명 신호 2개이며 개인 사용 경험 신호 없음",)
        return ("설명 신호가 2개 미만",)

    @property
    def is_shadow_candidate(self):
        return self.candidate_tier in (HIGH, MEDIUM)

    @property
    def is_high_signal(self):
        return self.candidate_tier == HIGH

    @property
    def active_signals(self):
        return tuple(name for name in SIGNAL_ORDER if self.matches.get(name))


@dataclass(frozen=True)
class ScanSummary:
    total_reviews: int
    description_two_plus: int
    shadow_candidates: int
    high_signal_candidates: int
    medium_candidates: int
    signal_counts: Counter
    combination_counts: Counter
    high_signal_rows: tuple[dict, ...]


def _evidence(patterns, text):
    found = []
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            value = match.group(0).strip()
            if value and value not in found:
                found.append(value)
    return tuple(found)


def analyze_text(content):
    """Return explainable signal matches from one raw review body."""
    if not isinstance(content, str) or is_blank(content):
        return TextAnalysis({})
    text = " ".join(content.split())
    matches = {
        name: evidence
        for name, patterns in SIGNAL_PATTERNS.items()
        if (evidence := _evidence(patterns, text))
    }
    return TextAnalysis(matches)


def scan_reviews(frame):
    """Aggregate shadow hints without changing the input dataframe."""
    description_two_plus = shadow_candidates = high_signal_candidates = medium_candidates = 0
    signal_counts = Counter({name: 0 for name in SIGNAL_ORDER})
    combination_counts = Counter()
    high_signal_rows = []

    for values in frame.itertuples(index=True, name=None):
        source_excel_row = values[0]
        row = dict(zip(frame.columns, values[1:]))
        analysis = analyze_text(row.get("content"))
        signal_counts.update(analysis.active_signals)
        if len(analysis.description_signals) >= 2:
            description_two_plus += 1
            combination_counts[analysis.active_signals] += 1
        if analysis.is_shadow_candidate:
            shadow_candidates += 1
        if analysis.is_high_signal:
            high_signal_candidates += 1
            high_signal_rows.append({
                "source_excel_row": source_excel_row,
                "platform": row.get("platform"),
                "product_id": row.get("product_id"),
                "review_id": row.get("review_id"),
                "content": row.get("content"),
                "analysis": analysis,
            })
        elif analysis.candidate_tier == MEDIUM:
            medium_candidates += 1

    high_signal_rows.sort(
        key=lambda row: (-len(row["analysis"].description_signals), row["source_excel_row"])
    )
    return ScanSummary(
        total_reviews=len(frame),
        description_two_plus=description_two_plus,
        shadow_candidates=shadow_candidates,
        high_signal_candidates=high_signal_candidates,
        medium_candidates=medium_candidates,
        signal_counts=signal_counts,
        combination_counts=combination_counts,
        high_signal_rows=tuple(high_signal_rows),
    )


def print_summary(summary, limit):
    print("P_text PRODUCT_DESCRIPTION_REPLACEMENT shadow analysis")
    print("주의: 아래 결과는 사람 검토 후보일 뿐이며 SUSPICIOUS/NORMAL 최종 라벨이 아닙니다.")
    print("행동·네트워크 정보 없이 리뷰 텍스트 신호만 사용했습니다.\n")
    print(f"전체 리뷰 수: {summary.total_reviews}")
    print(f"설명 신호 2개 이상 수: {summary.description_two_plus}")
    print(f"설명 신호 2개 이상 + 개인 경험 없음 수 (shadow candidate): {summary.shadow_candidates}")
    print(f"HIGH (설명 신호 3개 이상 + 개인 경험 없음): {summary.high_signal_candidates}")
    print(f"MEDIUM (설명 신호 2개 + 개인 경험 없음): {summary.medium_candidates}")

    print("\n개별 신호 수:")
    for name in SIGNAL_ORDER:
        print(f"- {name}: {summary.signal_counts[name]}")

    print("\n신호 조합별 수 (설명 신호 2개 이상인 리뷰):")
    if not summary.combination_counts:
        print("- 없음")
    for combination, count in sorted(
        summary.combination_counts.items(), key=lambda item: (-item[1], item[0])
    ):
        print(f"- {' + '.join(combination)}: {count}")

    shown = summary.high_signal_rows[:limit]
    print(f"\nhigh-signal 사람 검토 후보 원문 (최대 {limit}개, 표시 {len(shown)}개):")
    if not shown:
        print("- 없음")
    for number, row in enumerate(shown, start=1):
        analysis = row["analysis"]
        evidence = "; ".join(
            f"{name}={', '.join(analysis.matches[name])}"
            for name in analysis.description_signals
        )
        print(
            f"\n[{number}] source_excel_row={row['source_excel_row']} "
            f"platform={row['platform']} product_id={row['product_id']} review_id={row['review_id']}"
        )
        print(f"signals={', '.join(analysis.description_signals)}")
        print(f"personal_experience={', '.join(analysis.personal_experience_signals) or '없음'}")
        print(f"tier={analysis.candidate_tier}; reason={'; '.join(analysis.candidate_reasons)}")
        print(f"evidence={evidence}")
        print("content:")
        print(row["content"])


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="설명문 대체 가능성을 텍스트만으로 넓게 찾는 사람 검토용 shadow analysis"
    )
    parser.add_argument(
        "excel_path",
        nargs="?",
        type=Path,
        default=PROJECT_ROOT / "outputs" / "merged_reviews.xlsx",
        help="읽기 전용 입력 Excel (기본: outputs/merged_reviews.xlsx)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="콘솔에 표시할 high-signal 원문 최대 수 (기본: 20)",
    )
    args = parser.parse_args(argv)
    if args.limit < 0:
        parser.error("--limit은 0 이상이어야 합니다.")
    return args


def main(argv=None):
    # Windows legacy console encodings cannot represent every emoji or symbol
    # found in raw reviews.  Preserve a readable escaped form instead of
    # aborting the read-only scan midway through its console preview.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")
    args = parse_args(argv)
    source = args.excel_path.expanduser()
    if not source.is_absolute():
        source = PROJECT_ROOT / source
    source = source.resolve()
    try:
        frame, _, _, _ = read_reviews(source)
        summary = scan_reviews(frame)
        print_summary(summary, args.limit)
    except PermissionError as exc:
        print(f"오류: 입력 Excel 접근 권한을 확인해주세요. {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"오류: shadow analysis를 완료하지 못했습니다. {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
