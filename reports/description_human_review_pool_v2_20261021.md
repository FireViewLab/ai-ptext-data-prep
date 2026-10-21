# P_text Description Candidate — V2 Human Review Pool

이 결과는 사람이 직접 검토할 HIGH/MEDIUM 후보입니다. HIGH/MEDIUM은 
SUSPICIOUS/NORMAL 라벨이 아니며 자동 라벨링을 수행하지 않았습니다.

## Counts

| metric | count |
| --- | ---: |
| V1 candidate pool | 574 |
| V2 HIGH | 26 |
| V2 MEDIUM | 361 |
| V2 NOT_CANDIDATE | 187 |
| V2 survivor total | 387 |
| Reduction | 187 (32.58%) |

## Platform distribution

| platform | HIGH | MEDIUM | TOTAL |
| --- | ---: | ---: | ---: |
| elevenst | 1 | 28 | 29 |
| kurly | 0 | 5 | 5 |
| musinsa | 0 | 11 | 11 |
| naver | 0 | 0 | 0 |
| ohouse | 0 | 0 | 0 |
| oliveyoung | 25 | 317 | 342 |

플랫폼 분포는 suspicious prevalence가 아니라 후보 pool의 구성입니다.

## Integrity

- candidate_id duplicates: 0
- normalized-content duplicates: 0
- blank human_label: 387
- blank pattern_type: 387
- blank review_note: 387
- HIGH rows contiguous first: True

## Human review guidance

사람이 `human_label`에 입력할 수 있는 값:

- `SUSPICIOUS`
- `NORMAL`
- `UNCERTAIN`

`pattern_type` 예시:

- `PRODUCT_DESCRIPTION_REPLACEMENT`
- `OTHER`
- `UNKNOWN`

CSV의 `human_label`, `pattern_type`, `review_note`는 모두 빈 칸입니다.

## Regression sanity

| candidate_id | V1 | V2 | excluded |
| --- | --- | --- | --- |
| NEW-DESC-000005 | HIGH | NOT_CANDIDATE | True |
| NEW-DESC-000026 | HIGH | NOT_CANDIDATE | True |
| NEW-DESC-000047 | HIGH | NOT_CANDIDATE | True |

## Safety

- 입력 574건 CSV를 read-only로 재평가했습니다.
- 1.15M raw review를 재스캔하지 않았습니다.
- 모델 inference, training, embedding, fuzzy matching, LLM labeling을 수행하지 않았습니다.
- 이 CSV는 training dataset이 아니라 human-review candidate pool입니다.
