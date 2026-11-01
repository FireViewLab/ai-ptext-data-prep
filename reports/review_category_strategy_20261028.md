# 1.15M Review Category Distribution and Human Review Pool Strategy

> READ-ONLY analysis. 이 보고서는 최종 Human Review Pool을 생성하지 않고, 자동 human label·모델 추론·학습을 수행하지 않는다.

## 1. 실제 전체 review 수와 분석 범위

- 전체: **1,151,943건** / 6개 플랫폼
- 식별자는 문자열로 읽어 leading zero와 원래 표현을 보존했다.
- 외부 raw CSV는 열기/스트리밍만 수행했으며 크기·mtime signature가 전후 동일하다.

| platform | reviews | share |
| --- | --- | --- |
| elevenst | 171,052 | 14.85% |
| kurly | 463,843 | 40.27% |
| musinsa | 118,192 | 10.26% |
| naver | 1,286 | 0.11% |
| ohouse | 6,828 | 0.59% |
| oliveyoung | 390,742 | 33.92% |

## 2. product_category coverage

- blank/null: **1,755건 (0.15%)**
- nonblank raw category unique(global text): **954개**
- raw category는 삭제·치환하지 않고 모든 provisional normalized mapping과 함께 보존해야 한다.

| platform | raw category 종류 |
| --- | --- |
| elevenst | 423 |
| kurly | 270 |
| musinsa | 170 |
| naver | 14 |
| ohouse | 18 |
| oliveyoung | 59 |

## 3. raw category 분포와 fragmentation

### 상위 30 platform/raw category

| platform | raw category | reviews | products | provisional |
| --- | --- | --- | --- | --- |
| oliveyoung | 베이스 메이크업 | 45,826 | 229 | BEAUTY |
| oliveyoung | 스킨케어 | 37,881 | 174 | BEAUTY |
| oliveyoung | 립 메이크업 | 35,857 | 168 | BEAUTY |
| oliveyoung | 헤어 트리트먼트 | 28,207 | 147 | BEAUTY |
| oliveyoung | 아이 메이크업 | 24,244 | 124 | BEAUTY |
| oliveyoung | 클렌징 | 23,101 | 112 | BEAUTY |
| kurly | 반찬 > 두부/어묵/맛살 > 두부 | 17,049 | 61 | FOOD |
| kurly | 유제품 > 우유 > 흰우유 | 15,717 | 57 | FOOD |
| oliveyoung | 헤어 세정류 | 13,773 | 71 | BEAUTY |
| oliveyoung | 바디 세정류 | 13,310 | 67 | BEAUTY |
| kurly | 간식 > 과자 > 스낵 | 13,072 | 65 | FOOD |
| oliveyoung | 치약 | 12,675 | 62 | BEAUTY |
| oliveyoung | 핸드케어 | 12,591 | 70 | BEAUTY |
| oliveyoung | 제모용품 | 11,548 | 64 | BEAUTY |
| kurly | 반찬 > 김치 > 배추 김치류 | 11,148 | 55 | FOOD |
| oliveyoung | 퍼퓸 | 11,126 | 61 | BEAUTY |
| kurly | 냉장/냉동 식품 > 국/탕/찌개 > 국 | 10,816 | 48 | FOOD |
| kurly | 유제품 > 요거트/생크림 > 떠먹는 요거트 | 10,249 | 43 | FOOD |
| kurly | 쌀/잡곡 > 쌀 > 백미 | 10,047 | 47 | FOOD |
| oliveyoung | 마스크팩 | 9,705 | 45 | BEAUTY |
| musinsa | Accessory > 벨트 | 9,544 | 61 | FASHION |
| kurly | 면/즉석식품/통조림 > 라면 > 봉지라면 | 9,306 | 40 | FOOD |
| oliveyoung | 바디 보습류 | 9,250 | 44 | BEAUTY |
| oliveyoung | 선케어 | 8,848 | 41 | BEAUTY |
| kurly | 수산 > 생선 > 연어/참치 | 8,751 | 40 | FOOD |
| kurly | 베이커리/디저트 > 베이커리 빵 > 식빵/모닝빵 | 8,503 | 40 | FOOD |
| kurly | 달걀 > 일반달걀 > 4) 일반 케이지 | 8,471 | 28 | FOOD |
| musinsa | Socks/Legwear > 양말 > 중목/장목 양말 | 7,740 | 52 | FASHION |
| kurly | 양념/오일 > 양념/장류 > 간장 | 7,359 | 40 | FOOD |
| kurly | 유제품 > 치즈 > 슬라이스/슈레드/스트링 | 7,348 | 30 | FOOD |

