# Human Review Candidate Precision Audit

> 후보 source/prototype provenance이며 정답 라벨이 아닙니다. human_label과 human_note는 모두 비어 있습니다.

## Scope

- Canonical full index: **1,151,943**
- Expansion scan: canonical candidate-content **180,900**건 (raw 6개 CSV가 현재 경로에 없어 full-corpus expansion은 미실행)
- Existing source audit rows: **881**
- Expanded audit rows: **271**
- Total audit rows / unique row_uid: **1,152 / 1,120**

## Audit counts

| section | rows |
| --- | ---: |
| EXISTING::EXTREME_RESULT_CLAIM | 37 |
| EXISTING::IMMEDIATE_EFFECT_CLAIM | 10 |
| EXISTING::PRODUCT_DESCRIPTION_REPLACEMENT | 100 |
| EXISTING::PROMOTIONAL_TEMPLATE | 100 |
| EXISTING::LOW_INFORMATION_PRAISE | 84 |
| EXISTING::REPEATED_SHORT_TEMPLATE | 200 |
| EXISTING::EXACT_DUPLICATE_CLUSTER | 200 |
| EXISTING::HARD_NEGATIVE_CANDIDATE | 150 |
| EXPANDED::EXTREME_RESULT_EXPANDED_PROTOTYPE | 100 |
| EXPANDED::IMMEDIATE_EFFECT_EXPANDED_PROTOTYPE | 21 |
| EXPANDED::HARD_NEGATIVE_EXPANDED_CANDIDATE | 150 |

## Audit distribution

### Platform

| platform | rows |
| --- | ---: |
| elevenst | 357 |
| kurly | 216 |
| musinsa | 147 |
| naver | 16 |
| ohouse | 7 |
| oliveyoung | 409 |

### Category

| category | rows |
| --- | ---: |
| BABY | 65 |
| BEAUTY | 346 |
| DIET | 17 |
| ELECTRONICS | 83 |
| ETC_UNKNOWN | 57 |
| FASHION | 85 |
| FOOD | 147 |
| HEALTH_SUPPLEMENT | 111 |
| LIVING | 137 |
| PET | 50 |
| SPORTS_OUTDOOR | 54 |

## Expansion prototype

### EXTREME_RESULT_EXPANDED_PROTOTYPE

- total: **180** / existing overlap: **11** / expanded-only: **169**
- platforms: `{'elevenst': 18, 'kurly': 3, 'musinsa': 5, 'oliveyoung': 154}`
- categories: `{'BEAUTY': 162, 'FASHION': 1, 'FOOD': 1, 'HEALTH_SUPPLEMENT': 8, 'LIVING': 7, 'PET': 1}`

### IMMEDIATE_EFFECT_EXPANDED_PROTOTYPE

- total: **37** / existing overlap: **2** / expanded-only: **35**
- platforms: `{'elevenst': 14, 'oliveyoung': 23}`
- categories: `{'BEAUTY': 22, 'HEALTH_SUPPLEMENT': 3, 'LIVING': 12}`

### HARD_NEGATIVE_EXPANDED_CANDIDATE

- total: **11,084** / existing overlap: **801** / expanded-only: **10,283**
- platforms: `{'elevenst': 1331, 'kurly': 676, 'musinsa': 329, 'naver': 4, 'ohouse': 9, 'oliveyoung': 8735}`
- categories: `{'BABY': 240, 'BEAUTY': 8380, 'ELECTRONICS': 95, 'ETC_UNKNOWN': 47, 'FASHION': 157, 'FOOD': 1567, 'HEALTH_SUPPLEMENT': 243, 'LIVING': 231, 'PET': 82, 'SPORTS_OUTDOOR': 42}`
- expanded-only platforms: `{'elevenst': 1292, 'kurly': 638, 'musinsa': 319, 'naver': 4, 'ohouse': 8, 'oliveyoung': 8022}`
- expanded-only categories: `{'BABY': 230, 'BEAUTY': 7688, 'ELECTRONICS': 90, 'ETC_UNKNOWN': 45, 'FASHION': 156, 'FOOD': 1530, 'HEALTH_SUPPLEMENT': 197, 'LIVING': 223, 'PET': 82, 'SPORTS_OUTDOOR': 42}`
- oliveyoung 비율: 기존 `1,785 / 1,992 = 89.61%`, expanded-only `8,022 / 10,283 = 78.01%`, 기존+expanded-only union `9,807 / 12,275 = 79.89%`

