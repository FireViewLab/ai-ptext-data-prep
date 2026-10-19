# New review product-description candidates

이 결과는 사람이 검토할 HIGH/MEDIUM 후보 pool입니다. HIGH/MEDIUM은 SUSPICIOUS/NORMAL 라벨이 아니며 자동 라벨링을 수행하지 않았습니다.

## Execution

- Pilot: 플랫폼당 최대 5,000행, 총 26,286행, 성공
- Full scan: 1,151,943행
- 실행시간: 81.63초
- malformed rows: 0
- CSV streaming 방식이며 NOT_CANDIDATE 본문은 보관하지 않았습니다.

## Candidate counts

| tier | raw rows | unique normalized contents |
| --- | ---: | ---: |
| HIGH | 67 | 56 |
| MEDIUM | 551 | 518 |
| NOT_CANDIDATE | 1,151,325 | 저장하지 않음 |

최종 human-review pool은 normalized content 기준 574건입니다.

## Platform distribution

| platform | raw rows | HIGH | HIGH ratio | MEDIUM | MEDIUM ratio |
| --- | ---: | ---: | ---: | ---: | ---: |
| elevenst | 171,052 | 3 | 0.001754% | 62 | 0.036246% |
| kurly | 463,843 | 0 | 0.000000% | 7 | 0.001509% |
| musinsa | 118,192 | 0 | 0.000000% | 16 | 0.013537% |
| naver | 1,286 | 0 | 0.000000% | 0 | 0.000000% |
| ohouse | 6,828 | 0 | 0.000000% | 0 | 0.000000% |
| oliveyoung | 390,742 | 64 | 0.016379% | 466 | 0.119260% |

후보 비율은 플랫폼 문체와 상품군의 영향을 받을 수 있으며 suspicious prevalence가 아닙니다.

## Baseline normalized-content overlap

| tier | raw overlap rows | raw new-content rows | unique overlap | unique new content |
| --- | ---: | ---: | ---: | ---: |
| HIGH | 0 | 67 | 0 | 56 |
| MEDIUM | 0 | 551 | 0 | 518 |

Baseline overlap은 diagnostic이며 후보에서 제거하지 않았습니다.

## Description evidence distribution

| tier | signal | raw rows | unique contents |
| --- | --- | ---: | ---: |
| HIGH | ingredient_or_spec | 61 | 52 |
| HIGH | product_description | 59 | 48 |
| HIGH | usage_instruction | 24 | 20 |
| HIGH | benefit_claim | 58 | 49 |
| MEDIUM | ingredient_or_spec | 436 | 410 |
| MEDIUM | product_description | 244 | 228 |
| MEDIUM | usage_instruction | 76 | 73 |
| MEDIUM | benefit_claim | 346 | 325 |

## Personal-experience sanity check

- HIGH/MEDIUM raw rows with personal signal: 0
- Unique candidates with personal signal: 0
- 현재 analyzer 정책상 명시적 personal evidence가 있으면 NOT_CANDIDATE입니다.

## Deterministic diagnostic samples

Stable content SHA-256 순으로 tier별 최대 100건입니다. 이는 human label이나 정식 precision 측정이 아닙니다.

### HIGH — 56건

- `NEW-DESC-000004` / hash `009f9e8516f5cfce` / oliveyoung / product `A000000261234` / review `65865339`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: 피부 진정이랑 장벽 케어가 필요할 때 바르기 아주 딱 좋은 크림임 적당히 수분감 있으면서 영양감 있게 마무리되는 제형이라 피부에 펴 바르면 답답함 없이 부드럽게 스며듬 센텔라 성분이 들어있어서 붉은 기나 민감해진 자극을 순하게 다독여주고 속건조까지 잘 잡아줌 100ml 대용량에 미니 크림이랑 토너 샘플까지 알차게 구성되어 있어 여행 갈 때 챙겨 다니기도 너무 좋음
- `NEW-DESC-000005` / hash `00d256c639ffb287` / oliveyoung / product `A000000260948` / review `65848693`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: [협찬] 평소 충치 예방에 관심이 많아 고불소 치약을 알아보던 중, 믿을 수 있는 동아제약에서 나온 &#039;듀오버스터 맥스프레시&#039;를 체험단으로 사용해보게 되었습니다. 1450ppm의 고불소 함량이라 강력한 충치 예방 효과를 기대하며 선택했습니다. ​제품 특징 ​1450ppm 고불소 함량: 시중의 일반 치약보다 불소 함량이 높아 강력한 충치 예방과 치아 불소 막 형성에 도움을 줍니다 ​듀얼 액션 포뮬러: 충치 예방뿐
- `NEW-DESC-000006` / hash `02a1dc3b850330f0` / oliveyoung / product `A000000218630` / review `25875216`
  - signals: ingredient_or_spec, usage_instruction, benefit_claim
  - snippet: 그라펜 해수 컬크림은 제주 해수를 함유한 컬링 크림으로, 컬을 오랫동안 유지시켜 주고, 곱슬기를 잡아주는 효과가 있어요! 머릿결에 도움이 되는 영양 성분을 함유하여 손상된 모발을 복구하고, 윤기를 더해줘요~ 그라펜 해수 컬크림 사용 방법은 샴푸 후 젖은 모발에 적당량을 덜어 손으로 골고루 펴 발라준 후, 드라이어로 컬을 잡아주면 되요~ 컬을 잡아준 후에도 컬이 풀어지지 않도록 컬크림을 다시 한 번 발라주면 더욱 효과적이에요~ 
- `NEW-DESC-000007` / hash `067fe94443c3fa7d` / oliveyoung / product `A000000204495` / review `37406493`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: **나르카 젠틀 새틴 헤어 에센스 (70ml)**는 머리카락에 부드러운 윤기를 부여하고 손상된 모발을 케어하는 고급 헤어 에센스입니다. ### ✅ **제품 특징** - **주요 성분**: - **아르간 오일**: 모발에 영양을 공급하고 윤기를 더해줌 - **시어버터**: 보습 효과로 머리카락을 부드럽고 건강하게 유지 - **비타민 E**: 머리카락의 손상을 방지하고 건강한 상태 유지 - **효능**: - 엉킴 방지 및 부드러운
- `NEW-DESC-000008` / hash `0732d625f36d9744` / oliveyoung / product `A000000217511` / review `67360828`
  - signals: ingredient_or_spec, product_description, usage_instruction
  - snippet: 휩드에서 나온 130g 용량의 팩클렌저 기획 상품으로, 이번 옵션은 무화버터 타입과 클렌징밤이 함께 구성된 제품입니다. 본품 하나만 들어 있는 단품과 달리 추가 구성품을 함께 받아볼 수 있어 여러 제품을 한 번에 준비하고 싶은 경우 편리합니다. 130g 용량은 화장대나 욕실 주변에 두고 사용하기에 부담이 크지 않고, 필요한 만큼 덜어 사용할 수 있어 관리하기에도 무난한 편입니다. 이번 상품은 무화버터, 머그트리, 피치페어, 유
- `NEW-DESC-000009` / hash `1082de62eb4a64b6` / oliveyoung / product `A000000260749` / review `66425871`
  - signals: ingredient_or_spec, usage_instruction, benefit_claim
  - snippet: 평소 입술이 건조하면 각질도 잘 올라오고 금방 푸석해 보여서 립케어 제품을 자주 사용하는 편인데, 큐온립 크림은 부드럽게 발리면서 촉촉하게 보습감을 채워주는 느낌이라 마음에 들었어요. 크림 타입이라 입술에 얇게 펴 바르기 좋고, 자기 전에 조금 도톰하게 발라주면 다음 날 입술이 한결 매끈하고 촉촉하게 느껴졌어요. 특히 각질이 올라온 날 사용하면 입술이 거칠게 느껴지는 게 덜해서 요즘은 잠들기 전에 꼭 챙겨 바르고 있어요. 한 
- `NEW-DESC-000010` / hash `150e6ef8118c066a` / oliveyoung / product `A000000171735` / review `35990243`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: 모발 영양에 도움을 주는 아미노산 17종과 단백질 3종이 함유된 앰플을 젖은 모발에 도포하면 앰플이 크림 제형으로 변하면서 히팅효과와 모발코팅 효과를 줍니다. 트리셀 샴푸도 꽤나만족하면서 예전에 썼었는데 트리트먼트도 잠깐 부드럽다마는 어설픈 제형이 아니라 제법 촉촉하고 미끈미끈하네요 모발날림없이 차분하게 정돈되는편 워터중 효과는 괜찮은듯♡
- `NEW-DESC-000011` / hash `2bf43ae68d5970b6` / oliveyoung / product `A000000114415` / review `11732291`
  - signals: ingredient_or_spec, usage_instruction, benefit_claim
  - snippet: 오일성분이 없고 끈적입 없는 가벼운 헤어스프레이를 원하는 사람한텐 강추하는 헤어미스트에요 머리를 다 말린후에 뿌려주면 되는데 뿌리고나면 끈적임 없이 흡수되어 이 미스트로 인한 떡짐현상 전혀없구요 은은한 허브향이 기분좋게 만들어줘요 안개분사라 뭉침없이 골고루 뿌려져서 완전 맘에들었어요! 그리고 들고다기 좋게 사이즈도 적당하고 무게도 가벼워요 다만 탄력 강화는 모르겠더라구요 수분공급도 지속적으로 분사해주지 않는이상은 일시적인거같아
- `NEW-DESC-000012` / hash `31ad7ce2449a2bbc` / oliveyoung / product `A000000201277` / review `64428023`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: 1000ml의 엄청난 대용량 가성비에 두피 브러시까지 세트로 구성되어 있어 온 가족이 쓰기 최고인 탈모 완화 샴푸입니다. 거품이 조밀하고 풍성하게 잘 나며 머리를 감고 나면 두피가 시원하고 개운해지는 느낌을 줍니다. 샴푸 단독 사용 시 손상모발 개선 면에서는 트리트먼트를 꼭 함께 써줘야 부드러움이 유지된다는 점이 있습니다.
- `NEW-DESC-000013` / hash `3b67e155927284f5` / oliveyoung / product `A000000238929` / review `19964450`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: 믿고 쓰는 차앤박 스킨케어 제품!! 일단 구성이 너무 좋구요 크림이 총 100ml!! 크림 제형은 쫀쫀하고 불투명한 색상이에요 피부에 수면팩 하는거처럼 올라가는데 금방 흡수되고 보습력이 너무 좋아요 &gt;.&lt;!! 피부 장벽 케어에 좋을거 같아요🤩!!!
- `NEW-DESC-000014` / hash `42e7507b6b1d74ca` / oliveyoung / product `A000000259685` / review `65158096`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: 모링가 추출물과 비니거가 함유된 산뜻한 워터 제형이 건강한 모발을 위한 ph 밸런스를 맞추고 각질층을 정돈하여 건강한 두피 모발을 케어해 주는 제품이에요.
- `NEW-DESC-000015` / hash `4a9605ccf5f8e62a` / oliveyoung / product `A000000206683` / review `67341875`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: 바디 트러블의 근본적인 원인을 케어하여 매끄럽고 청정한 피부 결을 완성해 주는 일리윤 시카 아크네 바디워시 대용량 제품에 대한 상세 리뷰입니다. 등과 가슴 부위에 빈번하게 발생하는 바디 트러블, 일명 &#039;등드름&#039;과 &#039;가슴드름&#039;은 얼굴보다 두꺼운 바디 피부의 모공 속에 과잉 피지와 묵은 각질이 원활하게 배출되지 못해 발생합니다. 이 제품은 여드름성 피부 완화 기능성을 인증받은 바디워시로, BHA
- `NEW-DESC-000016` / hash `4b3c057c64fd126d` / oliveyoung / product `A000000172040` / review `15747304`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: ♡구매이유♡ 나이가 드니 염증이 잘생기는 피부타입으로 변해서 유분기많거나 아무거나 잘못쓰면 바로 피부트러블이올라와서 후기보고 구매한제품이에요. ♡가격♡ 50ml+31ml 구성이라 2만원대 초반이면 괜찮은거 같아요. ♡상품♡ 짜서 쓸수있는 타입이라 위생적이라 좋아요. 인텐카(병풀성분에서 핵심적인 성분을 추출해서 특허공법으로 만든)성분10000ppm이 들어 있어서 시카성분의 2~3배의 진정효과가 있다고 해요. ♡사용후기)♡ 일단 
- `NEW-DESC-000017` / hash `4ed734f3ef131f7c` / oliveyoung / product `A000000209948` / review `46307857`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: 머리스타일링을 자주 하는데 요즘같이 덥고 습한날은 밖에 나가면 금방 머리가 풀리더라고요. 그럴때 사용하면 좋은 컬링 에센스에요. 디자인이나 패키지도 깔끔해서 선물용으로도 좋을것 같더라고요. 처음 스타일링 그대로 고정되어 있어서 컬도 안풀리고 지속력이 오래가서 너무 맘에 들어요. 수분감을 듬뿍 담은 제형으로 촉촉해서 머릿결이 윤기있고 뷰드러우면서 수분을 채워줘서 볼륨감도 있어요. 프로틴 블룸 2X로 식물설 모발 유사 단백질과 보
- `NEW-DESC-000018` / hash `52866312993a4f69` / oliveyoung / product `A000000119707` / review `39716619`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: 헤어플러스 단백질 본드 앰플 에센스 70ml 2입 세트는 손상된 모발을 위한 고단백 케어 제품으로, 특히 건조하거나 염색·펌 등으로 손상된 머릿결에 효과적입니다. 씻어낼 필요 없는 노워시 타입으로, 샴푸 후 타월 드라이한 젖은 모발에 바르기만 하면 됩니다. 크림 제형이지만 끈적임 없이 빠르게 흡수되어 모발에 수분과 영양을 공급하며, 정전기 방지에도 도움을 줍니다. 전반적으로, 헤어플러스 단백질 본드 앰플 에센스는 간편한 사용법
- `NEW-DESC-000019` / hash `5606a30a21117c6d` / oliveyoung / product `A000000232913` / review `66614967`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: 쫀득하고 밀도 높은 크림 제형으로, 물을 묻혀 롤링해 주면 풍성하고 조밀한 미세 거품이 풍부하게 일어납니다. 풍성한 거품 덕분에 피부 마찰을 줄여주어 구석구석 부드럽게 세안하기 좋습니다. 핵심 성분으로 강력한 피지 흡착 효과를 지닌 제주 화산송이와 각질 정돈에 도움을 주는 BHA(바하) 성분이 함유되어 있습니다. 모공을 막고 있는 묵은 각질과 블랙헤드, 그리고 번들거리는 과다 피지를 말끔하게 흡착해 매끈한 피부 바탕을 가꿔줍니
- `NEW-DESC-000001` / hash `5785a0a5f8c3c0ef` / elevenst / product `2877959385` / review `523478012`
  - signals: ingredient_or_spec, usage_instruction, benefit_claim
  - snippet: 제품유통기간은 2025년 07월23일까지로 넉넉합니다. 한BOX 60캡슐로 한달분입니다. 섭취방법은 1일 1회 2알씩 섭취하면 되네요. 알약 크기는 조금 큰편으로 색상은 흰색입니다. 상어연골 핵심성분으로 콘드로이친 황산은 연골을 비롯한 결합조직의 주요성분입니다. 노화가되면서 골조직내에 콘드로이친이 감소하여 관절연골에 이상이 생기고하니 영양제로 섭취해야되겠죠. 50대가 되면서 골다공증과 관절연골이 신경써여 칼슘제하고 챙겨먹는데 
