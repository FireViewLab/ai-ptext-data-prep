"""Deterministic, compositional synthetic augmentation, explicitly not real evidence.

Product anchors come from source text, never the platform. No factual efficacy or
ingredient claims in these generated texts have been verified. They are artificial
challenge examples, not proof that similar real reviews are fraudulent.
"""

import random
import re


TYPES = (
    "PRODUCT_DESCRIPTION_REPLACEMENT", "NO_USE_ASSERTIVE_RECOMMENDATION",
    "PROMOTIONAL_TEMPLATE", "EXPERIENCE_FREE_CLAIM", "COPY_VARIATION",
)
# Product nouns, tasks and attributes must actually occur in the parent review.
ANCHORS = (
    "마스크팩", "샴푸", "트리트먼트", "클렌저", "클렌징", "선크림", "크림", "세럼",
    "로션", "립스틱", "틴트", "립밤", "쿠션", "파운데이션", "에센스", "패드",
    "스퀴지", "청소솔", "브러쉬", "브러시", "청소도구", "청소용품", "샤워기",
    "변기솔", "수세미", "밀대", "걸레", "세제", "수납장", "수납함", "선반",
    "조명", "스탠드", "전구", "무드등", "의자", "책상", "커튼", "이불", "베개",
    "수건", "매트", "테이블", "소파", "티셔츠", "셔츠", "바지", "운동화",
    "신발", "가방", "청소", "세정", "보습", "두피", "피부", "발색", "착용",
    "욕실", "화장실", "주방", "침실", "거실", "수납", "조립", "세탁",
    "디자인", "재질", "색상", "크기", "향", "제품",
)
ATTRIBUTES = (
    "보습", "세정", "발색", "지속력", "흡수", "사용감", "탄력", "두피", "피부결",
    "청소", "물기", "먼지", "손잡이", "수납", "설치", "밝기", "착용감", "사이즈",
    "내구성", "재질", "디자인", "색상", "관리", "구성", "향", "편리", "가성비",
)
QUALITY = ("완성도", "품질", "구성", "활용도", "실용성", "가치", "편의성", "만족도")
ADVANTAGES = ("안정적인", "균형 잡힌", "탄탄한", "군더더기 없는", "실속 있는", "간결한", "효율적인", "높은")
AUDIENCE = ("일상의 번거로움을 줄이고 싶은", "하나로 간단히 해결하고 싶은", "실용성을 우선하는",
            "선택에 시간을 쓰고 싶지 않은", "부담 없이 시작하려는", "완성도를 중요하게 보는",
            "기본에 충실한 구성을 찾는", "편리한 관리를 원하는")
CERTAINTY = ("분명하게 보장", "예외 없이 충족", "틀림없이 제공", "확실하게 구현", "언제나 유지", "빠짐없이 실현")
NO_USE = ("아직 직접 사용해 보지는 않았지만", "개봉 전이라 써 본 상태는 아닌데",
          "직접 써보기 전인 지금도", "아직 실사용은 하지 않았어요. 그렇지만",
          "받아놓고 사용은 미뤄둔 상태지만", "실제로 시험해 본 적은 없지만",
          "사용 전이라는 점부터 밝히자면", "아직 첫 사용도 안 했는데도",
          "직접 확인은 못 한 상태예요. 그래도", "실사용 기록은 아직 없지만")
INVITATIONS = ("망설이지 말고 선택해 보세요", "찾고 있었다면 이번에 구매해 보세요",
               "주변에도 알려두세요", "고민하던 분들은 바로 골라도 됩니다",
               "장바구니에 담아둘 만합니다", "선택을 미룰 이유가 없습니다",
               "필요한 분들께 적극 권해요", "다른 걸 찾기 전에 이것부터 살펴보세요",
               "이번 선택으로 정착해 보세요", "구입을 결정해도 후회 없을 거예요",
               "지금 준비해 두길 권합니다", "한 번 선택해 보시길 바라요")


