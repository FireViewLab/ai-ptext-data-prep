# Human Review 10K Quota Bottleneck Audit

> 진단용 in-memory simulation입니다. human label과 실제 10K review dataset을 생성하지 않았고 canonical SQLite를 read-only로 열었습니다.

## Executive findings

- v3의 category/platform balancing은 round-robin ordering이며 hard cap이나 quota rejection이 아니다.
- Signal은 expanded EXTREME/IMMEDIATE의 requested quota가 availability를 크게 초과해 cap 적용 전부터 부족하다.
- Balanced HARD_NEGATIVE 12,275는 raw union cardinality이며 signal 선점 및 product/cluster/text cap 이후의 독립 capacity가 아니다.
- duplicate cluster와 normalized text는 canonical exact-duplicate 데이터에서 같은 hash cluster를 표현하므로 cap=1에서는 효과가 중첩된다.
- source priority와 bucket order가 row_uid 선점 상태를 바꾸므로 손실은 독립적으로 합산할 수 없다.
- v3 random-control frame에는 cluster/hash metadata가 전달되지 않아 random bucket에는 duplicate/text cap이 적용되지 않았다.
- v3 보고서의 normalized_text_max_reviews=1 표기와 달리 선택 함수에는 별도 normalized-text cap이 구현되지 않았다.

## v3 reproduction and sequential loss attribution

### precision_first

- buckets: `{'signal_focused': 3795, 'hard_negative': 1658, 'random_control': 1500}` / unique **6,953** / shortfall **3,047**
- source selected: `{'PRODUCT_DESCRIPTION_REPLACEMENT': 514, 'EXTREME_RESULT_CLAIM': 29, 'EXTREME_RESULT_EXPANDED_PROTOTYPE': 74, 'IMMEDIATE_EFFECT_CLAIM': 9, 'IMMEDIATE_EFFECT_EXPANDED_PROTOTYPE': 9, 'PROMOTIONAL_TEMPLATE': 376, 'LOW_INFORMATION_PRAISE': 84, 'REPEATED_SHORT_TEMPLATE': 1350, 'EXACT_DUPLICATE_CLUSTER': 1350, 'HARD_NEGATIVE_UNION': 1658, 'HARD_NEGATIVE_CANDIDATE': 463, 'HARD_NEGATIVE_EXPANDED_CANDIDATE': 1195, 'RANDOM_CONTROL_ELIGIBLE': 1500}`

| source/bucket | requested | available | already used | selected | unfilled | availability | row_uid target loss | product | cluster | text |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| PRODUCT_DESCRIPTION_REPLACEMENT | 574 | 574 | 0 | 514 | 60 | 0 | 0 | 60 | 0 | 0 |
| EXTREME_RESULT_CLAIM | 37 | 37 | 0 | 29 | 8 | 0 | 0 | 7 | 1 | 0 |
| EXTREME_RESULT_EXPANDED_PROTOTYPE | 1100 | 169 | 5 | 74 | 1026 | 931 | 5 | 57 | 33 | 0 |
| IMMEDIATE_EFFECT_CLAIM | 10 | 10 | 0 | 9 | 1 | 0 | 0 | 1 | 0 | 0 |
| IMMEDIATE_EFFECT_EXPANDED_PROTOTYPE | 800 | 35 | 8 | 9 | 791 | 765 | 8 | 4 | 14 | 0 |
| PROMOTIONAL_TEMPLATE | 497 | 497 | 7 | 376 | 121 | 0 | 7 | 101 | 13 | 0 |
| LOW_INFORMATION_PRAISE | 282 | 278 | 0 | 84 | 198 | 4 | 0 | 73 | 121 | 0 |
| REPEATED_SHORT_TEMPLATE | 1350 | 67596 | 24 | 1350 | 0 | 0 | 0 | 0 | 0 | 0 |
| EXACT_DUPLICATE_CLUSTER | 1350 | 178311 | 1488 | 1350 | 0 | 0 | 0 | 0 | 0 | 0 |
| HARD_NEGATIVE_UNION | 2500 | 12275 | 412 | 1658 | 842 | 0 | 0 | 288 | 554 | 0 |
| RANDOM_CONTROL_ELIGIBLE | 1500 | 773638 | None | 1500 | 0 | 0 | 0 | 0 | 0 | 0 |