### 하위 20 platform/raw category

| platform | raw category | reviews | products | provisional |
| --- | --- | --- | --- | --- |
| elevenst | 계절가전>가습기>보틀형가습기 | 1 | 1 | ELECTRONICS |
| elevenst | 구기/라켓/스포츠>기타 스포츠용품>용품 기타 | 1 | 1 | SPORTS_OUTDOOR |
| elevenst | 모니터>일반 모니터>84cm이상(34인치~) | 1 | 1 | ELECTRONICS |
| elevenst | 생활가전>비데>휴대용비데 | 1 | 1 | ELECTRONICS |
| elevenst | 세제/방향/살충>청소세제/세정제>다목적청소세제 | 1 | 1 | LIVING |
| elevenst | 스포츠 잡화>스포츠 용품>타월 | 1 | 1 | SPORTS_OUTDOOR |
| elevenst | 여성의류>청바지>와이드 | 1 | 1 | FASHION |
| elevenst | 욕실용품>수건/타월>수건/타월>바스타월 | 1 | 1 | LIVING |
| elevenst | 욕실용품>욕실소품/잡화>욕실소품 기타 | 1 | 1 | LIVING |
| elevenst | 주방가전>가스레인지>3구 | 1 | 1 | ELECTRONICS |
| elevenst | 주방가전>원액기/주서기>착즙기 | 1 | 1 | ELECTRONICS |
| elevenst | 주방가전>전기포트>보온포트 | 1 | 1 | ELECTRONICS |
| elevenst | 주방용품>프라이팬>에그팬/간식팬>붕어빵팬/기타간식팬 | 1 | 1 | LIVING |
| elevenst | 청소용품>기타 청소도구>청소도구 기타 | 1 | 1 | ETC_UNKNOWN |
| elevenst | 취미>보드게임/테이블게임>마작 | 1 | 1 | ETC_UNKNOWN |
| elevenst | 커피/생수/음료>생수>기타 생수 | 1 | 1 | FOOD |
| elevenst | 해외직구>노트북/PC>노트북/PC 기타 | 1 | 1 | ETC_UNKNOWN |
| elevenst | 휴대폰>공기계/중고폰>중고폰 | 1 | 1 | ELECTRONICS |
| kurly | 가전제품 > 주방가전 > 기타/주방보조기기 | 1 | 1 | ELECTRONICS |
| kurly | 주방용품 > 주방잡화 > 기타 주방잡화 | 1 | 1 | LIVING |

### 희소 category

| 최대 reviews/category | platform-category pairs | participating reviews |
| --- | --- | --- |
| 1 | 31 | 31 |
| 10 | 128 | 508 |
| 100 | 298 | 7,650 |

- NFKC/공백/구분자만 다른 canonical variant group: 0개
- 동일 leaf명이 여러 hierarchy path에 존재하는 group: 54개
- 따라서 raw 954개를 그대로 sampling stratum으로 쓰면 지나치게 세분화된다. 다만 leaf명이 같다는 이유만으로 자동 병합해서도 안 된다.

## 4. platform × provisional normalized category

| platform | BEAUTY | HEALTH_SUPPLEMENT | DIET | FOOD | FASHION | LIVING | ELECTRONICS | BABY | PET | SPORTS_OUTDOOR | ETC_UNKNOWN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| elevenst | 21,035 | 16,288 | 219 | 23,540 | 6,173 | 52,086 | 26,555 | 8,561 | 5,748 | 8,011 | 2,836 |
| kurly | 20,063 | 2,847 | 2,241 | 423,343 | 450 | 7,657 | 1,853 | 2,607 | 2,697 | 85 | 0 |
| musinsa | 10,980 | 466 | 0 | 0 | 91,323 | 401 | 2,613 | 114 | 136 | 10,264 | 1,895 |
| naver | 0 | 0 | 0 | 0 | 0 | 1,145 | 41 | 100 | 0 | 0 | 0 |
| ohouse | 0 | 0 | 0 | 0 | 0 | 6,828 | 0 | 0 | 0 | 0 | 0 |
| oliveyoung | 337,905 | 15,045 | 0 | 17,853 | 542 | 10,948 | 3,247 | 2,793 | 1,331 | 0 | 1,078 |

관찰된 집중은 실제 데이터와 일치한다: oliveyoung은 BEAUTY 중심, musinsa는 FASHION/SPORTS 중심, kurly는 FOOD 중심, ohouse는 LIVING 중심이다. 단순 비례 sampling은 이 플랫폼-카테고리 결합을 그대로 증폭한다.