def context(parent):
    raw = parent["content"]
    nouns = [word for word in ANCHORS if word in raw]
    attributes = [word for word in ATTRIBUTES if word in raw]
    return (nouns or ["제품"]), (attributes or ["구성", "활용도"])


def sentence(rng, stem):
    # Different registers and punctuation; no platform names or reason codes.
    last = ord(stem[-1])
    consonant = 0xAC00 <= last <= 0xD7A3 and (last - 0xAC00) % 28 != 0
    casual = "이에요" if consonant else "예요"
    explanatory = "이라는 점." if consonant else "라는 점."
    return stem + rng.choice(("입니다.", casual + ".", "이네요" if consonant else "네요",
                              "입니다!", casual + "~", "임", explanatory))


def compose(parent, kind, rng):
    nouns, attributes = context(parent)
    anchor = rng.choice(nouns[:max(1, min(5, len(nouns)))])
    attribute = rng.choice(attributes)
    quality = rng.choice(QUALITY)
    advantage = rng.choice(ADVANTAGES)
    audience = rng.choice(AUDIENCE)
    # Build phrases rather than substitute a product name into a few sentences.
    subject = rng.choice((f"{anchor} 관련 구성을 보면", f"{anchor} 선택의 기준은",
                          f"{anchor} 쪽에서 눈여겨볼 부분은", "구성의 핵심은",
                          f"{anchor}, 핵심만 정리하면", "이 제품에서 주목할 점은"))
    description = sentence(rng, f"{subject} {attribute} 중심의 {advantage} {quality}")
    target = sentence(rng, f"{audience} 분들을 위한 {rng.choice(('구성', '선택지', '제품', '설계'))}")
    function = rng.choice((
        f"{attribute} 기능에 초점을 맞춰 필요한 부분을 간단하게 관리하도록 구성되어 있어요.",
        f"주요 특징은 {attribute}. 여기에 {quality}까지 함께 고려한 구성이죠.",
        f"{attribute} 중심으로 사용 목적을 정리하고, {quality} 측면까지 연결한 형태입니다.",
        f"사용 방법은 필요한 상황에 맞춰 적용하는 방식이며 {attribute} 관리에 적합합니다.",
        f"{quality} 중심의 설계로 {attribute} 관련 요구를 함께 다루도록 만들었습니다.",
    ))
    claim = rng.choice((
        f"{attribute} 면에서는 필요한 결과를 {rng.choice(CERTAINTY)}합니다.",
        f"조건이 달라져도 {quality}에는 차이가 없고 결과는 확실해요.",
        f"누가 선택하든 {attribute} 관련 걱정은 남지 않습니다.",
        f"{quality} 하나는 비교가 필요 없을 만큼 분명합니다.",
        f"{attribute}에 관한 기대는 반드시 채워지는 선택이에요.",
        f"다른 조건을 따질 필요 없이 {quality}만큼은 믿어도 됩니다.",
        f"{attribute} 측면에서 실패할 가능성은 없다고 볼 수 있어요.",
        f"어떤 상황에서도 {quality}가 떨어질 이유는 없습니다.",
    ))
    promotion = sentence(rng, f"{rng.choice(('가격부터 구성까지', '선택의 기준을 모아 보면', '여러 면을 함께 따지면', '전체적인 균형을 보면'))} {advantage} {quality}")
    generic = rng.choice((
        "품질, 가격, 편의성을 함께 챙길 수 있는 선택입니다.",
        "기대하는 기본은 모두 갖췄고 만족도까지 놓치지 않았어요.",
        "구성은 알차고 가격은 합리적이라 누구에게나 잘 맞아요.",
        "고민할 필요 없이 실속과 만족을 한 번에 챙길 수 있어요.",
        "첫 선택부터 좋은 인상을 남길 만한 완성도입니다.",
        "편의성과 품질을 두루 갖췄으니 비교할수록 돋보입니다.",
        "일상에 필요한 가치를 한데 모았다는 점이 매력입니다.",
        "누구나 부담 없이 선택할 수 있고 기대까지 채워줍니다.",
    ))
    invite = rng.choice(INVITATIONS) + rng.choice((".", "!", "~", " :)", ""))
    if kind == TYPES[0]:
        clauses = [description, target, function]
        rng.shuffle(clauses)
        clauses = clauses[:rng.choice((2, 3))]
    elif kind == TYPES[1]:
        clauses = [rng.choice(NO_USE) + " " + claim, invite]
        if rng.random() < .45:
            clauses.insert(1, description)
    elif kind == TYPES[2] or kind == TYPES[4]:
        clauses = [promotion, generic, invite]
        if rng.random() < .5:
            clauses.append(sentence(rng, f"{anchor} 쪽에서도 {advantage} 선택"))
        rng.shuffle(clauses)
    else:
        clauses = [claim, description]
        if rng.random() < .5:
            clauses.append(target)
        rng.shuffle(clauses)
    # Vary passage length with source context instead of a fixed sentence count.
    if kind in (TYPES[0], TYPES[3]) and len(parent["content"]) > 180:
        for extra_attribute in rng.sample(attributes, min(len(attributes), rng.randint(1, 3))):
            clauses.append(rng.choice((
                f"{extra_attribute} 관련 부분까지 함께 고려한 구성이어서 별도의 복잡한 조건을 따질 필요가 없습니다.",
                f"선택할 때 확인할 항목은 {extra_attribute}입니다. 필요한 목적에 맞춰 적용할 수 있도록 구성한 점이 특징이에요.",
                f"{extra_attribute} 중심으로 기본 구성을 살펴보면 어떤 부분에 무게를 두었는지 알 수 있습니다. 관리가 간단하다는 점도 핵심입니다.",
            )))
    elif kind == TYPES[3] and rng.random() < .3:
        clauses = [claim]
    return rng.choice((" ", "\n", "\n\n", " / ")).join(clauses)