- `NEW-DESC-000020` / hash `5d11a4bb1fc4a3b4` / oliveyoung / product `A000000239660` / review `66325638`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: 수분감을 가득 품은 쫀쫀한 크림 제형입니다. 피부에 부드럽게 스르륵 문질러주면 들뜸이나 겉돎 없이 피부 속 깊은 곳까지 촉촉하게 밀착 흡수됩니다. 피부 구조와 유사한 피부 장벽 유사 성분이 함유되어 있어 손상되고 건조한 피부 장벽을 기초부터 탄탄하게 케어해 줍니다. 피부 자극 테스트를 완료한 순한 저자극 처방이라 민감해진 피부도 자극 걱정 없이 안심하고 매일 바를 수 있습니다. 칼바람이 불거나 건조한 날씨에도 속당김이 완전히 
- `NEW-DESC-000021` / hash `6996ce7cbf881bb7` / oliveyoung / product `B000000200369` / review `28417316`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: 베베숲은 아기가 안전하고 엄마가 행복한 세상을 위해 시작되었고 안전한 제품으로 안심하고 사용할 수 있는 브랜드입니다. 그리고 이어서 엄마, 아빠를 위한 즐거움을 찾으려 하며 새롭운 시도를 많이 하는 브랜드로써 물티슈 품질만큼은 탑티어중 하나라고 생각합니다. 시그니처 레드의 경우 평량 80으로 시그니처 블루가 75인것에 비해 조금더 무게가 나가기 때문에 기본적으로 정말 두툼하고 촉촉함을 느낄 수 있습니다. 최고급 엠보싱 사용으로
- `NEW-DESC-000022` / hash `6a67470bc20abe40` / oliveyoung / product `A000000002944` / review `64238197`
  - signals: product_description, usage_instruction, benefit_claim
  - snippet: 알약 크기도 부담스럽지 않은 편이라 물과 함께 먹기 편했고, 바쁜 날에도 잊지 않고 챙겨 먹기 좋았습니다. 120정이라 약 4개월분으로 넉넉하게 구성되어 있어 매일 꾸준히 관리하기에도 실용적이에요. 특별히 번거로운 섭취 방법 없이 간단하게 챙길 수 있다는 점이 가장 마음에 들었고, 평소 식습관만으로 비타민C를 충분히 챙기기 어려운 분들이 데일리 영양 관리용으로 활용하기 좋은 제품이라고 생각합니다. 꾸준히 먹어보려고 합니다.
- `NEW-DESC-000023` / hash `6cac5607f92575b1` / oliveyoung / product `A000000116991` / review `39636111`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: 닥터포헤어 폴리젠 탈모증상완화 두피케어 샴푸는 탈모 증상 완화와 두피 건강 개선에 도움을 주는 기능성 샴푸입니다. 약산성 포뮬러로 민감한 두피에도 자극을 최소화하며, 비오틴, 세라마이드NP 등의 성분이 포함되어 두피 장벽을 강화하고 모발 성장을 촉진합니다. 임상 시험에서는 두피 각질과 피지 감소, 신생모 볼륨 증가 효과가 입증되었습니다. 시원한 멘톨 성분이 두피에 청량감을 주며, 유해 성분이 무첨가되어 안전하게 사용 가능합니다
- `NEW-DESC-000024` / hash `7747879a34ccb4a9` / oliveyoung / product `A000000209375` / review `66574993`
  - signals: ingredient_or_spec, product_description, usage_instruction
  - snippet: 클린뷰티 보디/헤어케어 브랜드 바이오가(Biorga)의 인기 헤어케어 제품인 바이오가 글라이신 트리트먼트 (Biorga Glycine Treatment) 1000ml 대용량 제품입니다. ​1. 제품 정보 ​제품명: 바이오가 글라이신 트리트먼트 (Biorga Glycine Treatment) ​주요 특징: ​글라이신(아미노산계 성분)과 단백질 성분이 함유되어 손상된 모발 발란스를 잡아주고 부드럽게 가꿔주는 트리트먼트입니다. ​온
- `NEW-DESC-000025` / hash `7874568cf97315d9` / oliveyoung / product `A000000000207` / review `67923769`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: 깔끔하고 개운한 세정감👍🏻 티트리 특유의 허브향이 특징이라 달달한 향보다는 산뜻하고 깔끔한 향을 선호하는 분들께 잘 맞을 것 같아요. ✔️ 좋은 점 * 티트리 특유의 상쾌하고 깔끔한 향. 호! * 산뜻한 세정감을 선호하는 분들에게 적합 * 475ml의 넉넉한 용량 ✔️ 아쉬운 점 * 세정력이 강하게 느껴질 수 있어 건조한 피부는 보습 관리가 필요할 것 같아요. 💗 총평 티트리향을 좋아하거나 산뜻한 바디케어 제품을 찾는 분들이라
- `NEW-DESC-000026` / hash `7be3ad0814f3f2bb` / oliveyoung / product `A000000171735` / review `15314917`
  - signals: product_description, usage_instruction, benefit_claim
  - snippet: 트리셀은 샴푸샘플 써보면서 알게된 브랜드인데 올영체험단으로 트리트먼트를 써보게되었어요. ✅️제형 그냥 본통 그대로 흔들어보고 뚜껑 열고 육안으로 보면 딱 워터타입이에요. ✅️사용ing 샴푸후 물기짠 머리카락에 쭉 짜서 처음에 도포하면 물처럼 묽어서 주르륵 흐르는데 바로 불투명한 크림제형으로 변해요. 사용방법은 일반 워터트리트먼트와 다르진않아요. 샴푸후 물기짠 머리카락에 도포하고 2분정도 내버려두면?ㅎㅎ됩니다. 근데 5분정도 오
- `NEW-DESC-000027` / hash `84955cf4dfe95ce2` / oliveyoung / product `A000000263007` / review `67966812`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: ## 💙 유세린 하이알루론 3X 아이크림 리뷰 ### ✔️ 제품 특징 - 눈가 보습과 탄력 관리를 위한 아이크림 - 15ml 본품 + 진정장벽 마스크팩 1매 + 광채 세럼 7ml 기획 구성 ### 👍 장점 - **발림성:** 눈가에 소량만 덜어 펴 바르기 좋아요. 눈가 피부가 얇은 만큼 손가락으로 가볍게 톡톡 두드려 바르면 부담이 적어요. - **보습감:** 눈 밑이 건조하고 당기는 느낌이 들 때 발라주면 촉촉하게 관리하기 좋
- `NEW-DESC-000028` / hash `8d22a57ed4538d8b` / oliveyoung / product `A000000268771` / review `67735732`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: 하루를 보내다 보면 해야 할 일이 많아져서 식사부터 영양 관리까지 꼼꼼하게 챙기기 어려울 때가 있네요 건강한 생활을 위해 기본적인 영양 보충부터 시작해 보려고 멀티비타민에 미네랄까지 들어가 있어서 챙기고 있습니다 리포좀 제형기술을 적용했다는 점이 눈에 들어왔고 하루 한 알로 1일 영양소 기준치 100퍼센트를 충족할 수 있도록 구성되어 있어 간편하네요 물과 함께 간단히 섭취할 수 있어 바쁜 일상에서도 챙기기 어렵지 않습니다 영양
- `NEW-DESC-000029` / hash `9857a15298184389` / oliveyoung / product `A000000157820` / review `64964024`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: 건조하고 예민한 피부 관리에 정말 추천하는 로션이에요. 피부 장벽 케어 핵심 성분인 세라마이드가 들어있어 건조해서 당기는 피부를 진정시켜주고 수분을 꽉 잡아줍니다. 질감은 촉촉한 밀크 타입으로 너무 무겁지 않고 발랐을 때 부드럽게 펴지고 흡수도 빠릅니다. 바르고 나서 기름지거나 끈적이는 느낌이 거의 없어 얼굴은 물론 몸 전체에 사용하기 좋아요. 자극적인 향이 거의 없어서 향에 예민한 분들도 부담 없이 쓸 수 있습니다. 샤워 후
- `NEW-DESC-000030` / hash `9a7d1e011c70e23b` / oliveyoung / product `A000000264460` / review `66259246`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: 페이스는 물론 건조한 전신 어디에나 넉넉하게 쓰는 만능 케어예요 150ml의 넉넉한 용량이라 얼굴뿐만 아니라 샤워 후 건조해지기 쉬운 목덜미 팔꿈치 바디 라인까지 아낌없이 바르기 참 좋아요 펌프형 용기로 제작되어 있어서 뚜껑을 돌려 열 필요 없이 위생적이고 간편하게 한 손으로 꾹 눌러 쓰기 편하더라고요 기획 세트라 용량 대비 가성비도 아주 훌륭해서 온 가족이 욕실과 화장대에 두고 함께 쓰는 패밀리 보습제로도 손색이 없어요 남녀
- `NEW-DESC-000031` / hash `9b11319186e609b9` / oliveyoung / product `A000000247241` / review `64930855`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: 이니스프리 노세범 톤업 선크림, 인스타 광고 보고 홀린 듯이 샀어요 인스타그램 피드를 넘기다가 우연히 광고를 봤는데, 너무 좋아보였어요. 매장 테스터로 손등에 주사바늘 자국으로 생긴 멍이 스윽 발리는 순간 감쪽같이 덮이는 걸 보고 감탄했어요. 이니스프리 데일리 유브이 톤업 노세범 선크림, 지금 올리브영에서 1+1 더블 기획으로 만나볼 수 있어요. 50ml 두 개가 함께 오는 구성이라 혼자 다 쓰기엔 양이 넉넉해서, 일단 엄마랑
- `NEW-DESC-000032` / hash `a000a3678f9d8b58` / oliveyoung / product `A000000209942` / review `53358331`
  - signals: ingredient_or_spec, product_description, usage_instruction
  - snippet: 염색과 펌으로 극손상모라서 단백질 케어 제품 찾다가 올리브영에서 이 기획으로 골랐는데 용량이 넉넉해서 좋네요. 제형이 진한 크림 타입이라 모발에 바를 때 잘 붙어서 흘러내리지 않아요. 샴푸 후 물기 제거하고 적당량 덜어 머리 끝부터 골고루 도포하면 돼요. 5~10분 정도 두고 헹구니 피부에 자극 없이 부드럽게 씻겨 내려가고, 헹구는 동안에도 모발이 실키하게 느껴져요. 사용 후 머릿결이 정말 매끄러워져요. 원래 푸석하고 엉키던 
- `NEW-DESC-000033` / hash `a0ca1a8f152b8d61` / oliveyoung / product `A000000253091` / review `18200389`
  - signals: ingredient_or_spec, usage_instruction, benefit_claim
  - snippet: 옵션:[단품]프라이머 피니쉬 팩트 세범 컨트롤 파우더 팩트 탤크 무첨가!! 피부가 편안한 저자극 파우더 용량: 6.5g 입자크기: 곱고 가벼운~ 사용용도: 메이크업 후 ➡️ 이마! 눈가! 콧등! T존 부위! 입가! 간편하게 유분 제거!!~ 사용방법: 팩트형이라서 간편하게수시로 사용 가능 발림성: 가볍게 톡톡~ 뭉침: 없구 끼임현상:그닥~ 밀착력: 건조함 없이 픽싱력: 깔끔하게! 커버력: 모공을 매끄럽게~ 보정력: 피부결 한~두
- `NEW-DESC-000034` / hash `a6f6d778aa75b363` / oliveyoung / product `A000000237115` / review `51638635`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: 크림 제형이 가볍고 부드러워서 젖은 모발에 발라도 끈적임 없이 잘 스며들고 말린 뒤에도 머릿결이 되게 매끈해져서 빗질이 훨씬 편해진 느낌이에용 부스스하거나 푸석한 머리카락을 정돈해두고 열 스타일링 전후로 소량 사용하면 모발 보호에도 좋아요!! 향도 은은하고 좋아서 부담 없이 매일 사용할 수 있고 150ml 용량이라 넉넉하게 오래 쓸 수 있을거같아요 ~~ 매일 쓰기 편하고 머릿결을 촉촉하게 유지해줘서 손이 잘가는거같아요 ㅎㅎ
- `NEW-DESC-000035` / hash `afc8902fa34ccd18` / oliveyoung / product `A000000263099` / review `67379666`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: 🥜페리페라 무드 블러 틴트 10호 꼬숩땅콩 및 미니틴트 도토감수성 CU편의점 콜라보 후기🥜 ​●구매이유 올영 한정컬러에 웜톤에 어울리는 이쁜 신상이라 구매함. ​■제품장점 올영 한정 컬러인데 너무 이쁨 진짜 굽굽한 색이고 같이 온 미니틴트도 너무 귀엽고 이뻐서 좋음. 너무나 부드러운 포슬 질감이 예술임. 향은 역시나 달콤한 바닐라향이 남. 미니 블러틴트도 마찬가지임. 요플레 현상도 없음. 김밥파우치 사이즈 65×125×65mm
- `NEW-DESC-000036` / hash `b2c08b8ada9ccdc9` / oliveyoung / product `A000000259285` / review `65922943`
  - signals: ingredient_or_spec, product_description, usage_instruction
  - snippet: ✨️ 사용법, 제형, 사용감 올라플렉스의 아미노결합 본드빌딩기술로 손상모 내부를 채우면서 복원하여 모발 끊어짐방지하는 특허상품이라 솔직히 가격이 좀 있지만 돈값해요. 💵 올라플렉스 전 라인에서 하나만 산다면 전 3번 추천해요! 머리감기전 마른모발에 물을 적신후 물기를 꽉 짜주고 올라플렉스3을 도포하여 3분 방치해뒀다가 정상적인 머리감기단계인 샴푸 트리트먼트 해주면 되는 제품이고 제형은 크림타입인데 약간 쫀쫀한 느낌이라 물기있는
- `NEW-DESC-000037` / hash `b3c544126d16dd27` / oliveyoung / product `A000000208395` / review `67357675`
  - signals: ingredient_or_spec, product_description, usage_instruction
  - snippet: 네오젠에서 나온 슬림 타입의 마스카라로, 이번 옵션은 6ml 본품 단품 구성입니다. 아이메이크업 제품은 브러시 형태나 제품 크기에 따라 사용 방식이 달라질 수 있는데, 슬림 타입을 찾는 경우 비교해 보기 좋은 제품입니다. 한 개 단위로 구성되어 있어 필요한 만큼만 구매하기 좋고, 파우치나 화장대에 보관할 때도 부피를 많이 차지하지 않아 관리가 간편한 편입니다. 마스카라는 눈가에 사용하는 제품인 만큼 사용 전에는 제품에 표시된 