- platform: `{'elevenst': 1801, 'kurly': 1052, 'musinsa': 852, 'naver': 92, 'ohouse': 127, 'oliveyoung': 3029}`
- category: `{'BABY': 263, 'BEAUTY': 2846, 'DIET': 24, 'ELECTRONICS': 535, 'ETC_UNKNOWN': 127, 'FASHION': 472, 'FOOD': 858, 'HEALTH_SUPPLEMENT': 448, 'LIVING': 768, 'PET': 238, 'SPORTS_OUTDOOR': 374}`
- unique products/clusters: **4,204 / 4,058**

### balanced

- buckets: `{'signal_focused': 3495, 'hard_negative': 1711, 'random_control': 1500}` / unique **6,706** / shortfall **3,294**
- source selected: `{'PRODUCT_DESCRIPTION_REPLACEMENT': 514, 'EXTREME_RESULT_CLAIM': 29, 'EXTREME_RESULT_EXPANDED_PROTOTYPE': 74, 'IMMEDIATE_EFFECT_CLAIM': 9, 'IMMEDIATE_EFFECT_EXPANDED_PROTOTYPE': 9, 'PROMOTIONAL_TEMPLATE': 376, 'LOW_INFORMATION_PRAISE': 84, 'REPEATED_SHORT_TEMPLATE': 1200, 'EXACT_DUPLICATE_CLUSTER': 1200, 'HARD_NEGATIVE_UNION': 1711, 'HARD_NEGATIVE_CANDIDATE': 474, 'HARD_NEGATIVE_EXPANDED_CANDIDATE': 1237, 'RANDOM_CONTROL_ELIGIBLE': 1500}`

| source/bucket | requested | available | already used | selected | unfilled | availability | row_uid target loss | product | cluster | text |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| PRODUCT_DESCRIPTION_REPLACEMENT | 574 | 574 | 0 | 514 | 60 | 0 | 0 | 60 | 0 | 0 |
| EXTREME_RESULT_CLAIM | 37 | 37 | 0 | 29 | 8 | 0 | 0 | 7 | 1 | 0 |
| EXTREME_RESULT_EXPANDED_PROTOTYPE | 1300 | 169 | 5 | 74 | 1226 | 1131 | 5 | 57 | 33 | 0 |
| IMMEDIATE_EFFECT_CLAIM | 10 | 10 | 0 | 9 | 1 | 0 | 0 | 1 | 0 | 0 |
| IMMEDIATE_EFFECT_EXPANDED_PROTOTYPE | 900 | 35 | 8 | 9 | 891 | 865 | 8 | 4 | 14 | 0 |
| PROMOTIONAL_TEMPLATE | 497 | 497 | 7 | 376 | 121 | 0 | 7 | 101 | 13 | 0 |
| LOW_INFORMATION_PRAISE | 282 | 278 | 0 | 84 | 198 | 4 | 0 | 73 | 121 | 0 |
| REPEATED_SHORT_TEMPLATE | 1200 | 67596 | 24 | 1200 | 0 | 0 | 0 | 0 | 0 | 0 |
| EXACT_DUPLICATE_CLUSTER | 1200 | 178311 | 1338 | 1200 | 0 | 0 | 0 | 0 | 0 | 0 |
| HARD_NEGATIVE_UNION | 2500 | 12275 | 401 | 1711 | 789 | 0 | 0 | 196 | 593 | 0 |
| RANDOM_CONTROL_ELIGIBLE | 1500 | 773638 | None | 1500 | 0 | 0 | 0 | 0 | 0 | 0 |

- platform: `{'elevenst': 1694, 'kurly': 1006, 'musinsa': 804, 'naver': 91, 'ohouse': 117, 'oliveyoung': 2994}`
- category: `{'BABY': 263, 'BEAUTY': 2791, 'DIET': 24, 'ELECTRONICS': 509, 'ETC_UNKNOWN': 127, 'FASHION': 449, 'FOOD': 808, 'HEALTH_SUPPLEMENT': 425, 'LIVING': 723, 'PET': 238, 'SPORTS_OUTDOOR': 349}`
- unique products/clusters: **4,081 / 3,800**

### diversity_first

