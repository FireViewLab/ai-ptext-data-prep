# Large Human Review Candidate Source Manifest

> 사람 검토 후보 탐색 결과입니다. candidate source는 SUSPICIOUS/NORMAL/UNCERTAIN 라벨이 아니며 최종 10K pool을 생성하지 않았습니다.

## Execution

- Full scan: **1,151,943 reviews**, 2 streaming passes
- Duration: **775.68 seconds**
- Raw signatures unchanged: **True**
- Storage: SQLite (`outputs/large_human_review_candidate_manifest_20261028.sqlite3`); random eligibility는 본문을 복제하지 않고 row_uid만 저장

## Candidate sources

| source | reviews | unique products |
| --- | ---: | ---: |
| PRODUCT_DESCRIPTION_REPLACEMENT | 574 | 402 |
| EXTREME_RESULT_CLAIM | 37 | 33 |
| IMMEDIATE_EFFECT_CLAIM | 10 | 10 |
| PROMOTIONAL_TEMPLATE | 497 | 357 |
| LOW_INFORMATION_PRAISE | 278 | 157 |
| REPEATED_SHORT_TEMPLATE | 67,596 | 4,285 |
| EXACT_DUPLICATE_CLUSTER | 178,311 | 6,540 |
| HARD_NEGATIVE_CANDIDATE | 1,992 | 848 |

- RANDOM_CONTROL_ELIGIBLE: **773,638** (eligibility only; not sampled)

## Platform and category distributions

### PRODUCT_DESCRIPTION_REPLACEMENT

- platforms: `{'elevenst': 62, 'kurly': 7, 'musinsa': 15, 'oliveyoung': 490}`
- provisional categories: `{'BABY': 1, 'BEAUTY': 439, 'ELECTRONICS': 9, 'ETC_UNKNOWN': 6, 'FASHION': 4, 'FOOD': 26, 'HEALTH_SUPPLEMENT': 72, 'LIVING': 10, 'PET': 1, 'SPORTS_OUTDOOR': 6}`
- length bands: `{'100-199': 123, '20-49': 5, '200+': 415, '50-99': 31}`

### EXTREME_RESULT_CLAIM

- platforms: `{'elevenst': 2, 'kurly': 3, 'oliveyoung': 32}`
- provisional categories: `{'BEAUTY': 32, 'ETC_UNKNOWN': 1, 'FASHION': 1, 'FOOD': 1, 'HEALTH_SUPPLEMENT': 1, 'PET': 1}`
- length bands: `{'100-199': 5, '200+': 28, '50-99': 3, '<20': 1}`

### IMMEDIATE_EFFECT_CLAIM

- platforms: `{'kurly': 1, 'musinsa': 1, 'oliveyoung': 8}`
- provisional categories: `{'BEAUTY': 10}`
- length bands: `{'100-199': 2, '200+': 8}`

### PROMOTIONAL_TEMPLATE

- platforms: `{'elevenst': 1, 'kurly': 26, 'musinsa': 30, 'oliveyoung': 440}`
- provisional categories: `{'BABY': 1, 'BEAUTY': 424, 'ELECTRONICS': 4, 'ETC_UNKNOWN': 3, 'FASHION': 23, 'FOOD': 29, 'HEALTH_SUPPLEMENT': 6, 'LIVING': 5, 'SPORTS_OUTDOOR': 2}`
- length bands: `{'100-199': 18, '200+': 478, '50-99': 1}`

### LOW_INFORMATION_PRAISE

- platforms: `{'elevenst': 216, 'kurly': 61, 'naver': 1}`
- provisional categories: `{'BABY': 6, 'BEAUTY': 20, 'ELECTRONICS': 40, 'ETC_UNKNOWN': 13, 'FASHION': 12, 'FOOD': 50, 'HEALTH_SUPPLEMENT': 7, 'LIVING': 104, 'PET': 3, 'SPORTS_OUTDOOR': 23}`
- length bands: `{'20-49': 2, '<20': 276}`

### REPEATED_SHORT_TEMPLATE

- platforms: `{'elevenst': 10148, 'kurly': 53966, 'musinsa': 2728, 'naver': 30, 'oliveyoung': 724}`
- provisional categories: `{'BABY': 972, 'BEAUTY': 3290, 'DIET': 371, 'ELECTRONICS': 1174, 'ETC_UNKNOWN': 146, 'FASHION': 2347, 'FOOD': 51784, 'HEALTH_SUPPLEMENT': 1381, 'LIVING': 5015, 'PET': 439, 'SPORTS_OUTDOOR': 677}`
- length bands: `{'20-49': 14334, '<20': 53262}`

### EXACT_DUPLICATE_CLUSTER

- platforms: `{'elevenst': 40709, 'kurly': 61685, 'musinsa': 14560, 'naver': 55, 'ohouse': 226, 'oliveyoung': 61076}`
- provisional categories: `{'BABY': 3355, 'BEAUTY': 57228, 'DIET': 439, 'ELECTRONICS': 3758, 'ETC_UNKNOWN': 497, 'FASHION': 12113, 'FOOD': 66903, 'HEALTH_SUPPLEMENT': 7469, 'LIVING': 22915, 'PET': 1459, 'SPORTS_OUTDOOR': 2175}`
- length bands: `{'100-199': 17487, '20-49': 51739, '200+': 13482, '50-99': 42341, '<20': 53262}`

### HARD_NEGATIVE_CANDIDATE