## Duplicate audit composition

- REPEATED_SHORT frequency buckets: `{'2-4': 65, '20+': 38, '5-9': 51, '10-19': 46}`
- EXACT frequency buckets: `{'5-9': 60, '2-4': 66, '20+': 37, '10-19': 37}`
- EXACT scopes: `{'CROSS_PRODUCT_SAME_PLATFORM': 87, 'SAME_PRODUCT': 52, 'CROSS_PLATFORM': 61}`

## Representative rows

전체 content와 blank human fields는 CSV에 있습니다.

| audit_id | source | platform | category | content preview |
| --- | --- | --- | --- | --- |
| PCA-00001 | EXTREME_RESULT_CLAIM | elevenst | FASHION | 소재가 그래서 그런가 화학 냄새가 쫌 나지만 페브리지 살짝 뿌리고 테라스에 하루 널어놨더니 싹 없어졌네요. 괜찮네요. 많이 파세요. |
| PCA-00002 | EXTREME_RESULT_CLAIM | elevenst | PET | 예전에는 비싼 수제 간식을 먹였었는데요, 자꾸 살이 찌더라구요. 쬐끄만한 소형견이라서 1.5kg이 정상 몸무게라는데 2.3kg까지 쪘어요. 체중이 많이 나가니 무 |
| PCA-00003 | EXTREME_RESULT_CLAIM | kurly | FOOD | 4개월 차인데 5kg 감량했어요 |
| PCA-00004 | EXTREME_RESULT_CLAIM | kurly | BEAUTY | 극건성, 속건조가 심해 고민하다 첫 사용해봤습니다. 개인적으로 끈적이는 엣센스를 좋아해서 제 기준에서는 200%만족입니다. 찬바람 불면서 양 볼과 입가가 건조했는 |
| PCA-00005 | EXTREME_RESULT_CLAIM | kurly | HEALTH_SUPPLEMENT | 멀쩡하다가 수영장만 다녀오면 다음날 갑자기 재치기와 콧물이 흘렀는데 이걸 먹으니까 증상이 싹 사라졌어요, 하루만 먹었는데 대박이에요!  알약 크기는 보통입니다.  |
| PCA-00006 | EXTREME_RESULT_CLAIM | oliveyoung | BEAUTY | 플루 퍼펙트 발 각질 케어 세트를 드디어 사용해봤습니다! 
 평소 건조하고 각질이 많은 발 때문에 고민이 많았는데
 이 제품 하나로 홈케어가 완벽하게 가능했어요. |
| PCA-00007 | EXTREME_RESULT_CLAIM | oliveyoung | BEAUTY | 스킨,로션으로 구성 된 제품 쓰다가 드디어 올인원으로 넘어왔네요. 제품이 워낙 다양해서 좀 살펴보다 아이오페 제품에다가 요즘 핫하다는 PDRN성분까지 함유돼 있다 |
| PCA-00008 | EXTREME_RESULT_CLAIM | oliveyoung | BEAUTY | 수부지이지만 피부 장벽 개박살 나서 끝까지 고민하다 결국 사버린 크림,,, 대만족입니다
 피부 벗겨지고 붉어짐이 너무 심해서 한여름에도 엄청 얇게 레이어링 해주니 |
| PCA-00009 | EXTREME_RESULT_CLAIM | oliveyoung | BEAUTY | 거품이 잘 안난다는 후기 있었는데 머리 흠뻑 잘 적셔주면 거품 아주 잘 납니다
 다만 감고나서 조금 많이 뻑뻑해서 꼭 트리트먼트를 해줘야하네요
 이 샴푸 쓰고 나 |