- buckets: `{'signal_focused': 2930, 'hard_negative': 797, 'random_control': 1500}` / unique **5,227** / shortfall **4,773**
- source selected: `{'PRODUCT_DESCRIPTION_REPLACEMENT': 402, 'EXTREME_RESULT_CLAIM': 22, 'EXTREME_RESULT_EXPANDED_PROTOTYPE': 53, 'IMMEDIATE_EFFECT_CLAIM': 6, 'IMMEDIATE_EFFECT_EXPANDED_PROTOTYPE': 8, 'PROMOTIONAL_TEMPLATE': 262, 'LOW_INFORMATION_PRAISE': 77, 'REPEATED_SHORT_TEMPLATE': 1050, 'EXACT_DUPLICATE_CLUSTER': 1050, 'HARD_NEGATIVE_UNION': 797, 'HARD_NEGATIVE_CANDIDATE': 203, 'HARD_NEGATIVE_EXPANDED_CANDIDATE': 594, 'RANDOM_CONTROL_ELIGIBLE': 1500}`

| source/bucket | requested | available | already used | selected | unfilled | availability | row_uid target loss | product | cluster | text |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| PRODUCT_DESCRIPTION_REPLACEMENT | 574 | 574 | 0 | 402 | 172 | 0 | 0 | 172 | 0 | 0 |
| EXTREME_RESULT_CLAIM | 37 | 37 | 0 | 22 | 15 | 0 | 0 | 15 | 0 | 0 |
| EXTREME_RESULT_EXPANDED_PROTOTYPE | 1500 | 169 | 4 | 53 | 1447 | 1331 | 4 | 94 | 18 | 0 |
| IMMEDIATE_EFFECT_CLAIM | 10 | 10 | 0 | 6 | 4 | 0 | 0 | 4 | 0 | 0 |
| IMMEDIATE_EFFECT_EXPANDED_PROTOTYPE | 1000 | 35 | 7 | 8 | 992 | 965 | 7 | 9 | 11 | 0 |
| PROMOTIONAL_TEMPLATE | 497 | 497 | 7 | 262 | 235 | 0 | 7 | 221 | 7 | 0 |
| LOW_INFORMATION_PRAISE | 282 | 278 | 0 | 77 | 205 | 4 | 0 | 127 | 74 | 0 |
| REPEATED_SHORT_TEMPLATE | 1050 | 67596 | 24 | 1050 | 0 | 0 | 0 | 0 | 0 | 0 |
| EXACT_DUPLICATE_CLUSTER | 1050 | 178311 | 1164 | 1050 | 0 | 0 | 0 | 0 | 0 | 0 |
| HARD_NEGATIVE_UNION | 2500 | 12275 | 290 | 797 | 1703 | 0 | 0 | 1584 | 119 | 0 |
| RANDOM_CONTROL_ELIGIBLE | 1500 | 773638 | None | 1500 | 0 | 0 | 0 | 0 | 0 | 0 |

- platform: `{'elevenst': 1466, 'kurly': 817, 'musinsa': 799, 'naver': 56, 'ohouse': 100, 'oliveyoung': 1989}`
- category: `{'BABY': 136, 'BEAUTY': 1832, 'DIET': 12, 'ELECTRONICS': 511, 'ETC_UNKNOWN': 67, 'FASHION': 442, 'FOOD': 782, 'HEALTH_SUPPLEMENT': 266, 'LIVING': 668, 'PET': 124, 'SPORTS_OUTDOOR': 387}`
- unique products/clusters: **5,227 / 2,814**

## Balanced hard-negative bottleneck

- raw union availability: **12,275**
- v3 selected: **1,711 / 2,500**
- independent capacity from empty state: `{'1': {'selected_from_empty_state': 1938, 'target_shortfall': 562, 'unique_products': 1938}, '2': {'selected_from_empty_state': 2500, 'target_shortfall': 0, 'unique_products': 1660}, '3': {'selected_from_empty_state': 2500, 'target_shortfall': 0, 'unique_products': 1453}, '5': {'selected_from_empty_state': 2500, 'target_shortfall': 0, 'unique_products': 1316}, 'unlimited': {'selected_from_empty_state': 2500, 'target_shortfall': 0}}`
- 따라서 12,275는 단순 union cardinality이며 현재 signal 선점과 product/cluster/text cap을 통과하는 독립 선택 가능 수량이 아니다.