## 5. 추천 normalized category 체계

`BEAUTY`, `HEALTH_SUPPLEMENT`, `DIET`, `FOOD`, `FASHION`, `LIVING`, `ELECTRONICS`, `BABY`, `PET`, `SPORTS_OUTDOOR`, `ETC_UNKNOWN`

| normalized category | reviews | share | unique products |
| --- | --- | --- | --- |
| BEAUTY | 389,983 | 33.85% | 2,075 |
| HEALTH_SUPPLEMENT | 34,646 | 3.01% | 268 |
| DIET | 2,460 | 0.21% | 12 |
| FOOD | 464,736 | 40.34% | 2,317 |
| FASHION | 98,488 | 8.55% | 1,475 |
| LIVING | 79,065 | 6.86% | 866 |
| ELECTRONICS | 34,309 | 2.98% | 782 |
| BABY | 14,175 | 1.23% | 138 |
| PET | 9,912 | 0.86% | 127 |
| SPORTS_OUTDOOR | 18,360 | 1.59% | 393 |
| ETC_UNKNOWN | 5,809 | 0.50% | 75 |

이 체계는 sampling용 상위 계층이다. `ETC_UNKNOWN`을 허용하고, raw category 및 mapping reason을 함께 저장해야 한다. 특히 musinsa `Food/Health`와 광범위한 root는 근거 없이 세분화하지 않는다.

## 6. raw → normalized mapping 전략

1. blank는 `ETC_UNKNOWN`으로 보존한다.
2. baby/pet/diet/supplement처럼 명시적인 전체 path 용어를 우선한다.
3. 플랫폼별 root taxonomy를 적용한다.
4. 매핑 근거가 없는 값은 `ETC_UNKNOWN`으로 남긴다.
5. mapping table은 `(platform, raw_category, normalized_category, mapping_reason, mapping_version)` 형태로 versioning한다.
6. JSON의 `raw_rows`가 전체 platform/raw mapping manifest 역할을 한다.

## 7. candidate source별 실제 탐색 가능성

| candidate source | 현재 가능성 | 근거/필요 작업 |
| --- | --- | --- |
| PRODUCT_DESCRIPTION_REPLACEMENT | 즉시 재사용 가능 | 기존 full-scan 574 → V2 387; HIGH 26 중 사람 SUSPICIOUS 24 (HIGH stratum 92.3%, 전체 precision 추정치는 아님) |
| EXTREME_RESULT_CLAIM | 새 analyzer 필요 | 기간+큰 수치/완전 변화 조합과 부정·인용 예외를 함께 설계 |
| IMMEDIATE_EFFECT_CLAIM | 새 analyzer 필요 | 즉시/하루/먹자마자 등 시간 표현+효과 동사 조합; 단독 keyword 금지 |
| PROMOTIONAL_TEMPLATE | 새 analyzer 필요 | 구조화된 장점/추천/총평과 cross-review phrase repetition을 결합 |
| LOW_INFORMATION_PRAISE | 탐색 쉬움, 단독 신호는 약함 | 20자 미만 250,756건. 길이만으로 label 금지; 제품/플랫폼 cap 필수 |
| REPEATED_SHORT_TEMPLATE | inventory 재사용 가능 | normalized-content duplicate extra rows 112,734건. 짧음+반복 결합 |
| NEAR_DUPLICATE_CLUSTER | 소규모 코드는 있으나 1.15M용 신규 구현 필요 | 기존 TF-IDF pair 도구는 전체 1.15M 직접 적용에 부적합; blocking/MinHash형 단계 필요 |
| CURRENT_PTEXT_HIGH | 현재 단계 실행 금지 | scored manifest가 별도로 제공될 때만 candidate source로 ingest |
| CURRENT_PTEXT_BOUNDARY | 현재 단계 실행 금지 | 실제 score distribution 확인 후 band 결정; 0.4~0.6 하드코딩 금지 |
| HARD_NEGATIVE_CANDIDATE | 후보 source 산출 후 가능 | signal은 강하지만 개인 경험이 구체적인 리뷰를 별도 검토층으로 구성 |
| RANDOM_NORMAL_CONTROL | 즉시 가능 | signal 비적중 모집단에서 category/platform/product 제한 stratified random |

## 8. 기존 repo에서 재사용 가능한 코드/module