- platforms: `{'elevenst': 123, 'kurly': 49, 'musinsa': 34, 'ohouse': 1, 'oliveyoung': 1785}`
- provisional categories: `{'BABY': 13, 'BEAUTY': 1736, 'ELECTRONICS': 17, 'ETC_UNKNOWN': 5, 'FASHION': 12, 'FOOD': 54, 'HEALTH_SUPPLEMENT': 121, 'LIVING': 28, 'PET': 2, 'SPORTS_OUTDOOR': 4}`
- length bands: `{'100-199': 140, '200+': 1842, '50-99': 10}`

## Source overlap

- source count/review: `{'1': 112740, '2': 67925, '3+': 235}`
- requested pairs: `{'PRODUCT_DESCRIPTION_REPLACEMENT & PROMOTIONAL_TEMPLATE': 3, 'EXTREME_RESULT_CLAIM & IMMEDIATE_EFFECT_CLAIM': 0, 'LOW_INFORMATION_PRAISE & REPEATED_SHORT_TEMPLATE': 218}`

Top combinations:

- `EXACT_DUPLICATE_CLUSTER`: 110,281
- `EXACT_DUPLICATE_CLUSTER|REPEATED_SHORT_TEMPLATE`: 67,378
- `HARD_NEGATIVE_CANDIDATE`: 1,523
- `PRODUCT_DESCRIPTION_REPLACEMENT`: 430
- `PROMOTIONAL_TEMPLATE`: 402
- `EXACT_DUPLICATE_CLUSTER|HARD_NEGATIVE_CANDIDATE`: 325
- `EXACT_DUPLICATE_CLUSTER|LOW_INFORMATION_PRAISE|REPEATED_SHORT_TEMPLATE`: 218
- `HARD_NEGATIVE_CANDIDATE|PRODUCT_DESCRIPTION_REPLACEMENT`: 102
- `EXACT_DUPLICATE_CLUSTER|PROMOTIONAL_TEMPLATE`: 62
- `LOW_INFORMATION_PRAISE`: 60
- `EXTREME_RESULT_CLAIM`: 34
- `EXACT_DUPLICATE_CLUSTER|PRODUCT_DESCRIPTION_REPLACEMENT`: 31
- `HARD_NEGATIVE_CANDIDATE|PROMOTIONAL_TEMPLATE`: 24
- `IMMEDIATE_EFFECT_CLAIM`: 10
- `EXACT_DUPLICATE_CLUSTER|HARD_NEGATIVE_CANDIDATE|PRODUCT_DESCRIPTION_REPLACEMENT`: 8
- `EXACT_DUPLICATE_CLUSTER|HARD_NEGATIVE_CANDIDATE|PROMOTIONAL_TEMPLATE`: 6
- `PRODUCT_DESCRIPTION_REPLACEMENT|PROMOTIONAL_TEMPLATE`: 2
- `EXACT_DUPLICATE_CLUSTER|EXTREME_RESULT_CLAIM|HARD_NEGATIVE_CANDIDATE`: 2
- `HARD_NEGATIVE_CANDIDATE|PRODUCT_DESCRIPTION_REPLACEMENT|PROMOTIONAL_TEMPLATE`: 1
- `EXTREME_RESULT_CLAIM|HARD_NEGATIVE_CANDIDATE`: 1

## Exact duplicate clusters

- clusters: **64,804**
- members: **178,311**
- frequency bands: `{'10-19': 711, '2-4': 59590, '20+': 234, '5-9': 4269}`
- scopes: `{'CROSS_PLATFORM': 756, 'CROSS_PRODUCT_SAME_PLATFORM': 49193, 'SAME_PRODUCT': 14855}`
- 반복 리뷰는 삭제/통합하지 않았고 duplicate_members에 모두 보존했습니다.

## Bias checks

- DIET candidates: **439**
- HEALTH_SUPPLEMENT candidates: **7,623**
- BEAUTY/oliveyoung 및 FOOD/kurly 집중은 source별 platform/category 표로 확인하며 다음 sampling 단계에서 soft cap을 적용해야 합니다.
- LOW_INFORMATION_PRAISE와 repeated-short는 weak source이며 단독 suspicious 근거로 사용하지 않습니다.

## 10K feasibility (recommendation only)

- Signal-focused 6,000 source quotas before overlap dedup: `{'PRODUCT_DESCRIPTION_REPLACEMENT': 574, 'EXTREME_RESULT_CLAIM': 37, 'IMMEDIATE_EFFECT_CLAIM': 10, 'PROMOTIONAL_TEMPLATE': 497, 'REPEATED_SHORT_TEMPLATE': 2332, 'EXACT_DUPLICATE_CLUSTER': 2272, 'LOW_INFORMATION_PRAISE': 278}`
- Hard Negative: target 2,500 / available 1,992
- Random Control: target 1,500 / eligible 773,638
- Exact 6,000/2,500/1,500 composition feasible without rule expansion: **False** (Hard Negative shortfall 508)
- sqrt platform soft targets: `{'elevenst': 1895, 'kurly': 3121, 'musinsa': 1576, 'naver': 164, 'ohouse': 379, 'oliveyoung': 2865}`
- Category soft policy: each category 50 when available, DIET 150 / HEALTH_SUPPLEMENT 500 preferred, any category max 25%.
- 실제 10K 선택에서는 overlap을 제거하고 product/cluster cap 및 platform×category strata를 적용해야 합니다.

## Scope and next step

- CURRENT_PTEXT_HIGH/BOUNDARY, semantic near-duplicate full scan, model/LLM inference, training은 실행하지 않았습니다.
- Near-duplicate는 length/language/category blocking + normalized character-shingle MinHash/LSH를 작은 audit sample에서 먼저 보정하는 방식을 권장합니다.
- 다음 단계는 이 manifest를 대상으로 quota dry-run 및 사람이 승인한 뒤에만 10K pool을 생성하는 것입니다.
- 자동 human label은 어디에도 생성하지 않았습니다.
