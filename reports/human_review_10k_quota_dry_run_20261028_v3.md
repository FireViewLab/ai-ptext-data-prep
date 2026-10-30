# Human Review 10K Quota Dry-run

> 실제 10K review CSV나 human label을 생성하지 않은 allocation simulation입니다.

## Shared policy

- Signal 6,000 / Hard Negative 2,500 / Random Control 1,500
- multi-source row는 scenario의 source 우선순위 하나에만 배정하고 최종 선택 단계에서 row_uid dedup
- duplicate/network 계열 soft cap 35~45%, cluster/normalized text/product cap 적용
- prototype source는 사람 precision 확인 전 정답 source로 간주하지 않음

## precision_first

- buckets: `{'signal_focused': 6000, 'hard_negative': 2500, 'random_control': 1500}`
- signal source requested: `{'PRODUCT_DESCRIPTION_REPLACEMENT': 574, 'EXTREME_RESULT_CLAIM': 37, 'EXTREME_RESULT_EXPANDED_PROTOTYPE': 1100, 'IMMEDIATE_EFFECT_CLAIM': 10, 'IMMEDIATE_EFFECT_EXPANDED_PROTOTYPE': 800, 'PROMOTIONAL_TEMPLATE': 497, 'LOW_INFORMATION_PRAISE': 282, 'REPEATED_SHORT_TEMPLATE': 1350, 'EXACT_DUPLICATE_CLUSTER': 1350}`
- feasible before row_uid dedup: `{'PRODUCT_DESCRIPTION_REPLACEMENT': 574, 'EXTREME_RESULT_CLAIM': 37, 'EXTREME_RESULT_EXPANDED_PROTOTYPE': 169, 'IMMEDIATE_EFFECT_CLAIM': 10, 'IMMEDIATE_EFFECT_EXPANDED_PROTOTYPE': 35, 'PROMOTIONAL_TEMPLATE': 497, 'LOW_INFORMATION_PRAISE': 278, 'REPEATED_SHORT_TEMPLATE': 1350, 'EXACT_DUPLICATE_CLUSTER': 1350}`
- availability shortfall before dedup: **1,700**
- source assignment after row_uid dedup/caps: `{'PRODUCT_DESCRIPTION_REPLACEMENT': 514, 'EXTREME_RESULT_CLAIM': 29, 'EXTREME_RESULT_EXPANDED_PROTOTYPE': 74, 'IMMEDIATE_EFFECT_CLAIM': 9, 'IMMEDIATE_EFFECT_EXPANDED_PROTOTYPE': 9, 'PROMOTIONAL_TEMPLATE': 376, 'LOW_INFORMATION_PRAISE': 84, 'REPEATED_SHORT_TEMPLATE': 1350, 'EXACT_DUPLICATE_CLUSTER': 1350}`
- unique bucket rows: `{'signal_focused': 3795, 'hard_negative': 1658, 'random_control': 1500}`
- final unique row_uid / total shortfall: **6,953 / 3,047**
- hard-negative available / target feasible: **12,275 / True**
- duplicate family requested share: **45.0%**
- actual duplicate cluster rows / unique clusters: **4,058 / 4,058**
- caps: `{'duplicate_cluster_max_reviews': 1, 'normalized_text_max_reviews': 1, 'product_max_reviews': 2}`; observed max cluster/product: `1/2`
- actual category allocation: `{'BABY': 263, 'BEAUTY': 2846, 'DIET': 24, 'ELECTRONICS': 535, 'ETC_UNKNOWN': 127, 'FASHION': 472, 'FOOD': 858, 'HEALTH_SUPPLEMENT': 448, 'LIVING': 768, 'PET': 238, 'SPORTS_OUTDOOR': 374}`
- actual platform allocation: `{'elevenst': 1801, 'kurly': 1052, 'musinsa': 852, 'naver': 92, 'ohouse': 127, 'oliveyoung': 3029}`

## balanced