- `NEW-DESC-000038` / hash `b740653373c532cb` / oliveyoung / product `A000000240098` / review `67362420`
  - signals: ingredient_or_spec, product_description, usage_instruction
  - snippet: 라입에서 나온 100ml 용량의 헤어 오일로, 이번 옵션은 오리지널 타입입니다. 헤어 오일은 한 번에 많은 양을 사용하기보다는 필요한 만큼 덜어 쓰는 경우가 많아 100ml 정도의 용량은 집에서 두고 사용하기에 부담이 크지 않은 편입니다. 화장대나 욕실 수납공간에 보관하기에도 무난하고, 한 병 단위로 구성되어 있어 필요한 만큼만 간단하게 구매하기 좋습니다. 오일 타입 제품은 사용량을 본인이 조절하기 쉽고, 별도의 도구 없이 손
- `NEW-DESC-000039` / hash `ba973b24282a571f` / oliveyoung / product `A000000246272` / review `67603775`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: 임상 시험으로 피부 밝기가 3,700% 개선된 것이 확인된 미백 파우더라고 해서 기대하며 챙겨 먹기 시작했는데요. 꾸준히 먹다 보니 겉만 잠깐 밝아지는 게 아니라 피부 속부터 맑고 환하게 차오르는 느낌이 들더라고요. 미백 효과는 물론이고, 평소 자주 올라오던 트러블까지 가라앉으면서 전반적인 피부 컨디션 케어에 정말 큰 도움을 받았습니다. ​무엇보다 식약처에서 인증받은 건강기능식품이라 안심하고 섭취할 수 있다는 점이 마음에 쏙 
- `NEW-DESC-000040` / hash `c0562644cd3cf6f3` / oliveyoung / product `A000000248463` / review `33612867`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: 메타그린슬림업은 건강 관리와 체형 개선을 원하는 소비자들을 위해 개발된 보조제로, 최근 많은 인기를 끌고 있습니다. 이 제품은 다양한 성분이 조화를 이루며, 특히 체지방 감소와 에너지 소비를 촉진하는 데 도움을 주는 것이 특징입니다. 먼저, 메타그린슬림업의 주요 성분에 대해 살펴보면, 그린커피빈 추출물, 가르시니아 캄보지아, 그리고 여러 가지 식물성 성분이 포함되어 있습니다. 그린커피빈은 지방 연소를 돕는 효과가 있는 것으로 
- `NEW-DESC-000041` / hash `c21198b546b20472` / oliveyoung / product `A000000258877` / review `64985033`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: &lt;&lt; 유효 성분 함량 분석 &gt;&gt; * 성분표만 보고 분석 ​1) 레티놀 복합체 (3X RETINOL) / 1% (레티놀 약 0.03% 수치) / 실효성 높음 : 레티놀, 레틴알, HPR 복합체로 구성되어 있으며 자극을 줄이면서 모공과 결 케어 효과를 누리기 딱 좋은 정석 유효 함량. 레티놀 복합체 (레티놀+레틴알+HPR)1% 배합 중 • 레티놀 1,000 IU/g (약 0.03%) • 레틴알 0.005% •
- `NEW-DESC-000042` / hash `caabcba88e81530c` / oliveyoung / product `A000000249103` / review `37835441`
  - signals: ingredient_or_spec, product_description, usage_instruction, benefit_claim
  - snippet: 자극이 적고 피부에 부드럽게 작용하여 안전하게 모공 관리와 블랙 헤드,각질 제거가 되는 클렌징 오일입니다. 모공을 축소하여 피부 트러블을 개선하는데 도움이 되고 복합적 성분들이 함유되어 산뜻하고 촉촉한 마무리감이 있습니다, 여기에 피부를 보습 및 진정 시켜주고 피부장벽 강화와 재생 효과를 부여합니다. 얼굴 세안 시에는 젖은 손에 적당량을 덜어, 얼굴 전체를 부드럽게 .마사지하고 미온수로 깨끗이 헹구면 되고 메이크업 세안 시에는
- `NEW-DESC-000043` / hash `cde092a6b4edbd8a` / oliveyoung / product `A000000265385` / review `67687275`
  - signals: ingredient_or_spec, usage_instruction, benefit_claim
  - snippet: ​평소 주름이나 잡티, 모공 케어에 관심이 많아 레티날 성분이 들어간 제품을 알아보다가 주문해 보았습니다. 바쿠치올 2%와 레티날 0.2%, 카페인 0.3% 조합이라 자극은 줄이면서 탄력 케어를 챙길 수 있어서 마음에 듭니다. ​튜브 타입이라 원하는 부위에 필요한 만큼 깔끔하게 짜서 쓰기 정말 편리하네요. 제형도 겉돌지 않고 피부에 부드럽게 밀착되어 모공 정돈과 주름 케어를 동시에 해주는 느낌입니다. ​꾸준히 밤마다 적당량 발
- `NEW-DESC-000044` / hash `ce89a2cb5a92b112` / oliveyoung / product `A000000263028` / review `51700802`
  - signals: product_description, usage_instruction, benefit_claim
  - snippet: 1.먼저 보습 효과 뛰어남 2,레이어링(겹 바르기)과 잘 어울림 여러 겹(3~5겹 이상) 레이어해서 바르면 보습감이 더 강해지고, 피부가 촉촉 + 광나는 느낌을 준다 3.민감성 피부에 적합 자극이 적고 피부 장벽 강화에 도움된다 4, 패키징 & 텍스처 펌프를 사용하면 거품 형태로 나와서 발랐을 때 부드럽고 흡수도 괜찮다 5, 사용 전 흔들어야 함 제품이 두 겹(오일 + 수분)으로 분리되어 있어서 펌프 전에 잘 흔들어야 거품 제
- `NEW-DESC-000045` / hash `d15871e15635a1a3` / oliveyoung / product `B000000231536` / review `46434139`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: 🧾 제품 특징 • 붓~ 기 관리에 도움을 주는 부종 케어 영양제 • 옥수수수염, 호박, 파인애플 브로멜라인 등 붓~기 완화에 좋은 성분 함유 • 간편한 스틱형으로 물 없이 섭취 가능 ⸻ 💊 섭취감 • 레몬/파인애플 같은 상큼한 맛 • 가루 타입이라 부담 없이 섭취 가능 • 아침이나 자기 전, 중요한 날 전날 챙기기 좋음 ⸻ 🌟 장점 • 꾸준히 먹으면 얼굴·다리 붓~ 기 완화 체감 • 운동이나 나트륨 많은 식사 후 먹기 좋음 •
- `NEW-DESC-000046` / hash `d39c20f5fb65ca1b` / oliveyoung / product `A000000261065` / review `67363126`
  - signals: ingredient_or_spec, product_description, usage_instruction
  - snippet: 셀리맥스에서 나온 50ml 용량의 듀얼 크림 제품으로, 한 용기 안에서 두 가지 타입을 나누어 사용할 수 있도록 구성된 점이 특징입니다. 일반적인 단일 제형 제품과 달리 한 제품 안에 서로 다른 구성을 함께 담은 형태라 사용 목적에 따라 나누어 활용하기 좋고, 여러 개의 용기를 따로 두지 않아도 된다는 점이 실용적입니다. 50ml 용량이라 화장대나 수납공간에 두기에도 부담이 크지 않은 편입니다. 듀얼 타입 제품은 각 부분을 필
- `NEW-DESC-000047` / hash `da71360a2bcf5161` / oliveyoung / product `A000000186037` / review `65705847`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: 탈모 증상 완화와 두피 케어에 도움을 주는 **닥터포헤어 폴리젠 시크닝 샴푸** 실사용 후기입니다. 요즘 두피가 예민해지고 모발에 힘이 없어지면서 정주행하게 된 **닥터포헤어 폴리젠 시크닝 샴푸** 찐후기 남겨요! 750ml 대용량 본품에 100ml 휴대용까지 구성이 아주 알차서 두고 쓰기 정말 든든하더라고요. 제형은 너무 묽지 않고 부드러운 영양감이 느껴지는 크리미한 타입인데, 물을 살짝만 묻혀 문질러도 조밀하고 풍성한 거품
- `NEW-DESC-000048` / hash `dfcac3685b9db6a2` / oliveyoung / product `A000000222698` / review `67341178`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: 건조함과 탄력 저하로 고민하는 피부에 즉각적인 수분 폭탄과 촘촘한 영양감을 선사하는 아누아 피디알엔 히알루론산 캡슐 세럼에 대한 심층 리뷰입니다. 이 세럼의 가장 큰 특징은 투명하고 수분감이 풍부한 겔 베이스 속에 미세한 보습 캡슐이 육안으로 선명하게 보인다는 점입니다. 펌핑 시 캡슐이 으깨지며 토출되는데, 피부에 도포하고 가볍게 롤링하는 순간 체온에 의해 캡슐이 부드럽게 녹아들며 피부 속 깊은 곳까지 유효 성분을 빈틈없이 전
- `NEW-DESC-000049` / hash `e1e07818abcc911f` / oliveyoung / product `A000000246331` / review `66488228`
  - signals: product_description, usage_instruction, benefit_claim
  - snippet: 워터리한 제형과 매력적인 잔향에 반한 2통째 찐후기 제형 및 흡수성: 손바닥에 덜어낸 컷처럼 주르륵 흐를 정도로 맑고 묽은 워터 오일 텍스처예요. 점도가 거의 없어 모발 끝에 도포해도 뭉치거나 떡지는 현상 없이 가볍고 보송하게 흡수됩니다. 향기 지속성: 솔직히 기분 좋은 향취 때문에 계속 집어 들게 되는 템이에요. 독하지 않은 은은한 꽃향이 머리카락 사이사이 꽤 오래 남아있어서 걸을 때마다 향수를 뿌린 듯 맴돕니다. 보습력 솔
- `NEW-DESC-000050` / hash `e56f702ee5f7ed85` / oliveyoung / product `A000000142695` / review `36780411`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: 비타민 C, 비타민 D, 아연, 셀레늄 등 중요한 성분들이 균형 있게 포함되어 있어 몸의 방어력을 높이는 데 도움을 줍니다. 또한 독일에서 오랜 연구를 거쳐 개발된 제품으로, 유럽에서도 꾸준한 인기를 얻고 있는 건강기능식품입니다. 그러나 단점으로는 7일 분량임에도 불구하고 다소 높은 가격으로, 가성비를 고려할 때 장기 복용에는 부담될 수 있습니다.
- `NEW-DESC-000002` / hash `e5be0b03dd4fbc16` / elevenst / product `9448173195` / review `547052621`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: 체험단에 당첨되어 체험할 수 있는 기회를 갖게 됐어요. 최근에 급격히 체중이 불고 배가 나와서 다이어트가 최대 관심사이던 차에 아주 좋은 체험 기회였습니다. 체험하게 된 제품은 체지방 감소와 혈중 콜레스테롤 개선에 도움을 줄 수 있는 리얼닥터의 체지방 다이어트&유산균 500mg x 30캡슐 제품입니다. 포장지를 보니, 측면에는 성분표가 있고 섭취량은 1일1회, 1회2캡슐 이네요. 체험제품의 소비기한은 년 월 까지로 넉넉한 것 
- `NEW-DESC-000051` / hash `e88ee4a10eb1b8a6` / oliveyoung / product `A000000183059` / review `67838320`
  - signals: ingredient_or_spec, usage_instruction, benefit_claim
  - snippet: 매일 사용하는 샴푸는 세정력뿐 아니라 씻은 뒤 모발이 얼마나 엉키는지도 중요하게 보게 되는데요. 손상 모발 케어에 관심이 있는 분들이 살펴보기 좋은 제품입니다. 샴푸할 때는 손톱으로 두피를 긁기보다 손끝으로 부드럽게 마사지하고, 잔여물이 남지 않도록 충분히 헹궈 주는 것이 중요해요. 500ml 두 개입이라 샴푸를 자주 사용하는 분들에게 넉넉한 구성이고, 스윗브리즈 옵션과 파워퍼프걸 콜라보 키링까지 있어 구성도 눈에 띕니다. 데
- `NEW-DESC-000052` / hash `eb572c418be4823a` / oliveyoung / product `A000000245087` / review `66618350`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: 제형은 촉촉하고 가벼운 젤과 크림 중간 타입으로, 피부에 부드럽고 매끄럽게 발립니다. 끈적임이나 답답함 없이 피부에 싹 흡수되어 속건조를 잘 잡아주고 산뜻한 수분 보호막을 형성해 줍니다. 핵심 성분으로 피부 진정에 도움을 주는 판테놀과 티트리잎수, 그리고 피부 장벽 케어에 유용한 세라마이드NP가 함유되어 있습니다. 자극받아 예민해진 피부를 빠르게 진정시키고 유수분 밸런스를 맞춰줍니다.
- `NEW-DESC-000053` / hash `ed5048879f123c58` / oliveyoung / product `A000000263070` / review `67116918`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: 바이오더마 시카비오 크림+의 장점 3가지입니다. ​악건성 피부를 위한 뛰어난 보습 케어: 깊은 보습과 영양을 공급해 주어 건조함으로 민감해진 악건성 피부도 촉촉하고 편안하게 진정시켜 줍니다. ​온 가족이 함께 쓰는 순한 성분: 피부 타입에 상관없이 누구나 부담 없이 사용할 수 있어, 엄마와 중학생 딸이 함께 데일리용으로 쓰기 아주 좋습니다. ​더블 기획의 넉넉한 용량과 가성비: 100ml 2개로 구성된 알찬 기획 세트로 온 가
- `NEW-DESC-000003` / hash `ee23ba035fd45326` / elevenst / product `9460836396` / review `548587932`
  - signals: ingredient_or_spec, usage_instruction, benefit_claim
  - snippet: 블랙스네일 프레스티지 4종세트 (토너,에멀젼,앰플,크림) 사용기한 제조일로부터 36개월 사용/개봉 후 사용기간 12개월 사용방법: 1)토너: 세안 후 내용물을 적당량 취해 피부 결을 따라 부드럽게 펴 발라 흡수시켜 줍니다. 2)앰플: 내용물을 적당량 취해 피부 결을 따라 부드럽게 펴 바르고 양손으로 얼굴 전체를 감싸 흡수시켜 줍니다. 3)에멀젼: 내용물을 적당량 취해 피부 결을 따라 부드럽게 펴 발라 줍니다. 4)크림: 스킨케
