from scripts import ptext_pilot_near_duplicates as near


def test_normalization_is_comparison_only_and_deterministic():
    source = "ＡBC   테스트\n문장"
    assert near.normalize_for_near_duplicate(source) == "abc 테스트 문장"
    assert source == "ＡBC   테스트\n문장"


def test_lsh_produces_candidates_but_never_decisions():
    documents = {
        "a": "배송 후 사용해 보니 손잡이가 단단하고 세척이 쉬웠습니다",
        "b": "배송 후 사용해보니 손잡이가 단단하고 세척이 쉬웠습니다",
        "c": "전혀 관련 없는 짧은 합성 문장입니다",
    }
    pairs = near.lsh_candidate_pairs(documents, seed=20261108)
    assert ("a", "b") in pairs
    scored = near.score_candidate_pairs(documents, pairs)
    assert all(row["decision"] == "UNREVIEWED" for row in scored)
    assert near.policy_contract()["exclusion_threshold"] is None
    assert near.policy_contract()["status"] == "CANDIDATE_GENERATION_ONLY"


def test_candidate_generation_is_input_order_independent():
    first = {"a": "가나다라마바사아자차", "b": "가나다라마바사아자카", "c": "별도 문장"}
    second = dict(reversed(list(first.items())))
    assert near.lsh_candidate_pairs(first, seed=7) == near.lsh_candidate_pairs(second, seed=7)


def test_blocking_prevents_cross_block_candidates_and_empty_text_buckets():
    documents = {"a": "동일한 합성 문장", "b": "동일한 합성 문장", "empty": "   "}
    blocks = {"a": "short-ko", "b": "long-ko", "empty": "short-ko"}
    assert near.lsh_candidate_pairs(documents, seed=7, blocks=blocks) == set()


def test_jaccard_diagnostic_boundaries():
    assert near.jaccard_similarity(set(), set()) == 1.0
    assert near.jaccard_similarity({"a"}, set()) == 0.0
    assert near.jaccard_similarity({"a", "b"}, {"b", "c"}) == 1 / 3

