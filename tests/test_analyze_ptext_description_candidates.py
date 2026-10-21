"""Pure text tests: no real review workbook is opened or changed."""

from pathlib import Path
import sys

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import analyze_ptext_description_candidates as shadow


def test_two_description_signals_without_experience_is_candidate():
    result = shadow.analyze_text(
        "병풀 추출물을 함유한 진정 크림 제품입니다. 민감한 피부 장벽 관리에 도움을 줍니다."
    )
    assert len(result.description_signals) >= 2
    assert not result.has_personal_experience
    assert result.is_shadow_candidate
    assert result.candidate_tier == shadow.MEDIUM


def test_three_description_signals_without_experience_is_high_signal():
    result = shadow.analyze_text(
        "히알루론산 성분을 포함한 보습 세럼 제품입니다. "
        "세안 후 적당량을 덜어 얼굴에 도포하세요. 피부 보습 유지에 도움을 줍니다."
    )
    assert len(result.description_signals) >= 3
    assert result.is_shadow_candidate
    assert result.is_high_signal
    assert result.candidate_tier == shadow.HIGH


def test_known_description_replacement_shape_is_high_signal():
    result = shadow.analyze_text(
        "이 샴푸는 발효식초와 인삼을 포함한 21종 이상의 핵심 성분이 어우러진 두피 전문 샴푸입니다. "
        "두피 고민 해결에 도움을 주며, 모발과 두피를 충분히 적신 후 적당량을 도포하고 "
        "마사지한 뒤 깨끗이 헹궈내는 방식으로 사용합니다."
    )
    assert result.description_signals == shadow.DESCRIPTION_SIGNALS
    assert not result.has_personal_experience
    assert result.is_high_signal


def test_description_signals_with_direct_experience_are_excluded():
    result = shadow.analyze_text(
        "세라마이드 성분을 함유한 장벽 크림 제품입니다. 피부 보습 관리에 도움을 줍니다. "
        "제가 일주일 동안 사용해 보니 발림성이 좋았어요."
    )
    assert len(result.description_signals) >= 2
    assert result.has_personal_experience
    assert not result.is_shadow_candidate
    assert not result.is_high_signal
    assert result.candidate_tier == shadow.NOT_CANDIDATE


def test_ordinary_natural_review_is_excluded():
    result = shadow.analyze_text("일주일 써보니 향이 은은하고 머리가 덜 가려워서 잘 쓰고 있어요.")
    assert result.has_personal_experience
    assert not result.is_shadow_candidate
    assert not result.is_high_signal


@pytest.mark.parametrize("content", [None, "", " \n ", 123])
def test_blank_or_non_text_content_is_excluded(content):
    result = shadow.analyze_text(content)
    assert result.active_signals == ()
    assert not result.is_shadow_candidate
    assert not result.is_high_signal


def test_explicit_no_use_is_not_direct_experience():
    result = shadow.analyze_text(
        "아직 사용해 보지 못했지만 병풀 성분을 함유한 진정 크림 제품입니다. "
        "피부 장벽 관리에 도움을 줍니다."
    )
    assert not result.has_personal_experience
    assert result.is_shadow_candidate


@pytest.mark.parametrize("experience", [
    "사용 후에도 산뜻한 느낌이 오래 유지되어 만족스러워요.",
    "처음 쓰자마자 만족했고 이 제품을 쓰고 나서는 가려움이 덜해졌어요.",
    "면세점에서 꾸준히 구매해서 사용중인 제품입니다.",
    "1회 직접 사용 후 시원함을 느꼈어요.",
    "2년 실사용 후 남기는 솔직 후기이며 쓸 때마다 만족했어요.",
    "제품을 사용해 보았습니다. 실제로 변화를 경험했습니다.",
    "주문해봤는데 실제 받아보니 좋았어요. 지금도 사용 중이에요.",
])
def test_strong_personal_experience_demotes_description_copy(experience):
    result = shadow.analyze_text(
        "병풀 추출물을 함유한 젤 제형 제품으로 피부 진정 관리에 도움을 줍니다. "
        "적당량을 덜어 도포하세요. " + experience
    )
    assert result.description_signal_count >= 3
    assert result.has_personal_experience
    assert result.candidate_tier == shadow.NOT_CANDIDATE


def test_use_before_instruction_is_not_personal_experience():
    result = shadow.analyze_text(
        "히알루론산 성분을 함유한 워터 제형입니다. 사용 전에 충분히 흔들어 주세요. "
        "피부 보습 유지에 도움을 줍니다."
    )
    assert "usage_instruction" in result.description_signals
    assert not result.has_personal_experience
    assert result.candidate_tier == shadow.HIGH


def test_before_after_actual_experience_is_personal():
    result = shadow.analyze_text(
        "세라마이드 성분을 함유한 크림 제형으로 피부 장벽 관리에 도움을 줍니다. "
        "사용 전에는 건조했는데 한 달 사용 후 많이 좋아졌어요."
    )
    assert result.has_personal_experience
    assert result.candidate_tier == shadow.NOT_CANDIDATE