## Sensitivity

| policy | unique | signal | hard | random | shortfall | products | clusters | max text |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| availability_adjusted_quotas | 6706 | 3495 | 1711 | 1500 | 3294 | 4081 | 3800 | 1 |
| bucket_order_hard-signal-random | 6909 | 2909 | 2500 | 1500 | 3091 | 4202 | 4246 | 1 |
| bucket_order_random-hard-signal | 6853 | 2853 | 2500 | 1500 | 3147 | 4190 | 4219 | 1 |
| product_cap_1 | 5452 | 3230 | 722 | 1500 | 4548 | 5452 | 3050 | 1 |
| product_cap_2 | 6706 | 3495 | 1711 | 1500 | 3294 | 4081 | 3800 | 1 |
| product_cap_3 | 7571 | 3599 | 2472 | 1500 | 2429 | 3702 | 4318 | 1 |
| product_cap_5 | 7659 | 3659 | 2500 | 1500 | 2341 | 3281 | 4533 | 1 |
| cluster_1_text_1 | 6706 | 3495 | 1711 | 1500 | 3294 | 4081 | 3800 | 1 |
| cluster_1_text_2 | 6706 | 3495 | 1711 | 1500 | 3294 | 4081 | 3800 | 1 |
| cluster_2_text_1 | 6706 | 3495 | 1711 | 1500 | 3294 | 4081 | 3800 | 1 |
| cluster_2_text_2 | 7138 | 3560 | 2078 | 1500 | 2862 | 4214 | 3399 | 2 |
| cluster_5_text_5 | 7311 | 3593 | 2218 | 1500 | 2689 | 4292 | 3308 | 5 |
| cluster_none_text_none | 7439 | 3669 | 2270 | 1500 | 2561 | 4356 | 3286 | 68 |
| flat_order_no_category_platform_round_robin | 6466 | 3495 | 1471 | 1500 | 3534 | 4297 | 3546 | 1 |
| random_with_duplicate_metadata | 6706 | 3495 | 1711 | 1500 | 3294 | 4081 | 3800 | 1 |
| signal_source_priority_reversed | 6658 | 3370 | 1788 | 1500 | 3342 | 4079 | 3836 | 1 |
| signal_source_priority_duplicate_first | 6624 | 3375 | 1749 | 1500 | 3376 | 4045 | 3799 | 1 |
| signal_union_fill_product_2 | 9020 | 6000 | 1520 | 1500 | 980 | 5344 | 6692 | 1 |
| signal_union_fill_product_3 | 9930 | 6000 | 2430 | 1500 | 70 | 4621 | 7292 | 1 |
| signal_union_fill_product_5 | 10000 | 6000 | 2500 | 1500 | 0 | 3791 | 7660 | 1 |

## Candidate-only ceiling and limits

- tested maximum: **10,000** (`signal_union_fill_product_5`)
- buckets: `{'signal_focused': 6000, 'hard_negative': 2500, 'random_control': 1500}`
- unique products: **3,791**; rows in duplicate clusters / unique clusters: **7,660 / 7,660**
- union-fill은 source quota를 제거하므로 기술적 capacity 진단일 뿐 권장 sampling 정책이 아니다. duplicate/network 계열과 검증 전 prototype이 지배할 위험이 있다.

## Full-corpus availability

- review_index: **1,151,943** / candidate_content: **180,900** / missing content: **971,043**
- raw CSVs present: **False**
- review_index는 전체 identity/category/hash/length/source_row를 보존하지만 content는 candidate_content에만 있다.
- 따라서 candidate 외부에 새 text rule을 적용하려면 원본 6개 CSV가 필요하며, 현재는 재스캔하지 않았다.

## Recommended next actions

1. expanded-only precision audit 완료 전 prototype quota 확대 금지
2. Balanced에서 product cap 3 민감도와 hard-negative category/product coverage를 사람이 검토
3. duplicate source quota뿐 아니라 전체 selected rows의 cluster/text 비율을 제약
4. 6개 raw CSV를 read-only로 다시 제공한 뒤 별도 full-corpus prototype을 실행
5. 승인 전까지 실제 10K pool과 human label을 생성하지 않음