- `NEW-DESC-000054` / hash `f02ebae931ac8fc2` / oliveyoung / product `A000000260005` / review `66891176`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: 세안 후에도 당김 없이 순하고 촉촉하게 메이크업과 노폐물을 지워주는 데일리 클렌징 밀크입니다. ​진정과 장벽 강화에 탁월한 D-판테놀 성분이 함유되어 있어 세안 과정에서 발생할 수 있는 피부 자극을 줄여주고 피부 장벽을 보호해 줍니다. ​제형 & 사용감: 부드러운 밀크 타입 제형이 피부에 자극 없이 스며들듯 메이크업을 녹여냅니다. 물로 씻어낸 후에도 피부 수분막이 남은 듯 촉촉함이 유지되어 건조함이나 당김 현상이 없습니다. ​
- `NEW-DESC-000055` / hash `f686c40a215a9722` / oliveyoung / product `A000000246877` / review `37833060`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: 닥터자르트 세라마이딘 울트라 크림은 강력한 보습력과 피부 장벽 강화 효과로 유명한 고보습 크림입니다. 기존 세라마이딘 크림보다 보습력이 한층 강화된 울트라 버전으로, 건조한 피부를 집중적으로 케어하며 수분 손실을 막아 피부를 촉촉하고 탄탄하게 유지시켜 줍니다. 특히 세라마이드 성분이 풍부하게 함유되어 있어 피부 장벽을 보호하고, 오랜 시간 수분감을 유지할 수 있도록 도와줍니다.🙂💗 ✅제품 특징 1. 강력한 보습 & 피부 장벽 
- `NEW-DESC-000056` / hash `ff14bf8577bdf04c` / oliveyoung / product `A000000171753` / review `25578497`
  - signals: ingredient_or_spec, product_description, benefit_claim
  - snippet: ✔️올리브영에서 테스터 사용 후 이건 꼭 사야해,, 하는 마음으로 구매한 롱테이크 샌달우드 인텐시브 핸드크림🤎 롱테이크는 향이 깔끔하면서도 고급스러워 핸드크림은 물론 바디 제품까지 인기가 많은 편이라 브랜드는 알고 있었는데 롱테이크의 우디향을 맡아본 후 ‘나 우디향 좋아하네?’ 를 깨닫게 되었습니다 ◡̎ 패키지❣️튜브 형식의 알루미늄 용기에요! 하얀색에 톤 다운된 우드 포인트로 심플하고 보기만 해도 깔끔한 느낌이 들어요🤍 뚜껑

### MEDIUM — 100건

- `NEW-DESC-000138` / hash `0053b90de2cc6be4` / oliveyoung / product `A000000224315` / review `51129184`
  - signals: ingredient_or_spec, product_description
  - snippet: [판매자에게 제품비의 일부를 지원받았지만, 저의 솔직한 후기입니다.] 묽은 로션같은 제형으로 오일제형보다 떡지지 않아 좋아요 향기도 진짜 좋구요 대만족 고데기 자주 하는데 필수품될듯합니다 30ml증정은 휴대용으로도 좋겠어요
- `NEW-DESC-000139` / hash `007b155ab521f33b` / oliveyoung / product `A000000187890` / review `60819576`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 🖤💛[포켓몬에디션/5월올영픽] 코스노리 아이래쉬 틴팅 세럼 블랙속눈썹영양제💛🖤 옵션: [포켓몬에디션] 블랙속눈썹영양제 9g으로 클리어랑 블랙 두가지 버전 모두 구매를 했어요~! 포켓몬콜라보로 피카츄 아크릴 수납 홀더까지 증정되서 마음에 들어용ㅎㅎ 클리어는 세안후 영양케어 목적으로 관리해줄 때 사용해주고, 블랙은 마스카라 대신 사용해주고 있어요! 제 속눈썹이 길이감은 있어도 숱 부분에서 많이 약해진거 같아서 관리해주려구요! 꾸준
- `NEW-DESC-000140` / hash `010b7f5994f568ea` / oliveyoung / product `A000000192405` / review `67547333`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: [내돈내산] 더하르나이 시카이드 크림 솔직 후기! 진정과 장벽 케어로 입소문 난 ‘더하르나이 시카이드 크림’ 분석해 드려요! 🌿 &lt;&lt; 성분 포인트 &gt;&gt; * 진정 콤플렉스: 병풀추출물, 마데카소사이드, 아시아티코사이드, 티트리잎추출물이 들어가 자극받은 피부 진정에 탁월해요. * 피부 장벽 & 보습: 세라마이드엔피, 시어버터, 다양한 분자량의 히알루론산 및 글루타티온까지 꽉 채웠어요. * 안티에이징: 카퍼트라
- `NEW-DESC-000141` / hash `010ec46ad5bb57f4` / oliveyoung / product `A000000205930` / review `61769801`
  - signals: product_description, benefit_claim
  - snippet: 질레트 면도기는 피부를 보호하는 쉴드 구조로 피부 자극을 최소화로 자극이 적으며 매끄러운 면도가 가능하고 면도날 간 거리와 각도가 잘 설계되어 피부에 고르게 밀착되어 누구나 쉽게 사용할 수 있어 믿고 사용할수 있는 제품이면서 지금까지 사용한 면도기 중에서 최고라고 생각합니다.
- `NEW-DESC-000142` / hash `019ef853d1266f87` / oliveyoung / product `A000000253592` / review `64641879`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 크림은 너무 묽게 흐르는 타입보다는 적당히 밀도감이 있어서 얼굴에 얇게 펴 바르기 편했음. 토너와 세럼 다음에 광대랑 볼처럼 잡티가 신경 쓰이는 부위에 한 번 더 얇게 레이어링하고, 아침에는 선크림으로 마무리함. 아침저녁 매일 사용 가능한 제품이라고 안내되어있는점도 참고함. 미백 케어 제품인데도 제형 자체가 지나치게 건조하거나 뻑뻑하지 않았다는 점. 세라마이드와 판테놀 등 보습 관련 성분도 함께 배합되어 있어서 건조한 볼에는 
- `NEW-DESC-000143` / hash `02053eccdf4edd43` / oliveyoung / product `A000000255774` / review `67769439`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 머리를 감고 나서 말리기 전에는 헤어 에센스를 꼭 챙기려고 하는데, 이번에는 밀크 타입 제품으로 골라봤어요. 오일처럼 무겁게 마무리되는 제품이 부담스러운 날에도 사용하기 편할 것 같아서 관심이 갔어요. 타월 드라이 후 모발 끝부분을 중심으로 소량씩 발라 주고 드라이하면 손질할 때 활용하기 좋겠네요. 특히 반곱슬 모발은 습도나 건조 상태에 따라 부스스해 보일 때가 있어서 평소 보습 관리가 중요하다고 느껴요. 90ml라 욕실이나 
- `NEW-DESC-000144` / hash `02c8a7df98fb5aaf` / oliveyoung / product `A000000268069` / review `67776651`
  - signals: product_description, benefit_claim
  - snippet: 환절기만 되면 피부가 들뜨는데 토너 팩으로 활용하니 각질이 싹 진정되네요. 보습력이 탁월해서 토너만으로도 피부 바탕이 탄탄해집니다. 미니 로션과 폼클렌징까지 알차게 구성되어 있어 가성비 대족입니다. 데일리 장벽 케어용으로 매일 손이 가는 효자 아이템이에요.
- `NEW-DESC-000145` / hash `03124908605ec422` / oliveyoung / product `A000000264460` / review `66259138`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 무너진 피부 장벽을 탄탄하게 채우는 세라마이드 보습, 끈적임 없는 부드러운 고보습 밀착 텍스처, 얼굴부터 바디까지 안심 케어 저자극 포뮬러, 넉넉한 150ml 알찬 기획 세트 구성 ​❤️ 건조하고 민감해진 피부를 편안하게 달래주고 싶어서 선택했어요 환절기만 되면 피부가 유난히 땅기고 붉게 달아오르는 데다 가려움까지 느껴져서 순한 보습제를 찾아보게 되었어요 보습력이 좋다는 크림은 유분기가 과해서 모공을 막거나 겉돌기 일쑤였고 가
- `NEW-DESC-000057` / hash `03981d0e88b56a63` / elevenst / product `5560778476` / review `510514176`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 나이가 40대에 접어드니 슬슬 흐릿하게 보이기도하고 눈이 피곤한게 자주 느껴지더라구요. 일하다보면 모니터도 꽤 긴 시간을 들여다보고 책도 많이 보다보니 남들이 먹는다는 루테인이 정말 효과가 있을까 궁금해하던 참에 이렇게 신상리뷰단에 루테인이 있어서 처음 접하게 되었어요. 일단 보령 루테인지아잔틴 아스타잔틴 플러스의 좋은점은 1일 1회 1캡슐만 복용하면 된다는점이고요. 일상이 바쁘다보면 여러번 챙기는 영양제들은 잊어버리기 쉽더라
- `NEW-DESC-000146` / hash `03e3a5ab2184ed73` / oliveyoung / product `A000000212126` / review `35858972`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 🩷케라스타즈 제네시스 샴푸 250ml🩷 케라스타즈 두피케어 제품 중 제네시스 두피앰플을 사용했었는데 향이 진짜 넘넘 좋아서 같은 라인인 제네시스 샴푸도 구매를 했어용 향 똑같고 진짜 넘 맘에 들어요 주변에서 헤어제품 뭐 쓰냐고 꼭 물어봐용 ㅎㅎ 증정품으로 받은 블랙 스크런치도 벨벳에다가 짱짱해서 맘에 들어용:)
- `NEW-DESC-000147` / hash `041267f12b0b9741` / oliveyoung / product `A000000243921` / review `57508599`
  - signals: ingredient_or_spec, product_description
  - snippet: &#34;치팅데이 필수템! 알파CD 성분으로 꽉 채운 스마트한 식단 서포트 후기 💛&#34; • 제품의 핵심: &#34;강력한 핵심 성분 배합&#34; 1포당 알파시클로덱스트린 2,860mg을 비롯해 난소화성말토덱스트린, 베타시클로덱스트린까지 총 3,500mg의 고함량 성분이 들어있어 기름진 음식 섭취 후 걱정되는 마음을 달랠 수 있습니다*^^* • 편의성 및 디자인: &#34;휴대가 간편한 옐로우 스틱&#34; 3.5g 소포
- `NEW-DESC-000058` / hash `044fc04c15ee87bb` / elevenst / product `76958610` / review `460825008`
  - signals: ingredient_or_spec, product_description
  - snippet: 테팔 프라이팬 3종 세트를 구입했습니다.. 24센티, 28센티 프라이팬과 28센티 웍, 세 가지로 구성되어 있습니다. 이번에 신상품 출시 기념행사가 있어서 저렴하게 구매할 수 있었습니다. 게다가 세트제품은 프라이팬의 실리콘 뚜껑과 컵에 사용할 수 있는 크기의 실리콘 뚜껑도 서비스로 들어 있네요... 프라이팬이 무게감이 있어서 좋습니다. 웍은 용량이 상대적으로 작다는 생각을 할 수도 있을 듯 합니다. 그럼에도 이 정도 가격에 테
- `NEW-DESC-000148` / hash `04d5ebbb6df97a03` / oliveyoung / product `A000000251304` / review `58431471`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 자외선 차단되는 핸드크림 찾다가 완전 픽했어요! 핸드크림에 SPF35 PA++라니.. 손도 자외선 차단 해줘야 한다는 거 알면서도 맨날 까먹었는데 이거 하나로 해결됐어요 ㅠㅠ 펌프형이라 짜서 바르기 편하고 위생적인 것도 마음에 들고요! 향이 진짜 대박인데 딥머스크 향이 은은하게 나서 손에서 은은한 향수 냄새 나는 느낌이에요🤍 향 때문에 또 손에 바르고 싶어질 정도.. 발림성도 찐득하지 않고 가볍게 쫙 펴발리면서 흡수도 빠르게 
- `NEW-DESC-000059` / hash `051d7010554dc859` / elevenst / product `2835570428` / review `499433715`
  - signals: usage_instruction, benefit_claim
  - snippet: 코큐텐은 항산화효과가 있으며 노화와 관련 된 여러가지 증상에 도움을 줄 수 있어서 꾸준히 복용하는 제품. 타블렛이 아닌 캡슐로 된 제품이어서 약 냄새가 나지 않고 외국제품은 크기가 다소 큰제품이 있는데 이 제품의 캡슐크기는 타이레놀 크기와 비슷해서 목 넘김이 어렵지 않아요. 한병당 120캡슐이 들어 있고 하루에 한번만 복용하세요.
- `NEW-DESC-000060` / hash `0520eb41a50900c9` / elevenst / product `3141554187` / review `527318948`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 3~4달전 여기서 구매한건 아니었지만 식욕감소 효과가 있긴 했어요. 그래서 운동 병행해서 5~6kg 정도 감량했지만 스스로의 식단조절, 운동 없이는 다시 복구 되더라구요. 다시 시작하려고 구입했어요. 여름이라 얼음팩도 3개씩 넣어서 보내주셔서 시원하게 왔어요.
- `NEW-DESC-000149` / hash `05710b8813b6e9d5` / oliveyoung / product `A000000142709` / review `67769060`
  - signals: ingredient_or_spec, usage_instruction
  - snippet: 손은 자주 씻다 보니 계절과 상관없이 건조함을 느낄 때가 있어서 핸드크림을 꾸준히 챙기는 편이에요. 비욘드 클래식 살냄새 핸드크림은 이름이 독특해서 궁금했는데, 이번에는 딥모이스처 올리브 타입으로 골라봤어요. 손이 건조할 때마다 적당량을 덜어 손등과 손가락 사이까지 꼼꼼하게 발라주면 좋을 것 같아요. 특히 손을 씻은 직후나 잠들기 전에 사용하는 루틴으로 활용하기 편리하겠어요. 100ml 용량이라 집에 두고 넉넉하게 사용하기에도
- `NEW-DESC-000150` / hash `05f6204f66172608` / oliveyoung / product `A000000192405` / review `67161485`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 평소 민감하고 예민하면서도 기름진걸 싫어하는 피부 타입인 저에게 바르는 순간 자극 없이 부드럽게 스며들어 확실한 진정 케어 효과를 안겨주었으며, 100ml 대용량 본품 외에도 30ml 추가 증정 구성이 함께 포함되어 있어 집은 물론 여행용으로 들고 다니기에 굿이었습니다. 끈적임이나 무거운 느낌 없이 촉촉하게 수분을 채워주는 덕분에 사계절 내내 부담 없이 바를 수 있는 훌륭한 1차 크림인것 같습니다
- `NEW-DESC-000151` / hash `074510cf00ec82e2` / oliveyoung / product `A000000268739` / review `67394439`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 틴트로만 가리려고만 했지 입술을 케어하고 착색된 입술톤을 개선하려고 안했었어요. 구달 청귤 비타씨 판테놀 립 세럼은 거무죽죽하게 착색된 입술톤을 개선하고 판테놀 5%로 보습 케어를 도와주네요. 입술 톤도 자연스럽게 밝아지고 입술 각질과 속보습도 개선되서 눈에 띄게 입술이 밝아졌어요. 왜 이제야 알았나 싶어요. 지인들에게도 선물햐줘야 겠어요.
- `NEW-DESC-000123` / hash `076cd5e68a2ace41` / musinsa / product `2758160` / review `87512260`
  - signals: product_description, benefit_claim
  - snippet: 3일째 사용 중입니다. 사용하기 편하고 코주위 턱주위 각질 제거에 효과가 있는것 같습니다. 제형은 거의 물같이 흐르는 액상 제형입니다. 스킨 같이 바르고있습니다.