- buckets: `{'signal_focused': 6000, 'hard_negative': 2500, 'random_control': 1500}`
- signal source requested: `{'PRODUCT_DESCRIPTION_REPLACEMENT': 574, 'EXTREME_RESULT_CLAIM': 37, 'EXTREME_RESULT_EXPANDED_PROTOTYPE': 1300, 'IMMEDIATE_EFFECT_CLAIM': 10, 'IMMEDIATE_EFFECT_EXPANDED_PROTOTYPE': 900, 'PROMOTIONAL_TEMPLATE': 497, 'LOW_INFORMATION_PRAISE': 282, 'REPEATED_SHORT_TEMPLATE': 1200, 'EXACT_DUPLICATE_CLUSTER': 1200}`
- feasible before row_uid dedup: `{'PRODUCT_DESCRIPTION_REPLACEMENT': 574, 'EXTREME_RESULT_CLAIM': 37, 'EXTREME_RESULT_EXPANDED_PROTOTYPE': 169, 'IMMEDIATE_EFFECT_CLAIM': 10, 'IMMEDIATE_EFFECT_EXPANDED_PROTOTYPE': 35, 'PROMOTIONAL_TEMPLATE': 497, 'LOW_INFORMATION_PRAISE': 278, 'REPEATED_SHORT_TEMPLATE': 1200, 'EXACT_DUPLICATE_CLUSTER': 1200}`
- availability shortfall before dedup: **2,000**
- source assignment after row_uid dedup/caps: `{'PRODUCT_DESCRIPTION_REPLACEMENT': 514, 'EXTREME_RESULT_CLAIM': 29, 'EXTREME_RESULT_EXPANDED_PROTOTYPE': 74, 'IMMEDIATE_EFFECT_CLAIM': 9, 'IMMEDIATE_EFFECT_EXPANDED_PROTOTYPE': 9, 'PROMOTIONAL_TEMPLATE': 376, 'LOW_INFORMATION_PRAISE': 84, 'REPEATED_SHORT_TEMPLATE': 1200, 'EXACT_DUPLICATE_CLUSTER': 1200}`
- unique bucket rows: `{'signal_focused': 3495, 'hard_negative': 1711, 'random_control': 1500}`
- final unique row_uid / total shortfall: **6,706 / 3,294**
- hard-negative available / target feasible: **12,275 / True**
- duplicate family requested share: **40.0%**
- actual duplicate cluster rows / unique clusters: **3,800 / 3,800**
- caps: `{'duplicate_cluster_max_reviews': 1, 'normalized_text_max_reviews': 1, 'product_max_reviews': 2}`; observed max cluster/product: `1/2`
- actual category allocation: `{'BABY': 263, 'BEAUTY': 2791, 'DIET': 24, 'ELECTRONICS': 509, 'ETC_UNKNOWN': 127, 'FASHION': 449, 'FOOD': 808, 'HEALTH_SUPPLEMENT': 425, 'LIVING': 723, 'PET': 238, 'SPORTS_OUTDOOR': 349}`
- actual platform allocation: `{'elevenst': 1694, 'kurly': 1006, 'musinsa': 804, 'naver': 91, 'ohouse': 117, 'oliveyoung': 2994}`

## diversity_first

- buckets: `{'signal_focused': 6000, 'hard_negative': 2500, 'random_control': 1500}`
- signal source requested: `{'PRODUCT_DESCRIPTION_REPLACEMENT': 574, 'EXTREME_RESULT_CLAIM': 37, 'EXTREME_RESULT_EXPANDED_PROTOTYPE': 1500, 'IMMEDIATE_EFFECT_CLAIM': 10, 'IMMEDIATE_EFFECT_EXPANDED_PROTOTYPE': 1000, 'PROMOTIONAL_TEMPLATE': 497, 'LOW_INFORMATION_PRAISE': 282, 'REPEATED_SHORT_TEMPLATE': 1050, 'EXACT_DUPLICATE_CLUSTER': 1050}`
- feasible before row_uid dedup: `{'PRODUCT_DESCRIPTION_REPLACEMENT': 574, 'EXTREME_RESULT_CLAIM': 37, 'EXTREME_RESULT_EXPANDED_PROTOTYPE': 169, 'IMMEDIATE_EFFECT_CLAIM': 10, 'IMMEDIATE_EFFECT_EXPANDED_PROTOTYPE': 35, 'PROMOTIONAL_TEMPLATE': 497, 'LOW_INFORMATION_PRAISE': 278, 'REPEATED_SHORT_TEMPLATE': 1050, 'EXACT_DUPLICATE_CLUSTER': 1050}`
- availability shortfall before dedup: **2,300**
- source assignment after row_uid dedup/caps: `{'PRODUCT_DESCRIPTION_REPLACEMENT': 402, 'EXTREME_RESULT_CLAIM': 22, 'EXTREME_RESULT_EXPANDED_PROTOTYPE': 53, 'IMMEDIATE_EFFECT_CLAIM': 6, 'IMMEDIATE_EFFECT_EXPANDED_PROTOTYPE': 8, 'PROMOTIONAL_TEMPLATE': 262, 'LOW_INFORMATION_PRAISE': 77, 'REPEATED_SHORT_TEMPLATE': 1050, 'EXACT_DUPLICATE_CLUSTER': 1050}`
- unique bucket rows: `{'signal_focused': 2930, 'hard_negative': 797, 'random_control': 1500}`
- final unique row_uid / total shortfall: **5,227 / 4,773**
- hard-negative available / target feasible: **12,275 / True**
- duplicate family requested share: **35.0%**
- actual duplicate cluster rows / unique clusters: **2,814 / 2,814**
- caps: `{'duplicate_cluster_max_reviews': 1, 'normalized_text_max_reviews': 1, 'product_max_reviews': 1}`; observed max cluster/product: `1/1`
- actual category allocation: `{'BABY': 136, 'BEAUTY': 1832, 'DIET': 12, 'ELECTRONICS': 511, 'ETC_UNKNOWN': 67, 'FASHION': 442, 'FOOD': 782, 'HEALTH_SUPPLEMENT': 266, 'LIVING': 668, 'PET': 124, 'SPORTS_OUTDOOR': 387}`
- actual platform allocation: `{'elevenst': 1466, 'kurly': 817, 'musinsa': 799, 'naver': 56, 'ohouse': 100, 'oliveyoung': 1989}`

## Recommendation

**Balanced**를 권장한다. signal coverage를 늘리면서 duplicate 계열을 40% 이하로 제한하고, oliveyoung/BEAUTY와 kurly/FOOD 집중을 완화하며 DIET·HEALTH_SUPPLEMENT·FASHION·LIVING·ELECTRONICS representation을 확보한다.

## Human review gates

1. expanded-only audit precision 확인
2. source별 precision과 reviewer agreement 확인
3. category/platform/product/cluster caps 확정
4. 그 뒤에만 별도 승인으로 실제 10K pool materialization
