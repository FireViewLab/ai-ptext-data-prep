# 신규 리뷰 데이터 Inventory

이 보고서는 READ-ONLY inventory와 exact overlap 진단입니다. 데이터 병합, 삭제, 라벨링, fuzzy similarity, embedding, 모델 추론 또는 모델 학습을 수행하지 않았습니다.

## 기준 데이터와 비교 정책

- 기준 파일: `outputs/merged_reviews.xlsx` / 시트: `Reviews` / 8,965행
- 기준 platform 값: `{'ohouse': 5111, 'elevenst': 713, 'oliveyoung': 3066, 'musinsa': 75}`
- platform은 CSV 실제 값을 사용하며 파일명 기준 예상값으로 임의 치환하지 않습니다.
- identity는 platform + product_id + review_id 세 값이 모두 있을 때만 비교합니다.
- ID 문자열은 leading zero와 문자열 `.0`을 포함해 그대로 유지합니다. 숫자형 정수와 정수형 float만 기존 식별자 진단 정책에 따라 정수 십진 문자열로 비교합니다.
- normalized content는 비어 있지 않은 값을 문자열화하고 양끝/연속 whitespace만 정리합니다. 대소문자, 문장부호, 한글, 영문, 숫자는 제거하지 않습니다.

## Platform 매핑 확인

| 입력 파일 기준 | CSV 실제 platform 값과 행 수 | 정확히 일치 |
| --- | --- | --- |
| elevenst | `{'elevenst': 171052}` | 예 |
| kurly | `{'kurly': 463843}` | 예 |
| musinsa | `{'musinsa': 118192}` | 예 |
| naver | `{'naver': 1286}` | 예 |
| ohouse | `{'ohouse': 6828}` | 예 |
| oliveyoung | `{'oliveyoung': 390742}` | 예 |

## 구조 호환성

- 6개 신규 CSV 컬럼 순서/목록 동일: 예
- 신규 CSV 컬럼: `['platform', 'product_id', 'review_id', 'content', 'rating', 'written_at', 'option', 'image_count', 'helpful_count', 'product_name', 'product_category', 'first_collected_at']`
- 기준과 공통: `['platform', 'product_id', 'review_id', 'content', 'rating', 'written_at', 'option', 'helpful_count']`
- 기준에만 존재: `['author', 'images', 'collected_at']`
- 신규 CSV에만 존재: `['image_count', 'product_name', 'product_category', 'first_collected_at']`
- 핵심 platform/product_id/review_id/content/rating은 호환되지만 전체 스키마는 동일하지 않습니다. 이번 분석에서는 병합하거나 컬럼을 변환하지 않았습니다.

## 플랫폼별 Inventory

| platform | rows | unique product | unique review | unique product+review | blank content | full-row dup extras | review-id dup extras | normalized-content dup extras | same-product content dup extras | <20 chars | rating blank |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| elevenst | 171,052 | 1,949 | 149,938 | 171,052 | 0 | 0 | 21,114 | 28,520 | 4,394 | 20,561 (12.02%) | 0 |
| kurly | 463,843 | 2,366 | 450,976 | 463,843 | 0 | 0 | 12,867 | 39,678 | 4,684 | 230,021 (49.59%) | 463,843 |
| musinsa | 118,192 | 1,827 | 118,192 | 118,192 | 0 | 0 | 0 | 7,947 | 7,062 | 24 (0.02%) | 0 |
| naver | 1,286 | 56 | 1,286 | 1,286 | 0 | 0 | 0 | 24 | 15 | 145 (11.28%) | 0 |
| ohouse | 6,828 | 100 | 6,828 | 6,828 | 0 | 0 | 0 | 129 | 103 | 0 (0.00%) | 0 |
| oliveyoung | 390,742 | 2,230 | 371,961 | 390,742 | 0 | 0 | 18,781 | 36,436 | 11,225 | 5 (0.00%) | 0 |

## Content 길이

normalized nonblank content 문자 수 기준입니다.