- `NEW-DESC-000152` / hash `0780e482d224041d` / oliveyoung / product `A000000263562` / review `66725201`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 구달은 써보신 분은 아시겠지만 항상 믿고 쓰는 제품입니다. 행사까지 하니까 사지 않을 이유가 없습니다. 본품 50ml에 리필까지 50ml입니다. 거기에다가 귀여운 폼폼푸린 마그넷 피규어까지 같이 받을 수 있습니다. 최고의 구성이죠! 이 제품은 모든 피부 타입에 괜찮은 듯 합니다. 잡티케어는 물론 피부 미백에도 좋다고 하네요. 또 주름개선에도 효과가 탁월하다고 설명하고 있어요. 완전 강추합니다!!
- `NEW-DESC-000061` / hash `0829c358e3e371eb` / elevenst / product `9087201366` / review `544389013`
  - signals: ingredient_or_spec, product_description
  - snippet: 40대가 되면서 건강 관리에 신경 쓰고 있는데 신풍제약 애드 마일스 칼슘 마그네슘 비타민D 아연 플러스 알게 되어 일주일간 복용해 봤습니다 영국산 프리미엄 벌집형 해조 칼슘 300mg 체내 흡수율이 높은 활성형 비타민D 마그네슘150mg, 미국산 프리미엄 아연을 한 번에 섭취할 수 있는 건강기능식품입니다 칼슘과 마그네슘이 2 대 1 황금비율로 구성되어 있는 제품으로 알약 사이즈는 중간 사이즈보다 약간 큰 사이즈로 1일 1회 1
- `NEW-DESC-000153` / hash `08ae9e1e6ac3a268` / oliveyoung / product `A000000267748` / review `67771560`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 너무 무겁지 않은 촉촉한 세럼이네요 ! 피부에 겉돌지도 않고 잘 흡수돼서 나이트 루틴에 쇽 넣기 좋아요 ㅎㅎ 마데카소사이드 성분이 들어 있어 데일리 진정 케어용으로도 좋고 바르고 나면 피부가 수분감 위주로 촉촉하게 정돈되고 당기는 느낌도 사라져서 넘 조아용 50ml 본품이 두 개라 총 100ml로 넉넉해서 한동안 부담 없이 사용할 수 있어 든든하네요~ 서울 에디션도 넘 예뻐서 더 맘에듭니당!
- `NEW-DESC-000154` / hash `0958665cb09aa2ba` / oliveyoung / product `A000000260524` / review `67772662`
  - signals: product_description, usage_instruction
  - snippet: 메이크업이나 피부 표면의 노폐물을 오일 타입으로 정리하고 싶은 분들이 관심을 가질 만한 클렌징 제품이에요. 마른 손과 마른 얼굴에 적당량을 덜어 부드럽게 마사지한 뒤, 물을 조금씩 더해 오일이 유화되도록 충분히 문질러 주고 깨끗하게 헹구면 돼요. 특히 코 주변처럼 피지가 신경 쓰이는 부위도 손에 힘을 주지 않고 부드럽게 관리하는 것이 중요해요. 리필 캡이 함께 구성되어 있어 본품을 사용한 뒤 이어서 활용하기에도 편리해요. 오일
- `NEW-DESC-000155` / hash `09bae94b2168a482` / oliveyoung / product `A000000142281` / review `67846850`
  - signals: ingredient_or_spec, usage_instruction
  - snippet: ​샤워볼에 적당량을 덜어 문질러보면 적은 양으로도 풍성한거품이 풍성하게 일어나서 구석구석 부드럽고 시원하게 씻어낼 수 있어요. 우유단백질과 바오밥나무씨 추출물이 들어있어서 샤워할 때 자극이 없고, 물로 헹궈낸 뒤에도 피부 당김 없이 샤워후촉촉함이 오랫동안 유지됩니다. ​무엇보다 부담스럽지 않은 은은한향의 화이트머스크 향기가 욕실에 기분 좋게 가득 퍼져요. 샤워를 마치고 나와서도 살살 감도는 살냄새 같은 잔향이 매력적이라 향수 
- `NEW-DESC-000062` / hash `09e62db15c0e1ce8` / elevenst / product `1904293793` / review `529387057`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 올 여름 폭염 때문인지 나이 때문인지 피부가 너무 안좋아져서 피모 사료와 면역 사료 중 뭘 살까 고민하다가 면역력을 개선해주면 피부도 좋아질 것 같아 선택했어요. 사료 위에 토핑을 해서라도 하루에 한 번은 꼭 먹도록 급여하고 있어요. 영양학적으로도 괜찮은 사료라 생각되고, 우선 피부에 집중을 하고 있어서 꾸준히 급여하고 있는데 급여 후 피부 상태가 점점 개선되고 있는 것 같아요. 100% 휴먼 그레이드 식재료. 합성보존료 착색
- `NEW-DESC-000156` / hash `0a0d7f817d52b3df` / oliveyoung / product `A000000252917` / review `66393657`
  - signals: product_description, benefit_claim
  - snippet: 손상 장벽 케어에 유명하길래 기획세트로 쟁여두고 한 달 동안 장벽 채우고 싶을 대 꾸덕하게 듬뿍 얹어봄. 연고 같은 크림 제형이라 처음엔 살짝 묵직한가 싶었는데, 흡수시키고 나면 거칠어졌던 피부 결이 쫀쫀하게 코팅되면서 편안하게 진정되는 게 확실히 체감됨. 외부 자극받아서 성난 부위나 푸석하던 피부가 매끄럽게 잠잠해져서 요즘 환절기 필수템으로 매일 쓰는 중. 평소에 찬바람이나 외부 자극 때문에 피부 장벽이 무너져서 쉽게 예민해
- `NEW-DESC-000124` / hash `0a45d716b3806f9f` / musinsa / product `4619643` / review `85568910`
  - signals: ingredient_or_spec, product_description
  - snippet: 검정벨트 사고싶어서 여기저기 계속 기웃거렸는데 무진장 세일덕분에 천연소가죽 벨트를 이 가격에.. 거기에다 적립금에 장바구니 쿠폰까지 적용되서 와우!! 완전 득템했네요^^ 폭 2cm라 슬랙스 청바지 아무데나 착용가능하구요 벨트구멍도 9개로 넉넉하게 뚫려있어 왠만한 사이즈는 다 커버될듯하네요. 참고로 저는 바지 M사이즈 허리 27~28정도인데 웨스트 높이정도에 따라 맨 안쪽 구멍에서부터 3~4번째 착용하니 잘 맞네요. 버클은 안쪽
- `NEW-DESC-000157` / hash `0a8ff1777c40e511` / oliveyoung / product `A000000147782` / review `64324460`
  - signals: ingredient_or_spec, product_description
  - snippet: 🥨딜라이트 프로젝트 옐로우 머스타드 프레첼 70g 후기🥨 ​[구매이유] 역시나 호기심에 구매함. ​■제품특징 ​톡 쏘는 머스타드의 이색적 매력 옐로우 머스타드 프레첼 코끝 찡한 머스타드에 한 번, 달콤짭짤한 맛에 또 한번 매료되는 멈출 수 없는 프레첼 스낵 ​■원료 ​벌크미니미니(이집트산/밀, 팜유, 소금, 설탕, 이스트), 혼합식용유(팜올레인유, 해바라기유, d-토코페롤), 복합조미식품(설탕, 머스타드분말, 가공소금, 식초분
- `NEW-DESC-000158` / hash `0ab364db755577f7` / oliveyoung / product `A000000213261` / review `65904737`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 실속 있는 두피 케어 조합~!~! 욕실에 두는 데일리 제품은 패키지만 화사해져도 공간 분위기가 달라집니다. 청미정 다시마 샴푸 산리오 폼폼푸린 콜라보 에디션은 귀여운 디자인은 물론, 세트에 포함된 샴푸브러시와 여행용 미니 용량 덕분에 활용도가 뛰어납니다. 핵심 특징 및 구성 포인트 * 알찬 기획 구성: 본품(500ml)에 더해 손에 착 감기는 샴푸브러시와 휴대하기 좋은 여행용 용량이 함께 포함되어 있어 출장이나 여행 시 덜어 
- `NEW-DESC-000159` / hash `0b17a37529d9343e` / oliveyoung / product `A000000237115` / review `51517575`
  - signals: product_description, usage_instruction
  - snippet: 머릿결이 건조하면 스타일이 잘 안 살아서 늘 고민이었는데 멜로우 크림은 바르는 순간 결이 매끄러워져요 흐르지 않는 촉촉한 크림 제형이라 펴 바를 때 모발에 얇게 밀착되고, 여러 번 레이어링해도 무겁지 않아 유분 많은 제품처럼 답답한 느낌이 전혀 없어요 모발 끝이 갈라지고 푸석했던 부분이 수분감이 차오르면서 자연스럽게 정돈돼서 손상모 케어용으로 딱 맞아요 특히 펌이 들어간 머리는 컬이 힘없이 풀리기 쉬운데 이 크림은 컬이 흐트러
- `NEW-DESC-000160` / hash `0b478a8b1f898a46` / oliveyoung / product `A000000232212` / review `64985685`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: &lt;&lt; 유효 성분 함량 분석 &gt;&gt; * 성분표만 보고 분석 1)​ 실리카 (미세침) / 전성분 중반 배합 / 유효함 : 피부 표면에 미세한 자극을 주어 유효성분의 흡수를 높여주는 핵심 딜리버리 유효 성분. ​2) 나이아신아마이드 / 전성분 상단 (약 2~5% 추정) / 실효성 높음 : 정제수 및 보습제 바로 뒤에 배합되어 피지 조절, 장벽 강화, 미백 효과를 충분히 낼 수 있는 위치. 3) ​병풀추출물 및 C
- `NEW-DESC-000161` / hash `0c57a4d7162268d5` / oliveyoung / product `A000000242806` / review `65306071`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 장벽 강화에 진짜 효과 있어요! 31ml 추가 증정이라 구성도 알차고 건조한 피부에 딱이에요 🌿
- `NEW-DESC-000162` / hash `0d1a954cf03023fa` / oliveyoung / product `A000000173340` / review `16486872`
  - signals: product_description, benefit_claim
  - snippet: 평소에도 퍼펙스세럼 좋아하는데 샴푸로까지 나왔다기에 바로 올리브영체험단에서 신청하였어요 퍼펙트세럼 영양을 담은 영양케어 샴푸 후 헹굴때도 엉킴없이 부드러워서 마치 트리트먼트를 한 것 같은 효과를 샴푸만으로도 느낄 수 있어서 너무 신기했습니다 제형은 투명한 겔 타입으로 에센스짜는 느낌이라 거품이 잘 안나올까 걱정했는데 샴푸하면 거품이 엄청 잘 나와서 골고루 두피의 노폐물을 제거하는데 충분했습니다 대부분 샴푸하고 나면 머릿결이 빳
- `NEW-DESC-000163` / hash `0dcd4b855769ce34` / oliveyoung / product `A000000244929` / review `65931770`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 평소 장 유산균이랑 잘유산균을 따로 먹었는데 요건 하나로 같이 관리할 수 있는 제품이라 편하네요. 하루 1캡슐, 장과 질 건강을 한 번에 케어할 수 있어서 장 유산균을 따로 먹지 않아도 돼서 좋아요 ㅎ 질 유래 유산균이 아니라 식약처에서 인정받은 리스펙타 프로바이오틱스가 들어있고, 질 내 유익균 증식 및 유해균 억제에 도움을 주는 제품 시험에서도 섭취 15일 후 질 분비물 75% 감소, 질 소양감 79% 감소 결과가 있었고 질
- `NEW-DESC-000063` / hash `0f18eef8c09dffb7` / elevenst / product `9448173195` / review `547071040`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 신상리뷰단에 당첨되어 기쁘네요 ~ 요번상품은 리얼닥터 체지방다이어트 앤 유산균30캡슐입니다~ 박스포장으로 꼼꼼히 잘 배송되었고요~ 요상품의 특징은 녹차추출물과 프로방오틱스 카테킨300mg함유로콜레스테롤억제와 장건강까지 도움을 받을수 있는제품ㅇ예요 전 비만아닌 마른체형이지만 갱년기때문에 장이 안좋아 유산균먹고있어요 장 유산균이 중요하고 또한 당뇨 혈관생각해서 콜레스테롤 수치 잡아줘야 좋거든요 요제품이 한번에 두가지 기능이 있어 
- `NEW-DESC-000164` / hash `0f8dfbc85718c8de` / oliveyoung / product `A000000261442` / review `67086442`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 어성초추출물의 압도적 용량 100,000ppm을 함유하여 신속하게 피부 진정에 도움을 줄 수 있어 아주 좋아요 :) 단 한번의 사용만으로 오돌토돌 요철을 케어할 수 있으며 어성초 PDRN이 손상된 피부 장벽을 되돌려 요철을 효과적으로 케어하여 매끈한 피부를 완성할 수 있어 추천합니다 ♥
- `NEW-DESC-000165` / hash `1003a37c009adaa5` / oliveyoung / product `A000000251616` / review `65235216`
  - signals: ingredient_or_spec, product_description
  - snippet: 10%할인에 1+1까지 적용되고, 추가로 구매 3만원 이상시 3천원 추가 할인으로 너무 저렴하개 샀습니다~!!
- `NEW-DESC-000166` / hash `107504bb35949291` / oliveyoung / product `A000000257345` / review `62640599`
  - signals: ingredient_or_spec, product_description
  - snippet: 평소 데오드란트 향이 강한 건 좀 부담스러운데 이건 무향이라 너무 좋더라구용! 향수 뿌려도 향 안 섞여서 굿👍 크림 제형이라 손으로 쓱쓱 바르기 편하고 끈적임 없이 흡수도 잘 돼요. 생각보다 지속력도 괜찮아서 외출할 때 바르고 나가면 든든한 느낌ㅎㅎ 15ml라 파우치에 쏙 들어가는 크기라 운동 갈 때나 여행 갈 때 챙겨 다니기 좋을 것 같아요. 그리고 나이아신아마이드 성분이 들어있어서 제모 때문에 거뭇해진 겨드랑이 관리도 같이