| PCA-00010 | EXTREME_RESULT_CLAIM | oliveyoung | BEAUTY | 꾸덕할줄 알았는데 완전 묽은 제형이더라구요! 처음 사용하시면 주의하셔야 할듯! 근데 하루만에 비듬 싹 사라졌어요! 저는 주에 한두번 정도 사용하는데 정말 만족합니 |
| PCA-00011 | EXTREME_RESULT_CLAIM | oliveyoung | BEAUTY | 저는 머리카락보다 두피 상태 때문에 샴푸를 바꾸게 되는 경우가 더 많은 편이에요.
 
 특히 계절이 바뀌거나 야근이 계속되면 두피가 괜히 답답하고 하얗게 각질처럼 |
| PCA-00012 | EXTREME_RESULT_CLAIM | oliveyoung | BEAUTY | 계속 사용하는 제품이라 세일할 때는 사서 쟁여두고 있습니다. 라우쉬 미역샴푸 좋다는 이야기 듣고 처음 사서 사용하기 시작했는데 지금 벌써 몇 통째 사용이네요. 
 |
| PCA-00013 | EXTREME_RESULT_CLAIM | oliveyoung | BEAUTY | &lt;건성 두피, 건강모의 대략 2달 사용 후기&gt;
 
 향, 세정력, 거품 양 : 매우 매우 매우 만족!!!
 
 +두피 가려움증이 종종 있었는데 이 샴푸 |
| PCA-00014 | EXTREME_RESULT_CLAIM | oliveyoung | BEAUTY | 저는 모발 손상이 꽤 심한 편이고 수개월째 복구가 되지 않고 있는데, 이 제품은 아침 저녁으로 사용한지 4일째인데 워터트리트먼트를 사용한것처럼 매우 매끄럽게 정돈 |
| PCA-00015 | EXTREME_RESULT_CLAIM | oliveyoung | BEAUTY | 환절기만 되면 온몸이 건조해서 가려웠는데, 이 바디로션을 한 달 동안 꾸준히 사용하고 나서 피부 고민이 싹 사라졌어요. 끈적임 없이 부드럽게 롤링되며 스며드는 텍 |
| PCA-00016 | EXTREME_RESULT_CLAIM | oliveyoung | BEAUTY | 추천⭐️X100 입니다.
 향 좋고 보습 좋은 바디로션 찾으시는 분 꼭 구매하세요 ㅠ-ㅠ
 + 향 오래가고 좋으면서 보습 좋은 바디로션을 찾고 있었는데 존슨즈베이 |
| PCA-00017 | EXTREME_RESULT_CLAIM | oliveyoung | BEAUTY | 낫포유
 🩵제 피부타입은 일단 등드름이 있는 상태였어요
 붉은 뾰루지 올라오고 종종 피지나, 간지럽거나, 아픈 여드름이 등에 올라오곤 했오요
 제가 탄수화물, 짠 |
| PCA-00018 | EXTREME_RESULT_CLAIM | oliveyoung | BEAUTY | 🩵제 피부타입은 일단 등드름이 있는 상태였어요
 붉은 뾰루지 올라오고 종종 피지나, 간지럽거나, 아픈 여드름이 등에 올라오곤 했오요
 제가 탄수화물, 짠것 많이  |
| PCA-00019 | EXTREME_RESULT_CLAIM | oliveyoung | BEAUTY | 이번 여름에 한 통 싹싹 비웠는데 만족스러웠음 ! 처음 개봉하고 썼을 당시에 한 일주일 썼나…등드름 큰거 두개 있었는데 싹 사라졌음,,,원래 알아서 사라지긴 하겠 |
| PCA-00020 | EXTREME_RESULT_CLAIM | oliveyoung | BEAUTY | 솔직 후기‼️
 가슴이랑 등에 트러블이 있는 편이라 사봤어요
 한 달 써봤는데 드라마틱하게 트러블 개선은 안됩니당
 그래도 전보단 가라앉긴 했어요!
 새로 올라오 |