| platform | min | median | mean | max |
| --- | ---: | ---: | ---: | ---: |
| elevenst | 1 | 55.00 | 70.06 | 2,974 |
| kurly | 1 | 20.00 | 28.96 | 3,614 |
| musinsa | 5 | 42.00 | 64.85 | 1,445 |
| naver | 9 | 83.00 | 126.47 | 3,058 |
| ohouse | 20 | 96.00 | 117.29 | 1,226 |
| oliveyoung | 14 | 74.00 | 134.57 | 1,613 |

## 기존 8,965건과 Exact overlap

| platform | identity overlap rows | same-platform review_id overlap rows | normalized content overlap rows | new identity rows | new unique normalized contents |
| --- | ---: | ---: | ---: | ---: | ---: |
| elevenst | 360 | 394 | 559 | 170,692 | 142,163 |
| kurly | 0 | 0 | 19 | 463,843 | 424,161 |
| musinsa | 1 | 1 | 72 | 118,191 | 110,242 |
| naver | 0 | 0 | 0 | 1,286 | 1,262 |
| ohouse | 324 | 324 | 326 | 6,504 | 6,373 |
| oliveyoung | 1,179 | 1,409 | 1,669 | 389,563 | 353,061 |

## 핵심 답변

1. 새 원본은 총 **1,151,943행**입니다.
2. 플랫폼별 규모는 위 Inventory 표와 같습니다.
3. 신규 CSV끼리는 구조가 동일. 기준 Excel과는 핵심 5개 필드는 호환되지만 전체 컬럼은 다릅니다.
4. 즉시 확인할 품질 이슈는 아래 주의사항에 정리했습니다.
5. 기존 데이터와 identity가 겹치는 incoming row는 **1,864행**, normalized content가 겹치는 incoming row는 **2,645행**입니다.
6. 완전한 identity 중 기존과 겹치지 않는 incoming row는 **1,150,079행**입니다. identity 판정 불가 행은 0행입니다.
7. incoming 전체 normalized unique content는 **1,038,436개**, 기존에 없는 신규 normalized unique content는 **1,036,492개**입니다.
8. candidate extraction 입력으로 활용할 수 있지만, blank/short content와 exact duplicate를 정책에 따라 별도 처리하고 스키마 매핑을 먼저 확정해야 합니다. 이번 단계에서는 처리하지 않았습니다.
9. 플랫폼별 중복·결측과 구조 차이는 위 표 및 아래 주의사항을 따라야 합니다.

## 신규 데이터 내부 플랫폼 간 exact content

- 2개 이상 입력 플랫폼에 등장한 normalized content 그룹: 756개
- 해당 그룹 참여 incoming row: 6,926행
- 플랫폼 간 동일 문장은 삭제 또는 이상 판정 근거가 아닙니다.

## 품질 및 사용 주의사항

- elevenst: blank content 0, identity 불완전 0, malformed row 0, 여러 product_id에 걸친 동일 review_id 9,225개.
- kurly: blank content 0, identity 불완전 0, malformed row 0, 여러 product_id에 걸친 동일 review_id 12,556개.
- musinsa: blank content 0, identity 불완전 0, malformed row 0, 여러 product_id에 걸친 동일 review_id 0개.
- naver: blank content 0, identity 불완전 0, malformed row 0, 여러 product_id에 걸친 동일 review_id 0개.
- ohouse: blank content 0, identity 불완전 0, malformed row 0, 여러 product_id에 걸친 동일 review_id 0개.
- oliveyoung: blank content 0, identity 불완전 0, malformed row 0, 여러 product_id에 걸친 동일 review_id 17,069개.
- Full-row duplicate는 CSV header 순서의 모든 파싱 문자열을 SHA-256으로 직렬화해 계산했습니다.
- identity overlap과 content overlap은 서로 겹칠 수 있으므로 합산해 제거 건수로 해석하면 안 됩니다.
- `new identity rows`는 identity가 완전한 행만 포함합니다. 결측 identity 행을 신규라고 임의 분류하지 않습니다.
- 원문 content, 사용자 식별 정보, 전체 ID 목록은 보고서에 포함하지 않았습니다.