- `NEW-DESC-000167` / hash `10b4ebf9724e3ddf` / oliveyoung / product `A000000233029` / review `67716569`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 알찬 구성이라 득템 느낌 만점이에요! ✨ 데일리로 챙기기 딱 좋아서 프롬랩스 단백질 흡착 트리트먼트 200ml 더블 기획 만족도 최고예요 ☁️ 1등 손상모 트리트먼트답게 단 1회 만에 손상모를 개선해주고, 단백질 흡착으로 푸성푸성했던 모발이 매끈하게 정돈돼요 💧 200ml 더블 구성이라 든든하고, 푸른 향과 부드러운 사용감으로 머릿결에 탄력과 윤기를 되찾아줘서 든든해요 🫧 샴푸 후 바쁜 샤워 루틴에서 당김 없는 부드러움과 한 
- `NEW-DESC-000168` / hash `10f1fa7a5113f62c` / oliveyoung / product `A000000188024` / review `68038169`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 세안 후 급격히 푸석해지고 탄력이 떨어질 때 영양을 밀도 있게 채워주는 마스크팩입니다. 농밀한 에센스 제형이 흐르지 않고 시트에 착 붙어 있어서 깔끔하게 부착하기 편리해요. 밀착력이 우수해 유효 성분이 온전히 스며들어 투명한 광채를 만들어 줍니다. 지치고 메마른 얼굴에 집중적으로 영양 케어를 하고 싶을 때 망설임 없이 선택하는 정착 제품입니다.
- `NEW-DESC-000169` / hash `11afea47574494ba` / oliveyoung / product `A000000222837` / review `67537381`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 에스트라 아토베리어365 하이드로에센스 [200ml + 크림 10ml + 앰플 10ml] 완전 대만족이에요! 🌟 역시 에스트라 답게 건조하고 예민한 피부도 안심하고 쓸 수 있는 촉촉한 수분감이네요~ 😆 200ml 대용량 본품에 크림과 앰플 증정까지 해서 든든하고 가성비 최고예요! ✨ 제형이 물처럼 가볍지만 발랐을 때 수분감이 확실히 차오르고 끈적임 없이 산뜻하게 스며들어요 💧 아토베리어 라인 특유의 진정 케어 덕분인지 피부 장
- `NEW-DESC-000170` / hash `13c4a4b6719d6df4` / oliveyoung / product `A000000267556` / review `66715226`
  - signals: product_description, benefit_claim
  - snippet: ​스터닝 틴티드 립 오일과 이지 케어링 립 오일이 양쪽에 함께 구성된 듀오 립 제품으로, 틴트는 물론 글로우, 치크, 립밤, 하이라이터까지 다방면으로 활용 가능한 알찬 하이브리드 립이에요. ​03 뉴트 비스코티 컬러를 입술에 얹어보니 차분하면서도 고급스러운 분위기를 만들어주고, 끈적임 없는 논스티키 제형이라 사용감이 정말 깔끔합니다. 저자극 보습 케어와 수분 젤 키핑 시스템 덕분에 각질 부각이나 건조함 없이 24시간 촉촉하게 
- `NEW-DESC-000171` / hash `14b16568f053cf08` / oliveyoung / product `A000000137180` / review `66441319`
  - signals: ingredient_or_spec, product_description
  - snippet: 대용량이라 데일리 토너로 정말 넉넉하게 사용할 수 있어서 마음에 들었어요. 제형은 물처럼 가볍고 산뜻한 편이라 세안 직후 피부에 부담 없이 사용할 수 있었습니다. 화장솜에 충분히 적셔 피부결을 닦아내듯 사용해도 좋고, 손바닥에 덜어서 여러 번 레이어링해도 끈적임이 심하지 않았어요. 피부가 건조하게 느껴지는 날에는 두세 번 덧발라주면 촉촉함이 더 잘 느껴졌습니다. 500ml 본품에 100ml까지 추가로 구성되어 있어서 아낌없이 
- `NEW-DESC-000125` / hash `15491163f4a5f767` / musinsa / product `5858524` / review `84218314`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 영양 성분 및 맛: 설탕을 뺀 '제로 슈거' 제품임에도 불구하고, 진한 초코 우유의 맛을 잘 구현해 냈습니다. 특히 당류 0g에 단백질 24g이라는 고함량 설탕 방패를 갖춰, 식단 관리 중 발생하는 '단맛에 대한 갈증'을 리스크 없이 해결해 줍니다. 제형 및 목넘김: 단백질 음료 특유의 텁텁함이나 걸쭉함이 적어 목넘김이 매우 깔끔합니다. 냉장 보관 후 차갑게 흔들어 마시면 운동 직후 열기를 식히는 [이익 x 멀티플] 효과를 극
- `NEW-DESC-000172` / hash `15903d244771be0e` / oliveyoung / product `A000000171735` / review `36238805`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 모발 영양에 도움을 주는 아미노산 17종과 단백질 3종이 함유된 앰플 트리트먼트예요. 특히 머릿결을 부드럽고 윤기나게 가꾸어주고 머릿결에 힘이 느껴지네요. 두피 가 건강해 지는 느낌이에요
- `NEW-DESC-000173` / hash `15d7e5bf318e8886` / oliveyoung / product `B000000231536` / review `48589812`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 가벼움을 위한 칼륨, 커큐민, 병풀 추출물이 함유되어있고 원활한 순환을 위한 회화나무 열매, 메리로트, 포도씨 함유로 간접적으로 붓.기개선에 탁월한 도움을 줍니다. 맛있는 파인애플 맛으로 먹기 편하고 아침에 얼굴이 잘 붓는 사람에게 필수템입니다.
- `NEW-DESC-000174` / hash `1630edecdbbfbee0` / oliveyoung / product `A000000206053` / review `67722700`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 알찬 구성이라 득템 느낌 만점이에요! ✨ 데일리로 챙기기 딱 좋아서 넘버즈인 1번 판토텐산 액티브 수딩크림 [수분진정/올영단독] 80ml 1+1 기획 (더블기획) 만족도 최고예요 ☁️ 1번 판토텐산 성분 답게 수분 진정 케어에 탁월하고 130시간 수분지속으로 건조함을 확실히 잡아주면서 피지 감소에도 도움을 주는 느낌이에요 💧 끈적임 없이 산뜻하면서도 보습력이 뛰어나 바쁜 아침 토너 대용이나 저녁 마무리 크림으로 데일리로 부담 
- `NEW-DESC-000175` / hash `1641910c8b3de335` / oliveyoung / product `A000000246272` / review `65900812`
  - signals: ingredient_or_spec, product_description
  - snippet: 피부 속부터 화사하게 밝혀주는 글로우뮤즈 스킨 밸런스 파우더 레몬맛이에요! 핵심 성분인 피에스트로가 함유되어 (피부밝기 3700% 증가 확인) 피부톤과 기미·잡티 케어에 탁월하고, 아연 성분이 트러블 개선 및 전반적인 피부 컨디션과 피부결을 매끈하게 케어해 줍니다. 식약처 인증을 받아 안심하고 챙길 수 있으며, 새콤달콤한 레몬맛 파우더 제형이라 물 없이 간편하게 챙겨 먹기 좋아요! 매일 맛있게 피부 바탕을 케어해 주는 데일리 
- `NEW-DESC-000176` / hash `1681e72db2c7fb56` / oliveyoung / product `A000000214738` / review `66986921`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 완전 대만족이에요! 🌟 수상 경력에 믿고 질렀는데 비듬 케어 샴푸로 역시 최고네요~ 😆 200ml 용량이라 든든하고, 5종 중 골츠푸트(비듬정화)로 선택하니 내 머리에 딱 맞는 느낌이에요! 거품이 풍성하게 나고 씻고 나면 두피가 시원하게 정화되는 느낌이 들어요 ✨ 비듬이 확실히 진정되고 머리카락이 뽀송하게 말려서 다음 날에도 두피가 편안해요 💧 비듬 고민이 있거나 두피 케어를 제대로 하고 싶은 분들께 진짜 강추합니다 💖
- `NEW-DESC-000177` / hash `16e4bead43279f9e` / oliveyoung / product `A000000223625` / review `67873070`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 피부 표면의 각질을 관리하고 매끄러운 피부 결을 유지하고 싶을 때 살펴보기 좋은 제품이에요. 글리콜릭 애시드 7%가 함유된 토너라 매일 사용하는 수분 토너와는 구분해서 관리용으로 사용하는 것이 좋습니다. 처음에는 일주일에 한두 번 정도로 시작해 피부가 어떻게 반응하는지 확인하고, 따가움이나 건조함이 느껴지면 사용을 중단하는 편이 안전해요. 레티놀이나 다른 각질 제거 성분과 한 번에 함께 사용하지 않도록 주의하고 보습 케어도 충
- `NEW-DESC-000178` / hash `170b238ff2aa19b1` / oliveyoung / product `A000000268771` / review `67867193`
  - signals: product_description, benefit_claim
  - snippet: 직업상 출근하는 시간이 들쑥날쑥이기도하고 아침에는 준비할 일이 많아서 식사를 제대로 챙기지 못하는 날이 종종 있는데 영양제를 먹으려고 해도 식후에만 섭취해야 하면 자꾸 놓치게 되는데 공복에도 섭취할 수 있는 제품이라 편리해 보여 선택하게됐어요 하루 한 알로 비타민과 미네랄을 간편하게 챙길 수 있고 리포좀 제형기술이 적용되었다는 점도 마음에 들어서 선택하게됐구요 1일 영양소 기준치도 충족이 되서 매일 챙기는 영양 관리용으로 활용
- `NEW-DESC-000064` / hash `1778254c5f5a98ee` / elevenst / product `2835570428` / review `441468355`
  - signals: ingredient_or_spec, usage_instruction
  - snippet: 유통기한 2024. 01 // 복용법 : 1캡슐당 500mg 용량이니 1일 2캡슐씩 2회 식간(공보) 이나 잠자기 전에 섭취하되 충분한(8 oz) 물이나 음료를 마시면 흡수률을 높일 수 있다고 되어있어요. 아무래도 수용성 아미노산이라 그런듯하네요. 저는 일어나서 2알, 점심과 저녁사이에 2알 복용하고 있어요. 알약 크기는 손가락 한마디정도로 삼키는 데 부담스럽지는 않네요. L아르기닌 이 운동하는 분들도 많이 드시긴 하지만 임신
- `NEW-DESC-000179` / hash `17b29fab823f14d8` / oliveyoung / product `A000000230114` / review `66074289`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 머리 감고 나서 젖은 상태에 가볍게 슥슥 뿌려주기만 하면 돼서 평소에 바쁜 아침이나 드라이 전후로 손이 아주 자주 가요 🤍 끈적임 없는 촉촉한 밀크 제형이라 모발에 뭉침 없이 고르게 스며들고, 드라이 열로부터 모발을 보호해 주는 느낌이라 부담 없이 쓰기 딱 좋아요 ✨ 푸석하던 머릿결이 한결 부드럽고 차분하게 정돈돼서 만질 때마다 기분이 좋아지더라고요 👍 넉넉한 200ml 본품에 리필까지 더해진 구성이라 당분간 헤어 케어 걱정 
- `NEW-DESC-000180` / hash `184587240eff5e36` / oliveyoung / product `A000000212062` / review `66630130`
  - signals: usage_instruction, benefit_claim
  - snippet: 드라이 하기 전 머리카락에 도포해요. 머릿결 보호 효과가 있는 것 같아요 .
- `NEW-DESC-000065` / hash `18a36416d1c31a63` / elevenst / product `9572896511` / review `548488067`
  - signals: ingredient_or_spec, product_description
  - snippet: 포좀 기술이 적용되어 일반 비타민보다 체내 지속력과 흡수율이 뛰어나다는 점이 가장 큰 장점 같아요 하루 1000mg으로 몸 속 항산화 성분을 꽉 채워주는 느낌이라 아주 만족스럽게 섭취 중입니다
- `NEW-DESC-000181` / hash `18c4421d069a426b` / oliveyoung / product `A000000184723` / review `22173045`
  - signals: ingredient_or_spec, usage_instruction
  - snippet: 보통 헤어 오일은 아무래도 사용감이 무겁고 끈적이기 쉬운데 라온 헤어 오일 에센스는 오일이지만 가벼운 사용감에 바로 머리카락에 흡수되고 끈적임이 적어 부담 없이 매일 사용하기 좋아요. 머리를 감고 타월로 물기를 제거 후 적당량을 덜어 바르면 전체적으로 차분하면서도 윤기가 돌고 부드러운 머리카락을 느낄 수 있어요. 기획세트로 본품 100ml에 작은 30ml 사이즈가 같이 들어있어 여행 갈 때나 평소 백에 간단히 넣어 다니기 좋아
- `NEW-DESC-000182` / hash `197aae230ede76ea` / oliveyoung / product `A000000213261` / review `67812526`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 청미정 다시마 샴푸로 두피는 개운하게, 머릿결은 산뜻하게 관리하기 좋아요. 500ml라 넉넉하고 문어괄사까지 있어 두피 케어하는 시간이 더 즐거워졌어요. 데일리 샴푸로 만족합니다!
- `NEW-DESC-000066` / hash `19f1d2ae1b3bc7df` / elevenst / product `4445285171` / review `518767131`
  - signals: ingredient_or_spec, usage_instruction
  - snippet: 30수 대나무섬유 170g 뱀부타월 두껍진않지만 세탁전 첫 느낌 부드럽고 세탁 후 물기흡수도 좋을것으로 예상 후기 수정할게요. 드럼이라서 세탁 주의사항 지키려구요
- `NEW-DESC-000183` / hash `1a42c67030ac9044` / oliveyoung / product `A000000213261` / review `67745900`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 평소 사용하는 샴푸는 매일 손이 가는 제품이라 용량과 사용 편의성을 중요하게 생각하는데, 청미정 다시마 샴푸는 500ml라 여유 있게 사용할 수 있어 좋네요~ 샴푸할 때 두피를 꼼꼼하게 마사지하면서 사용하기 좋고, 깨끗하게 헹궈낸 뒤의 개운한 마무리감도 좋고 기획 구성에 문어괄사가 포함되어 있어 두피 관리에 관심 있는 분들에게 실용적인 조합인 것 같아요! 샴푸 하나만 사용하는 것보다 두피 마사지까지 함께 신경 쓸 수 있다는 점
- `NEW-DESC-000184` / hash `1a7389461cb43283` / oliveyoung / product `A000000238525` / review `66312182`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 🧴 정확히 어떤 제품인가요? 이 제품은 바이오가(BIORGA) 등드름 바디워시 베타인살리실레이트 1,000mL입니다. 이 세트에는 바이오가 백 바디 클리어 미스트 20mL가 함께 들어 있습니다. 올리브영에서도 현재 같은 1,000mL + 20mL 미스트 기획 구성을 판매하고 있습니다. 제품의 핵심은 일반적인 향 좋은 바디워시라기보다 등·가슴의 피지, 각질, 트러블성 피부를 관리하는 기능성 바디워시라는 점이에요. 브랜드 측에서도
- `NEW-DESC-000185` / hash `1acab63b7647e86a` / oliveyoung / product `A000000175385` / review `13667885`
  - signals: ingredient_or_spec, product_description
  - snippet: 블랙헤드까지 같이 케어해주는 클렌징오일인데 기름지지않고 마무리까지 깔끔합니다. 원래 밤타입을 쓰곤했는데 기름기가 가시질않아서 사용후에 찝찝함을 느껴서 다시 클렌징오일로 갈아타게된건데 이거 마무리감이 기름지지않고 깔끔해요 블랙헤드랑 피지케어도 같이되니깐 일석이조템이라고 느껴지네요 30ml짜리까지 같이 세트로 구성되서 이득이여서 기분좋습니다