- `analyze_new_review_inventory.py`: streaming CSV, identifier policy, exact/normalized duplicate inventory
- `analyze_ptext_description_candidates.py`: description signal 분석
- `extract_new_description_candidates.py`: 1.15M streaming candidate manifest/identity dedup
- `build_description_human_review_pool_v2.py`: V2 precision refinement와 normalized-content dedup
- `detect_near_duplicates.py`: 소규모 TF-IDF near-duplicate 기준 참고용(1.15M 직접 재사용 금지)
- `prepare_description_human_review_annotations.py`: annotation identity/integrity validator
- model score/inference manifest를 만드는 runtime은 이 repo에 확인되지 않았다.

## 9. 새로 필요한 analyzer/script

1. `analyze_review_category_strategy.py` — 현재 보고서와 전체 mapping manifest 생성(구현됨)
2. `extract_claim_candidates.py` — EXTREME/IMMEDIATE claim evidence만 기록, label 금지
3. `extract_template_candidates.py` — promotional/low-information/repeated-short source
4. `build_text_duplicate_clusters.py` — exact/near cluster와 대표 review 분리
5. `merge_candidate_manifests.py` — multi-source provenance와 identity dedup
6. `sample_human_review_pool.py` — quota/cap 기반 deterministic sampling; 최종 pool 생성은 승인 후 별도 단계
7. `validate_human_review_pool.py` — source identity/content, strata, overlap, label blank 검증

## 10. candidate source overlap 예상과 보존 구조

- description ↔ promotional ↔ extreme/immediate는 높은 overlap이 예상된다.
- low-information ↔ repeated-short ↔ near-duplicate도 높은 overlap이 예상된다.
- 한 review를 source별로 복제하지 말고 `candidate_sources`를 multi-value provenance로 저장한다.
- review table에는 identity/content/source evidence를, cluster table에는 `cluster_id`, member identity, representative 여부를 둔다.
- exact identity duplicate는 한 review로 통합하되 membership metadata는 삭제하지 않는다.
- normalized-content duplicate는 대표 1건을 기본 검토 대상으로 하고, cluster audit quota에서 추가 member를 선택한다.

## 11. 10K / 20K / 30K 구성안

| pool | signal-focused | hard negative | random normal | 용도 |
| --- | --- | --- | --- | --- |
| 10K | 6,000 | 2,500 | 1,500 | 첫 calibration gate |
| 20K | 11,000 | 5,500 | 3,500 | 10K 결과가 안정적일 때 누적 확장 |
| 30K | 15,000 | 9,000 | 6,000 | source yield/합의도 검증 후에만 |

공통: source 하나가 전체의 25%를 넘지 않게 soft cap을 두고, multi-source와 아직 적게 본 category/platform을 우선한다. 현재 description V2는 387건뿐이므로 임의 oversampling하지 않는다.

## 12. 가장 추천하는 규모

**10K gated pilot**을 먼저 권장한다. 현재 사람 precision 근거는 description HIGH 26건뿐이고 나머지 source는 아직 analyzer/yield calibration이 없다. 10K에서 source별 positive yield, reviewer agreement, category/platform coverage를 확인한 뒤 **20K cumulative**로 확장하는 것이 정보 효율적이다. 30K를 바로 만들면 약한 signal과 중복 cluster가 annotation 예산을 소모할 위험이 크다.

### sqrt(platform size) 기준 10K soft target

| platform | target |
| --- | --- |
| elevenst | 1,895 |
| kurly | 3,121 |
| musinsa | 1,576 |
| naver | 164 |
| ohouse | 379 |
| oliveyoung | 2,865 |

## 13. category/platform 편향 방지

- platform과 normalized category의 joint stratum을 사용하되 raw category를 보조 metadata로 유지한다.
- 기본 quota는 모집단 비례가 아니라 sqrt(size)로 완화한다.
- platform max 30%, normalized category max 25%, candidate source max 25% soft cap을 둔다.
- product는 기본 최대 2개 review, 동일 duplicate cluster는 기본 대표 1개로 제한한다.
- 희소 stratum은 최소 수량을 보장하되 naver처럼 모집단이 작은 플랫폼은 과도한 소진을 막는다.
- 각 quota 미달분은 인접 stratum으로 deterministic redistribution하고 사유를 manifest에 남긴다.

## 14. Hard Negative 확보