| PCA-00021 | EXTREME_RESULT_CLAIM | oliveyoung | BEAUTY | [정착후기] 왁싱샵 원장님 추천템 &#039;라이콘&#039;, 이제 올리브영에서 편하게 구매해요! 💫
 
 ✨왁싱 좀 해본 분들이라면 다 아는 그 이름, 라이콘 |
| PCA-00022 | EXTREME_RESULT_CLAIM | oliveyoung | BEAUTY | 🍧동화약품 큐온립크림 후기🍧
 
 ​[구매이유]
 
 재재구매임. 할인 행사 진행할 때 미리 쟁여두려고 또 구매함.
 
 ​■제품장점
 
 제약회사인 동화약품의  |
| PCA-00023 | EXTREME_RESULT_CLAIM | oliveyoung | BEAUTY | 요즘 가족들 다 피부이상생기면서 저는 입술이 건조해서 당기고 따가울정도였는데 이거 연속 이틀 바르니까 완전히 나아졌어요. 지금부터 겨울까지 유용하게 잘쓸게요 |
| PCA-00024 | EXTREME_RESULT_CLAIM | oliveyoung | BEAUTY | 털 얇은쪽은 일주일에 한 번 한 달 하니까 좀 듬성듬성 털이 안 나는 게 보여요! 팔이랑 손가락 털이 가장 먼저 변화가 보이네요 저는 하면 한 바로는 털이 싹 사 |
| PCA-00025 | EXTREME_RESULT_CLAIM | oliveyoung | BEAUTY | 기대감 없이 샀다가 매우 만족한 치약이에요
 잇몸 시림 엄청 심했는데 한달 넘게 쓰니까 싹 사라졌습니다 
 가격대가 좀 있는게 아쉽지만 꾸준히 쓰려구요 |
| PCA-00026 | EXTREME_RESULT_CLAIM | oliveyoung | BEAUTY | 🐈주변인들에게 바이오더마, 특히 토너에 대한 이야기를 많이 들어서, 좋은 제품이라는건 알고 있었으나 제대로 접해볼 수 있게된건 이번이 처음이었어요
 
  🐈아무리 |
| PCA-00027 | EXTREME_RESULT_CLAIM | oliveyoung | BEAUTY | 🐈주변인들에게 바이오더마, 특히 토너에 대한 이야기를 많이 들어서, 좋은 제품이라는건 알고 있었으나 제대로 접해볼 수 있게된건 이번이 처음이었어요
 
  🐈아무리 |
| PCA-00028 | EXTREME_RESULT_CLAIM | oliveyoung | BEAUTY | 평소 칙칙한 피부 톤과 점점 짙어지는 기미, 잡티가 고민이라 강력한 토닝 케어가 필요해서 구매했습니다. 비타민 C 화장품은 특유의 끈적임이 있거나 피부에 자극적일 |
| PCA-00029 | EXTREME_RESULT_CLAIM | oliveyoung | BEAUTY | 하 진자 스트라이덱스❤️나 💗💗💗
 제 좁쌀 구원템이에요 진짜ㅜㅜㅜ 전 처음에 써보고 딱히 자극 없어서 데일리로 써봤는데 한 일주일 후 부터 효과보이기 시작하더니 |
| PCA-00030 | EXTREME_RESULT_CLAIM | oliveyoung | BEAUTY | ㄹㅇ 예전에는 무슨 남자가 관리냐 했는데
 이번에 들어서 맞지 남자도 관리 해야지 였었는데
 또 무슨 남자가 화장이냐 이건 진짜 아니다 
 생각했거든요? 근데 주 |

## Interpretation guardrails

- 기존 37/10건은 좁은 coverage 가능성을 뜻할 뿐 실제 recall 수치가 아니다.
- expanded 후보 증가는 성능 개선을 뜻하지 않으며 사람이 precision을 확인해야 한다.
- sensory/일상 변화/시간적 선후관계/개인 경험형 광고 문구가 주요 false-positive 위험이다.
- 어떤 후보도 SUSPICIOUS/NORMAL/UNCERTAIN로 자동 판정하지 않았다.