- `NEW-DESC-000186` / hash `1ace3c3cc283c5d2` / oliveyoung / product `A000000130713` / review `36495379`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 평소 치아미백에 신경쓰고 있었는데 좋은 제품을 만난거 같아 좋아요 2중 화이트닝 케어로 치아 변색층을 제거하는데 도움을 줘서 사용하면서 점점 밝아지는 치아에 미소 지을 때 자신감을 되찾았어요 부드러운 사용감으로 매일 매일 자주 사용해도 부담이 없어서 데일리 사용가능한 미백치약이네요 프랑스 Eco-Cert 인증 받은 유기농 캐모마일 성분을 함유해서 엄청 부드러운 사용감의 미백치약이에요 추천드려요!
- `NEW-DESC-000187` / hash `1b2b10690efbf6b6` / oliveyoung / product `A000000223191` / review `45686263`
  - signals: product_description, benefit_claim
  - snippet: 선크림 깨끗하게 세정하고 싶어서 클렌징 오일을 꼭 사용하는데 바이오던스가 유화가 빠르고 가벼운데 모공탄력까지 케어한다고 해서 골랐어요. 오일치고 정말 가벼워요. 제형이 산뜻한 타입이라 그런지 유화가 정말 빠르고 잔여감이 없어서 완전 좋음! 오 솔직히 좀 놀랐음. 이렇게 산뜻하다고? 리무버 안해도 포인트 메이크업도 잘 지워지고 눈가 자극없어서 민감한 피부도 사용하기 좋아요. 피부결도 정돈되고 콜라겐 덕분인지 뭔가 피부가 탱탱한 
- `NEW-DESC-000188` / hash `1be038e91be477c9` / oliveyoung / product `A000000252917` / review `64267914`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 피부 뒤집어졌을 때 구원투수 같은 존재임ㅠㅠ 진심 내 상비템이야.. 얼굴에 트러블 났거나 자극받아서 빨갛게 달아올랐을 때 듬뿍 바르고 자면 다음 날 아침에 붉은기도 많이 가라앉고 피부 결이 급속도로 편안해지는 게 느껴짐. 제형이 살짝 꾸덕하고 연고 같은 느낌이긴 한데 흡수시켜주면 답답하지 않고 싹 감싸주는 느낌이라 밤마다 듬뿍 바르기 딱 좋음. 손상된 피부 장벽 케어하는 데는 이것만한 걸 못 봤다.. 용량도 100ml 기획이라
- `NEW-DESC-000189` / hash `1c33663b039abd19` / oliveyoung / product `A000000114263` / review `44670349`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 🤍일리윤 세라마이드 아토6.0 탑투토워시🤍 옵션: [헬로키티에디션] 500+리필500+굿즈 일단 본품과 같은 리필도 500ML 증정되서 완전 쟁여야 할 제품 중 하나! pH 약산성 올인원 워시로 저자극이고, 무향 포뮬러로 영유아도 사용한 제품이에요! 머리부터 발끝까지 사용이 가능한 제품으로 헤어, 바디, 얼굴 모두 한 번에 깔끔 클렌징이 가능해요 아기 목욕용이나 수영장이나 헬스장 갈때 챙겨가기 좋아요! 소프트 젤타입에 풍성한 
- `NEW-DESC-000190` / hash `1c936ebbf44e738d` / oliveyoung / product `A000000246272` / review `66087512`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 요즘 피부톤이 칙칙해 보이고 기미나 잡티도 신경 쓰여서 피부 관리를 좀 더 제대로 해보려고 챙겨 먹기 시작한 스킨 밸런스 파우더 레몬맛 🍋 이 제품은 피부톤과 기미·잡티 케어에 도움을 줄 수 있는 피에스트로가 들어있는데, 피부 밝기가 3700% 증가한 결과가 확인됐다고 해서 더 관심이 갔어요. 또 피부 컨디션을 전반적으로 관리하고 싶을 때 챙기기 좋은 아연도 함유되어 있어서 트러블이나 피부결 등 평소 피부가 신경 쓰이는 분들에
- `NEW-DESC-000191` / hash `1c9a97dff113e097` / oliveyoung / product `A000000246124` / review `56174593`
  - signals: ingredient_or_spec, product_description
  - snippet: 샤워할 때마다 내 몸에서 퍼지는 달콤한 생무화과즙 향 덕분에 힐링 되는 기분이에요. 핑크빛 오로라 젤 제형이 시각적으로도 즐겁고, 거품도 풍성하게 잘 납니다. 아이슬란드산 씨솔트와 핀란드산 자작나무 수액 등 북유럽의 청정 자연 성분이 담겨있어있다니!! 피부가 한결 건강해지는 느낌이에요. 특히 자연 유래 AHA, BHA 성분이 함유되어 있어 데일리로 부드럽게 노폐물을 세정하기 좋고, 사용 후에는 피부 결이 정돈되어 매끈한 결광 
- `NEW-DESC-000192` / hash `1cb083133406f398` / oliveyoung / product `A000000188024` / review `68055714`
  - signals: product_description, benefit_claim
  - snippet: 부드럽고 하얀 밀크 타입의 에센스가 건조한 피부에 깊은 영양감과 탄력을 부여해 줍니다. 일반 워터 제형의 팩들과 달리 묵직하고 탄탄하게 보습 장벽을 세워주는 느낌이라 찬 바람 부는 계절에 쓰기 딱 좋아요. 시트가 쫀쫀하게 밀착되면서 얼굴을 긴장감 있게 잡아주어 사용 후 만져보면 피부가 말랑하고 탱글해진 게 느껴집니다. 영양이 풍부함에도 트러블 유발 없이 순하게 잘 맞아서 유독 피로해 보이는 날 밤마다 영양 보충용으로 애용해요.
- `NEW-DESC-000193` / hash `1d09d0ec6e2dd82b` / oliveyoung / product `A000000212210` / review `33086967`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 속눈썹 연장을 자주하다보니 속눈썹이 손상되어서 숱(?)이 줄어드는게 보여서 구매하게 되었어요! 이 제품은 모근 건강에 도움을 주는 핵심성분인 2가지와 영양공급에 도움을 주는 펩타이드 3가지 성분이 함유되어있는 유명한 제품이더라구요! 그리고 15ml인 대용량👍🏻 크고 양이 많아서 2달은 거뜬히 사용할 수 있을 것 같더라구요ㅎㅎ 그리고 바르고 나서 눈시림, 따가움도 없어서 더 대만족이에요!
- `NEW-DESC-000194` / hash `1d6754bc618ebc15` / oliveyoung / product `A000000268739` / review `67560161`
  - signals: product_description, benefit_claim
  - snippet: 스칼렛 언니랑 개발한 립밤이어서 더욱 관심이 갔어용!! 착색케어할 수 있는 립밤은 처음 사용해보는거라 반신반의했는데 확실히 효과가 좋은 것 같습니다!
- `NEW-DESC-000195` / hash `1e63ba90ba6b6332` / oliveyoung / product `A000000190494` / review `64695714`
  - signals: ingredient_or_spec, product_description
  - snippet: 🍓에스네이처 아쿠아 라이스 약산성 클렌징폼 160ml 기획 한 달 후기🍓 ​ ■제품특징 여주 고아미쌀 추출물과 쌀가루, 팥 및 당호박 추출물을 담은 약산성 비건 클렌징폼입니다. 쫀쫀한 크림 제형이 거품으로 바뀌며 노폐물과 잔여물을 세정해 주며, 인공 향료를 배제하여 부담을 줄였습니다. 본품 160ml와 추가 20ml, 세안용 헤어 찍찍이가 결합된 패키지입니다. ​■제품장점 한 달간 사용하면서 피부 밸런스를 편안하게 유지하는 데
- `NEW-DESC-000196` / hash `1ed17054d54353cf` / oliveyoung / product `A000000222781` / review `65578967`
  - signals: ingredient_or_spec, product_description
  - snippet: 🥊[케어플러스] 상처 커버 스팟 패치 72매 + 헬로키티 PVC/ 파우치🥊 ​[구매이유] 사용하지도 않고 얼굴에 뭐가 나서 짤일은 없지만 순전히 키티파우치 때문에 구매함. ​■제품장점 ​케어플러스 상처 커버 스팟 패치 제품 자체는 오랫동안 코덕들에게 검증받은 대표 스팟 케어 라인업임. ​기능성과 원단 퀄리티 면에서 전체적인 완성도가 대단히 뛰어남. ​하이드로콜로이드 재질이 적용되어 스팟 부위의 진물과 삼출물을 신속하게 흡수함.
- `NEW-DESC-000067` / hash `1ee97a50fb5892e4` / elevenst / product `9034967045` / review `543968313`
  - signals: usage_instruction, benefit_claim
  - snippet: 종근당 랏토핏 골드(유산균) 150포는 잘 도착했습니다. 도착하자마자, 섭취하였습니다. 랏토핏 골드(유산균)을 선택한 이유는 장시간 의자에 앉아 생활하는 분, 장내 유산균이 감소하는 노년층,등 "온 가족에 추천합니다" 라고, 해당 문구가 있어 선택했습니다. 락토핏 골드 유산균을 섭취량 및 섭취방법 따라 복용하였습니다. 하루에 한 번 섭취하였습니다. 물 없이 섭취하였습니다. 유산균 가루 맛은 달고 맛있습니다. 거부감은 전혀 없습
- `NEW-DESC-000197` / hash `1fd9629a4597622f` / oliveyoung / product `A000000218338` / review `64285568`
  - signals: product_description, benefit_claim
  - snippet: 24. 츠바키 프리미엄 볼륨 & 리페어 샴푸 * 머리를 감은 후 깔끔하고 산뜻하게 정돈하기 좋아요. * 볼륨과 손상 케어를 함께 신경 쓰고 싶은 분들에게 잘 맞을 것 같아요. * 향도 은은하게 남아서 샤워 후 기분이 좋아지는 느낌이에요. * 여러 용량으로 구성되어 있어 사용하기 편리해요. * 모발 관리와 볼륨을 함께 챙기고 싶은 분께 추천해요.
- `NEW-DESC-000198` / hash `209cb10048514a46` / oliveyoung / product `A000000130970` / review `11088221`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 워셔블 마스카라 찾기 힘들고 거희 없어서 올영에서 마스카라 이것저것 보다 알게 되어 샀어요 매일 화장을 하진 않지만 가끔씩 마스카라를 하는데 워터프루프는 지울때 너무 번거롭게 잘 안지워지고 여러번 지우게 되고 이러면 피부도 상하고 그래서 워셔블이 좋을 것 같아서 처음으로 샀는데 미온수로 잘지워지고 클렌징이 편해졌어요 롱앤컬하고 볼륨앤컬 두 가지 있는데 제가 산건 롱앤컬인데 마스카라 브러쉬가 살짝 C컬 브러쉬고 얇고 촘촘한 솔이
- `NEW-DESC-000068` / hash `215962b326986041` / elevenst / product `2928566919` / review `449317934`
  - signals: ingredient_or_spec, product_description
  - snippet: 받은 제품의 문에 대한 3가지 문제가 있었는데 첫번째가 정면에서 봤을때 문이 3mm 정도 왼쪽으로 삐뚜러져 있었고(첫번째~세번째사진) 두번째는 문이 완전히 닫히지 않는것(네번째~여섯번째사진), 세번째는 한곳이 미세하게 찌그러져(일곱번째 사진) 들어가 있었습니다. 그래서 카톡 상담했더니 첫번째와 세번째문제는 엉급도없고 두번째 문제에 대한 황당한 답변만 하였습니다(여덜번째 사진). 다른분들 리뷰중에 열이 옆으로 샌다는것이 이거였구
- `NEW-DESC-000199` / hash `21b6f6f06e187c7b` / oliveyoung / product `A000000225736` / review `68010235`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 4~5통 이상은 비운 인생템입니다. 날 다 했지요~ My 피부 타입: 여름 - 지성, 그외 - 수분 부족 지성 순하기는 합니다. 그렇다고 해서 자극이 0%냐 라고 하면 당연히 아닙니다. 사용 후 스킨 케어는 반드시 수분 + 진정으로 하셔야 내일 아침에도 요철 하나 없는 예쁜 피부를 유지할 수 있어용
- `NEW-DESC-000200` / hash `221eaaa3877ca59a` / oliveyoung / product `A000000207738` / review `55974140`
  - signals: usage_instruction, benefit_claim
  - snippet: 반곱슬머린데 네이밍이 스트레이트라던가 반곱슬탈출이라던가..너무 강요해서 혹했는데 스트레이트도 반곱슬탈출도 안됩니다..그냥 안돼요ㅠ 설명란에도 보면 바르고 고데기를 해야 사진처럼 쫙 펴지는 거지 발라서 드라이한다고 달라지는 건 아닙니다ㅜ 근데 웃긴 건 사용법에는 또 젖은머리에 적당량 바르고 말리기만 하면 매끈하고 차분한 슬릭헤어완성이래유ㅠ 어디서부터 잘 못 된거랭ㅜ 그냥 열보호를 강조하길래 열보호가 된다에 의의를 두고 쓰는 게 
- `NEW-DESC-000069` / hash `2268706e7306dd4f` / elevenst / product `1964216253` / review `404999344`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 받고나서 한주간 꾸준히 복용했습니다. 우선 용량은 270정으로 상당히 넉넉한 용량입니다. 한 알의 사이즈가 크지 않아서 먹기가 매우 좋아요. 맛과 향이 옛날 어린시절에 먹던 원기소였던가? 그 냄새와 상당히 흡사했어요. 덕분에 먹기엔 수월했는데 씹어서 섭취 할 용기는 아직 없어서 삼키고 있습니다. 일주일의 복용으로 드라마틱한 효과는 없지만 워낙 머리카락이 가늘어서 선택했기에 꾸준한 복용으로 좋은 효과가 있길 바래봅니다. 여성용 
- `NEW-DESC-000201` / hash `235d899dc759dc43` / oliveyoung / product `A000000268771` / review `67980702`
  - signals: product_description, benefit_claim
  - snippet: 비타민을 고를 때 단순히 함량만 보는 것보다 어떤 제형으로 만들어졌는지도 살펴보고 구매하면 좋다고해서 고민하고 비교하게되네요 이번에는 생체 흡수율을 높인 리포좀 제형기술이 적용된 제품을 찾아보다가 픽하게 됐구요 하루 한 알로 필요한 비타민과 미네랄을 간편하게 보충할 수 있고 여러 제품을 복잡하게 챙기지 않아도 요거하나면 충분해서이것저것 챙기지 않아도되네요 인증시설에서 제조했다는 점도 선택할 때 참고했고 섭취 방법도 간단하고 찬
- `NEW-DESC-000202` / hash `23efb3d1896cc16d` / oliveyoung / product `A000000184496` / review `66427998`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 피부에 착 밀착되는 하이드로겔 시트라 에센스가 흐르지 않고 촉촉함이 오랫동안 유지돼요. 어성초, 수분초, 부활초 3종이라 피부 컨디션에 따라 진정, 수분, 영양 케어로 골라 쓰기 너무 좋아요. 콜라겐 성분 덕분에 사용 후 피부가 탱탱해지고 속건조까지 잡아주어 매끈한 윤광이 도는 게 느껴지네요. 끈적임 없이 깔끔하게 스며들어 홈케어용으로 제격이라 세일할 때 종류별로 쟁여두시는 걸 추천해요!
- `NEW-DESC-000203` / hash `242f83f39823fc61` / oliveyoung / product `B000000200520` / review `55587353`
  - signals: ingredient_or_spec, product_description
  - snippet: ✔ 끈적임 없이 산뜻한 오일 타입 ✔ 손상모 끝부분 정돈에 효과적 ✔ 은은한 플로럴 향으로 기분 좋은 마무리 ✔ 휴대용 10ml 추가 증정으로 실용적 염색이랑 드라이를 자주 하다 보니 머리 끝이 푸석하고 갈라져서 고민이었는데, 이 헤어 에센스 오일 사용하고 나서 확실히 차분해졌어요. 투명한 오일 제형인데 생각보다 가볍게 발려서 손에 남는 끈적임이 거의 없고, 모발에 빠르게 흡수되는 느낌이에요. 타월 드라이 후 젖은 모발에 한 