@pytest.mark.parametrize("experience", [
    "체험단으로 제품을 받아 일주일 사용해봤어요.",
    "제품을 협찬받아 직접 사용해봤습니다.",
    "직접 구매해서 한 달 사용해보니 만족스러웠어요.",
    "어제 배송받고 바로 사용해봤는데 괜찮아요.",
    "2주 동안 복용해보니 전보다 편한 느낌이에요.",
    "직접 입어보니 생각보다 핏이 편했어요.",
    "한 달 실사용 후기입니다. 꾸준히 써보니 만족해요.",
])
def test_v2_personal_experience_categories_demote_description_copy(experience):
    result = shadow.analyze_text(
        "병풀 추출물을 함유한 젤 제형 제품으로 피부 진정 관리에 도움을 줍니다. "
        "적당량을 덜어 도포하세요. " + experience
    )
    assert result.description_signal_count >= 3
    assert result.has_personal_experience
    assert result.candidate_tier == shadow.NOT_CANDIDATE


@pytest.mark.parametrize("instruction", [
    "사용 후 충분히 씻어내세요.",
    "하루 한 번 복용하세요.",
    "세안 후 얼굴에 골고루 발라주세요.",
    "구매 전 반드시 사이즈를 확인하세요.",
    "배송 가능 지역을 확인하세요.",
])
def test_v2_instructions_are_not_personal_experience(instruction):
    result = shadow.analyze_text(instruction)
    assert not result.has_personal_experience


@pytest.mark.parametrize("content", [
    # NEW-DESC-000005 regression shape
    "[협찬] 체험단으로 사용해보게 되었습니다. 1450ppm 함량으로 충치 예방에 도움을 줍니다.",
    # NEW-DESC-000026 regression shape
    "올영체험단으로 트리트먼트를 써보게되었어요. 사용하면서 온열감이 느껴졌어요.",
    # NEW-DESC-000047 regression shape
    "두피 케어에 도움을 주는 샴푸 실사용 후기입니다. 감고 나면 모발이 부드러워져요.",
])
def test_v2_observed_candidate_regressions_have_personal_evidence(content):
    result = shadow.analyze_text(content)
    assert result.has_personal_experience


@pytest.mark.parametrize("content", [
    "한 달 정도 사용하면서 느낀 건 입술이 덜 건조해졌다는 점이에요.",
    "예전에 썼었는데 제법 촉촉하고 괜찮았어요.",
    "알약 크기가 작아서 먹기 편했고 꾸준히 챙기고 있습니다.",
    "꾸준히 먹다 보니 피부가 맑아지는 느낌이 들더라고요.",
    "올영 한정 컬러라 구매함.",
    "구매 후기 리뷰를 남깁니다.",
    "올리브영에서 테스터 사용 후 구매한 핸드크림입니다.",
])
def test_v2_additional_observed_experience_phrases_are_personal(content):
    result = shadow.analyze_text(content)
    assert result.has_personal_experience


@pytest.mark.parametrize("content", [
    "사용 후 머릿결이 정말 매끄러워져요.",
    "전 샤워캡을 쓰고 방치했는데 더 효과 있다고 느꼈어요.",
    "펌프형이라 한 손으로 쓰기 편하더라고요.",
    "손상모라서 이 기획으로 골랐는데 용량이 넉넉하네요.",
])
def test_v2_observed_results_and_first_person_shorthand_are_personal(content):
    result = shadow.analyze_text(content)
    assert result.has_personal_experience


@pytest.mark.parametrize("content", [
    "매일 사용하기 적합한 제품입니다.",
    "꾸준히 먹으면 건강 관리에 도움을 줄 수 있습니다.",
    "사용하면서 보관 방법을 확인하세요.",
])
def test_v2_generic_usage_copy_is_not_personal_experience(content):
    result = shadow.analyze_text(content)
    assert not result.has_personal_experience


def test_generic_description_words_alone_are_not_description_evidence():
    result = shadow.analyze_text("좋은 제품입니다. 기능과 효과가 좋고 고민 해결에 추천합니다.")
    assert result.description_signal_count < 2
    assert result.candidate_tier == shadow.NOT_CANDIDATE


def test_negative_limit_is_rejected():
    with pytest.raises(SystemExit):
        shadow.parse_args(["--limit", "-1"])


def test_scan_counts_candidates_and_signal_combinations():
    frame = pd.DataFrame(
        {
            "platform": ["shop", "shop", "shop"],
            "product_id": [1, 2, 3],
            "review_id": [11, 12, 13],
            "content": [
                "병풀 성분을 함유한 진정 크림 제품입니다. 피부 장벽 관리에 도움을 줍니다.",
                "히알루론산 성분을 포함한 보습 세럼 제품입니다. 적당량을 덜어 도포하세요.",
                "일주일 써보니 순하고 좋아요.",
            ],
        },
        index=pd.Index([10, 11, 12], name="source_excel_row"),
    )
    summary = shadow.scan_reviews(frame)
    assert summary.total_reviews == 3
    assert summary.description_two_plus == 2
    assert summary.shadow_candidates == 2
    assert summary.high_signal_candidates == 0
    assert summary.medium_candidates == 2
    assert len(summary.high_signal_rows) == 0
    assert sum(summary.combination_counts.values()) == 2