def generate(parents, count=1350, seed=42):
    """Return synthetic rows; COPY_VARIATION siblings share an explicit family."""
    if count < 0 or (count and not parents):
        raise ValueError("synthetic 수는 음수일 수 없고, 생성에는 실제 부모 리뷰가 필요합니다.")
    rng = random.Random(seed)
    pool = sorted(parents, key=lambda row: row["source_excel_row"])
    rng.shuffle(pool)
    output, seen = [], {row["content"] for row in parents}
    for type_index, kind in enumerate(TYPES):
        target = count // len(TYPES) + (type_index < count % len(TYPES))
        prototype = None
        parent = None
        family = None
        for index in range(target):
            if kind != TYPES[4] or index % 3 == 0:
                parent = pool[(len(output) + index) % len(pool)]
                family = f"family-{seed}-{type_index}-{index:05d}"
                prototype = None
            for attempt in range(200):
                if kind == TYPES[4] and prototype is not None and attempt == 0:
                    clauses = re.split(r"(?<=[.!])\s+|\n+| / ", prototype)
                    clauses = [clause for clause in clauses if clause]
                    rng.shuffle(clauses)
                    content = " ".join(clauses).replace("선택", "선택지").replace("있어요", "있습니다")
                elif kind == TYPES[4] and prototype is not None:
                    content = prototype.replace(".", rng.choice(("!", "~", " :)")), 1)
                    content = content + " " + rng.choice(INVITATIONS)
                else:
                    content = compose(parent, kind, rng)
                if content not in seen:
                    break
            else:
                raise ValueError("고유 synthetic 생성 한도를 초과했습니다.")
            if kind == TYPES[4] and prototype is None:
                prototype = content
            seen.add(content)
            output.append({
                "platform": parent["platform"], "product_id": parent["product_id"],
                "review_id": f"synthetic-{seed}-{type_index}-{index:05d}", "content": content,
                "label": "SUSPICIOUS", "label_origin": "synthetic", "synthetic_type": kind,
                "parent_review_id": parent["review_id"], "parent_source_excel_row": parent["source_excel_row"],
                "source_excel_row": None, "synthetic_family_id": family,
                "generation_method": "contextual_compositional_v1", "seed": seed,
            })
    return output