- `NEW-DESC-000204` / hash `247cacf4798960b6` / oliveyoung / product `A000000231315` / review `66711143`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 메이크업 세정과 폼 클렌징을 한 번에 해결해 주는 프리메라 마일드 앤 퍼펙트 클렌징 오일 투 폼입니다! 처음에는 오일 형태로 부드럽게 문질러 메이크업과 모공 속 노폐물을 녹여주고, 물이 닿으면 미세하고 풍성한 거품으로 바뀌어 이중 세안 필요 없이 깔끔하게 세안돼요. 세안 후에도 피부 당김 없이 촉촉함이 유지되며, 200ml 본품에 200ml 리필까지 더해진 1+1 구성이라 가성비와 제품력 모두 완벽한 클렌저입니다.
- `NEW-DESC-000205` / hash `24a356871597eed1` / oliveyoung / product `A000000155458` / review `66751699`
  - signals: ingredient_or_spec, product_description
  - snippet: 도브 바디워시 상세 리뷰 1. 향 및 제형 (질감) * 조밀하고 풍성한 거품 제형: 적은 양으로도 생크림처럼 쫀쫀하고 밀도 높은 거품이 풍성하게 일어나 피부를 부드럽게 감싸줍니다. * 취향을 사로잡는 시그니처 향: * 뷰티 모이스처 / 딥 모이스처: 도브 특유의 포근하고 깨끗한 비누 향(파우더리한 살냄새)으로 호불호 없이 온 가족이 쓰기 좋습니다. * 고 프레시 (오이&녹차 / 자몽 등): 상큼하고 청량한 향으로 여름철이나 운
- `NEW-DESC-000206` / hash `2507a148b9e90caf` / oliveyoung / product `A000000243918` / review `45210408`
  - signals: ingredient_or_spec, usage_instruction
  - snippet: 슬림쏙씬덱스3500 LlKE EAT를 두개를 구입했어요 몇개밖에 없어서 사러와 사고 싶었던 제품이 세일가로 안해 할수없이 슬림쏙을 남은 싹다 구입했어요 부침개나 부추전위에 뿌려먹을까 그런 생각을 했는데~....식후에 먹으면 될것같아 얼른 집에 가기전에 비옷을 샀어요 갑자기 비 와서 우산도 못 챙겨 후다닥~...비가 와서 비옷입고 집에 왔지만 사 왔던 기름 진걸 먹으면 속이 느글거려 슬림쏙 먹으면 덜 해요 아니면 물과 같이 먹으
- `NEW-DESC-000207` / hash `254ef0c51044f361` / oliveyoung / product `A000000248463` / review `37084519`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 바이탈뷰티 제품은 항상 믿고 먹는 것 같아요 건강보조제들이 으례 그렇듯 큰 효과가 있는 것 보다는 꾸준히 먹어주면 효과가 있기를 바라면서 먹는 제품입니다. 0.6cm 정도로 작은 타블렛 제형이고, 약간 갈색빛이 돕니다. 침에 닿으면 녹아서 약간 씁쓸한 맛이 나오니 바로 삼키는 것이 먹기에는 더 편해요 왠만한 다른 제품들보다 먹기 편하게 작은 제형이라서 좋은 것 같아요 꾸준히 먹으면 효과를 볼수 있겠죠?
- `NEW-DESC-000208` / hash `25545deffb245a55` / oliveyoung / product `A000000249292` / review `57619219`
  - signals: product_description, benefit_claim
  - snippet: 최근 두피가 땡기고 모발이 힘 빠진 느낌이 들어서 릴리이브 그로우턴 엑소좀 캡슐 트리트먼트를 써보게 됐어요. 두피부터 모발까지 케어하는 2in1 트리트먼트라서, 탈모 관리용 샴푸랑 같이 쓰기 좋겠다 싶었어요. 사용 느낌은 일단 묽지 않고 묵직한 크림 텍스처인데, 생각보다 뻑뻑하지 않고 잘 퍼져서 두피에 잘 흡수되는 편이에요
- `NEW-DESC-000209` / hash `25af60f3122f371e` / oliveyoung / product `A000000235186` / review `53176959`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 릴리이브 스칼프턴 시카 PDRN 딥클린 샴푸후기 🧩용량 : 대용량500g+소용량100g 기획. 🧩가격 : 16000원대. 🧩색상 : 연두색에 가까운 올리브 그린. 🧩권장두피 : 지루성 두피염, 지성두피, 복합성두피 비듬두피, 간지러운 두피. 🧩권장계절 : 사계절 가능. 🧩향 : 프레쉬 민트향으로 시원하면서 순한 허브향. ●구매이유-저녁만 되면 머리가 기름지고 두피가 피곤하고 간지러운 느낌 들어서. ■제품장점 및 특징 - 🎄지루
- `NEW-DESC-000210` / hash `261e90522920d1a9` / oliveyoung / product `A000000260483` / review `66126038`
  - signals: ingredient_or_spec, usage_instruction
  - snippet: 사용 전에 충분히 흔들어 분사하면 미세한 안개 입자가 피부에 고르게 밀착되어 메이크업 위에 뿌려도 뭉치거나 번지지 않았습니다. 피부 속은 촉촉하게 채워주면서 겉은 자연스럽게 윤기가 살아나 과한 번들거림 없이 은은한 속광 피부를 표현해줬어요. 건조함이 느껴질 때마다 가볍게 뿌려주면 피부가 한층 생기 있어 보이고 메이크업도 더욱 자연스럽게 유지되었습니다. 50ml의 휴대하기 좋은 사이즈라 외출 시 가지고 다니며 사용하기에도 편리했
- `NEW-DESC-000211` / hash `265fe35831ef95d4` / oliveyoung / product `A000000251932` / review `62395109`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 단순히 모공을 인위적으로 메우는 느낌이 아니라, 피부 본연의 결을 매끄럽게 정돈해 주는 데 집중한 성분 배합이 돋보여요. 피부 장벽 케어 성분: 연작 특유의 식물 추출 성분들이 함유되어 있어, 메이크업 전 피부 기초 체력을 탄탄하게 다져주고 외부 자극으로부터 피부를 보호하는 데 도움을 줍니다. 사일런트 벨벳 제형: 처음 손끝에 덜어내었을 때는 수분감이 느껴지는 촉촉한 리퀴드 제형인데, 피부에 펴 바르는 순간 신기하게도 아주 가
- `NEW-DESC-000126` / hash `26670b45e43df3c4` / musinsa / product `2758160` / review `85674541`
  - signals: usage_instruction, benefit_claim
  - snippet: 🌳피부타입 : 복합성 (T존과 턱부분은 기름기가 많고 블랙헤드 및 화이트 헤드가 있음 / 볼이나 관자놀이는 수부지에 가까움) 🌳사용방법 : 약산성으로 가볍게 세안 후 토너를 발라 흡수 시킨 다음 T존과 턱에 적은 양을 사용함 / 이를 2~3일 1번 저녁에 사용 🌳효과 : 확실히 화이트헤드와 블랙헤드에 효과가 있어 보임 다만 각질 제거제인 만큼 피부 자극이 심해 추후 진정효과가 있는 세럼이나 크림을 사용함 🌳추천대상 : 블랙헤드
- `NEW-DESC-000212` / hash `26ad89ad0dfd2ddb` / oliveyoung / product `A000000138140` / review `27276902`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 샴푸처럼 꾸~덕하니 나와요🤍 샤워볼에 코를 가까이 두고 킁킁하면 포근한 향이 폴폴 스크럽이랑 섞어서 문지르는 방법도 있더라구요? 집에 있는 거랑 같이 써봐야겠어요 한방에 씻어낼 수 있어서 편할 것 같음🤭 포근한 향이라서 남친선물용으로도 괜찮을 것 같아요 500g이라서 묵직하니 양 넉넉하고 욕실에 두었을 때도 깔끔! 샤워볼에 한 번 펌핑해도 거품 쫀쫀하고 급하게 로션바르지 않아도 몸이 촉촉한 게 느껴져요 바디제품 안 맞거나 하면
- `NEW-DESC-000213` / hash `27883da9b55ffa93` / oliveyoung / product `B000000167559` / review `44824844`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: ✅ 높은 단백질 함량 운동하는 분들이나 단백질 섭취를 늘리고 싶은 분들에게 최적화된 제품입니다. 한 팩에 약 25g 이상의 단백질이 함유되어 있어 근육 유지와 회복에 도움을 줍니다. ✅ 간편한 조리법 전자레인지나 뜨거운 물에 간단히 데우기만 하면 바로 먹을 수 있어 바쁜 아침이나 운동 후 식사 대용으로 매우 편리합니다. 냉장 보관만 해두면 언제든 빠르게 준비할 수 있습니다. ✅ 맛과 풍미 블랙페퍼 시즈닝 덕분에 일반 닭가슴살 
- `NEW-DESC-000214` / hash `2829209efa983407` / oliveyoung / product `A000000240243` / review `12929665`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: ✔️섞을 필요 없는 모델링팩(근데 모델링이랑 좀 다른 느낌) ✔️크림같은 앰플이 들어있어 하나만 해도 보습력 커요 ✔️반값 할인 7천원 구매 🥺쿨링감은 글쎄? 🥺성분이 그닥이에요ㅠ 🥺인중 모델링팩이 자꾸 흘러내려요 전직 피부관리사입니다. 모델링팩 남의 얼굴에 많이 붙여줘봤지 제 얼굴에 셀프로는 안했는데 모델링파우더도 사고 이렇게 그냥 붙이는 것도 사봤어요! 반값 하길래 샀눈데 그냥 집에 있는 앰플이랑 에센스 떡칠하고 이거 올리
- `NEW-DESC-000215` / hash `2878ec7f5e530bfb` / oliveyoung / product `A000000140183` / review `67778181`
  - signals: usage_instruction, benefit_claim
  - snippet: 모발이 푸석해 보이거나 스타일링 후 차분하게 정리하고 싶을 때 활용하기 좋은 헤어 오일 에센스예요. 샴푸 후 타월 드라이를 한 상태에서 모발 중간부터 끝부분까지 소량을 발라 주면 드라이 전에 모발을 관리하기 편리해요. 이미 머리를 말린 뒤에도 끝부분에 조금 발라 정돈할 수 있어요. 다만 한 번에 너무 많이 사용하면 머리카락이 무겁거나 기름져 보일 수 있으니 적은 양부터 시작하는 것을 추천해요. 향을 중요하게 생각하는 분들은 리
- `NEW-DESC-000216` / hash `294ad2ec9dcff95b` / oliveyoung / product `A000000254191` / review `67761801`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 집에서 꾸준히 헤어 케어하기 좋은 대용량 트리트먼트예요. 샴푸 후 모발에 바르고 헹구는 방식이라 사용법이 간단하고, 990ml라 자주 사용하는 분들도 넉넉하게 쓸 수 있습니다. 극손상 모발용 에센스팩 타입이라 모발을 관리하고 싶을 때 샤워 루틴에 더하기 편했어요.
- `NEW-DESC-000217` / hash `29a2fe37f3324dab` / oliveyoung / product `A000000242173` / review `54940189`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 평소 피부 관리에 무심한 남자친구에게 선물했어요. 남친이 &#34;끈적이지 않는데 속은 촉촉하다&#34;며 좋아해요. 특히 면도 후 예민해진 피부가 금방 진정되는 게 눈에 보여서 제가 더 뿌듯하더라고요. 120g에 30g 추가 증정 구성이라 가성비도 훌륭하고, 귀찮은 거 싫어하는 남자들에게 딱이예요
- `NEW-DESC-000218` / hash `2a46f12be329e215` / oliveyoung / product `A000000212210` / review `33177622`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 해외에서 난리난 속눈썹 영양제라니 ! 올영 출시하자 마자 1위된거 대박 !! 그리고 제품 뜯자마자 손에 딱 쥐면 묵직함이 뭔가 엄청 고급스러워요 ㅎㅎ 고농축 영양 공급되며 특허성분이 무려10종이나 ! 눈시림 전혀 없고 15ML 대용량 사이즈라서 2개월 거뜬하게 사용가능해여 ㅎㅎ 앞부분은 뭉텅하고 안쪽에는 솔로 되어있어서 속눈썹에 터치할때 엄청 편하고 좋더라구용 ~ 아침 저녁으로 꾸준히 발라서 속눈썹 많이 자랐으면 좋겠어요 &g
- `NEW-DESC-000219` / hash `2a650b8d03889033` / oliveyoung / product `A000000260329` / review `67800703`
  - signals: ingredient_or_spec, benefit_claim
  - snippet: 세라마이드와 히알루론산이 들어 있는 수분 세럼이라 보습 관리용으로 골랐어요. 수분 공급과 피부 장벽 관리를 함께 기대할 수 있는 구성이 마음에 들고, 분홍색 패키지도 예뻐요. 용량은 30ml라 크기가 부담스럽지 않네요. 보습 제품은 꾸준히 써보는 게 중요할 것 같아서 기초 관리에 활용해보려고 해요!
- `NEW-DESC-000127` / hash `2aec2d07f7e45d9b` / musinsa / product `5031928` / review `87812800`
  - signals: ingredient_or_spec, product_description
  - snippet: 시카 PDRN 성분이 함유되어 있어서 진정 효과는 물론이고, 피부 속부터 수분과 영양이 탄탄하게 채워지는 느낌을 받았습니다. 쫀득하면서도 부드러운 크림 제형이 겉돌지 않고 밀착력 있게 흡수되어 속건조를 깔끔하게 잡아주더라고요. 꾸준히 발라주니 칙칙했던 피부 톤도 한결 맑아지고 붉은기나 자국 같은 흔적들이 편안하게 정돈되는 게 느껴집니다. 자극 없이 순한 편이라 아침저녁 데일리로 부담 없이 펴 바르기 딱 좋아요. 피부 탄력 저하

## Interpretation and safety

- 후보 수나 플랫폼 비율을 실제 suspicious 비율로 해석하지 않습니다.
- 리뷰 길이는 metadata일 뿐 tier 판정에 사용하지 않았습니다.
- 동일 normalized content는 identity와 무관하게 한 행만 deterministic하게 선택했습니다.
- candidate ID는 tier, platform, stable content SHA-256 정렬 후 부여했습니다.
- human_label과 review_note는 빈 칸이며 자동 SUSPICIOUS/NORMAL/UNCERTAIN 값을 넣지 않았습니다.
- 모델, embedding, fuzzy similarity, LLM labeling 또는 training을 실행하지 않았습니다.