- signal evidence는 존재하지만 실제 구매·사용·착용·섭취·배송·체감이 구체적인 review를 우선한다.
- description signal+personal experience, claim 표현+기간/개인차 한정, 구조화된 장문 정상 후기를 별도 source로 둔다.
- reviewer에게 candidate source를 정답처럼 노출하지 않고, source는 provenance로만 보존한다.
- SUSPICIOUS 확정 후의 반대 사례가 아니라 label 이전의 독립 sampling stratum이어야 한다.

## 15. Random Normal 대조군

- 모든 suspicious candidate source 비적중 모집단에서 추출한다.
- platform×normalized category×length band로 stratify하고 product/cluster cap을 적용한다.
- 10K 기준 1,500건(15%)부터 시작하고, source false-positive가 높으면 20K에서 17.5%로 확대한다.
- random control에도 human label은 blank로 두며 NORMAL로 선입력하지 않는다.

## 16. 다음 구현 단계

1. 이 category mapping의 ETC_UNKNOWN/ambiguous root를 사람이 검토해 mapping v1을 고정한다.
2. EXTREME/IMMEDIATE claim analyzer를 작은 stratified sample에서 precision calibration한다.
3. promotional/repeated-short analyzer와 exact cluster manifest를 만든다.
4. 1.15M용 near-duplicate blocking 설계를 별도 승인받고 cluster audit을 수행한다.
5. model inference 없이 가능한 source manifest부터 생성하고 overlap/yield를 측정한다.
6. P_text scored manifest가 외부에서 제공될 때 HIGH/BOUNDARY source를 합친다.
7. multi-source merge manifest를 검증한 뒤 10K quota를 dry-run한다.
8. category/platform/source/product/cluster coverage 보고서를 승인받은 후에만 최종 pool을 생성한다.
9. future annotation에서는 `candidate_sources`와 human `pattern_type`을 분리한다. human pattern은 겹칠 수 있으므로 `primary_pattern_type`+`secondary_pattern_types` 또는 multi-value field를 검토하되 현재 schema는 수정하지 않는다.

## Description candidate 편향 실측

### DESCRIPTION_V1

- manifest/matched: 574/574
- platforms: `{'elevenst': 62, 'kurly': 7, 'musinsa': 15, 'oliveyoung': 490}`
- provisional categories: `{'HEALTH_SUPPLEMENT': 72, 'ELECTRONICS': 9, 'ETC_UNKNOWN': 6, 'BEAUTY': 439, 'FASHION': 4, 'PET': 1, 'LIVING': 10, 'SPORTS_OUTDOOR': 6, 'FOOD': 26, 'BABY': 1}`
- unique products: 402

### DESCRIPTION_V2

- manifest/matched: 387/387
- platforms: `{'elevenst': 29, 'kurly': 5, 'musinsa': 11, 'oliveyoung': 342}`
- provisional categories: `{'HEALTH_SUPPLEMENT': 34, 'ELECTRONICS': 5, 'ETC_UNKNOWN': 3, 'BEAUTY': 309, 'FASHION': 3, 'LIVING': 7, 'SPORTS_OUTDOOR': 5, 'FOOD': 20, 'BABY': 1}`
- unique products: 300

### DESCRIPTION_V2_HIGH

- manifest/matched: 26/26
- platforms: `{'elevenst': 1, 'oliveyoung': 25}`
- provisional categories: `{'BEAUTY': 22, 'HEALTH_SUPPLEMENT': 3, 'BABY': 1}`
- unique products: 26

### HUMAN_SUSPICIOUS

- manifest/matched: 24/24
- platforms: `{'elevenst': 1, 'oliveyoung': 23}`
- provisional categories: `{'BEAUTY': 20, 'HEALTH_SUPPLEMENT': 3, 'BABY': 1}`
- unique products: 24

### HUMAN_NORMAL

- manifest/matched: 2/2
- platforms: `{'oliveyoung': 2}`
- provisional categories: `{'BEAUTY': 2}`
- unique products: 2

V2 387건 중 oliveyoung은 342건(88.4%)이다. 현재 description candidate 결과를 미래 전체 pool의 category/platform 분포 기준으로 사용하면 안 된다.

## Annotation vocabulary 설계 의견

- 현재 schema는 변경하지 않는다.
- future pool에서는 `candidate_sources`(machine/rule provenance)와 `human_pattern_type`(사람 판단)을 분리한다.
- extreme, immediate, promotional은 동시에 성립할 수 있으므로 단일 pattern만 강제하면 정보 손실이 있다.
- 권장안: 단일 `human_label` + `primary_pattern_type` + optional multi-value `secondary_pattern_types`; reviewer UI가 어렵다면 우선 primary만 받고 adjudication에서 secondary를 보강한다.
