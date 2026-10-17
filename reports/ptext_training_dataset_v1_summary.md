# P_text training dataset v1

모델 입력은 content 한 컬럼만 사용합니다. label_origin, synthetic_type, ID, platform 등은 모델 입력에서 제외합니다.
실제 사람 검토 라벨 / 비후보 추정 NORMAL / synthetic SUSPICIOUS를 별도로 기록합니다.

## total

| 항목 | 수 |
| --- | ---: |
| total | 3403 |

## label

| 항목 | 수 |
| --- | ---: |
| NORMAL | 2052 |
| SUSPICIOUS | 1351 |

## label_origin

| 항목 | 수 |
| --- | ---: |
| human_candidate_review | 552 |
| human_suspicious | 1 |
| sampled_non_candidate | 1500 |
| synthetic | 1350 |

## synthetic_type

| 항목 | 수 |
| --- | ---: |
| [real/empty] | 2053 |
| PRODUCT_DESCRIPTION_REPLACEMENT | 270 |
| NO_USE_ASSERTIVE_RECOMMENDATION | 270 |
| PROMOTIONAL_TEMPLATE | 270 |
| EXPERIENCE_FREE_CLAIM | 270 |
| COPY_VARIATION | 270 |

## platform

| 항목 | 수 |
| --- | ---: |
| ohouse | 1922 |
| elevenst | 191 |
| oliveyoung | 1261 |
| musinsa | 29 |

## split

| 항목 | 수 |
| --- | ---: |
| test | 511 |
| train | 2381 |
| validation | 511 |

## evaluation_set

| 항목 | 수 |
| --- | ---: |
| real_human_evaluation | 166 |
| training | 2381 |
| weak_label_evaluation | 450 |
| synthetic_challenge | 406 |

## platform_x_label

| 항목 | 수 |
| --- | ---: |
| ohouse &#124; NORMAL | 1175 |
| elevenst &#124; NORMAL | 118 |
| oliveyoung &#124; NORMAL | 739 |
| musinsa &#124; NORMAL | 20 |
| oliveyoung &#124; SUSPICIOUS | 522 |
| ohouse &#124; SUSPICIOUS | 747 |
| elevenst &#124; SUSPICIOUS | 73 |
| musinsa &#124; SUSPICIOUS | 9 |

## split_x_label

| 항목 | 수 |
| --- | ---: |
| test &#124; NORMAL | 308 |
| train &#124; NORMAL | 1436 |
| validation &#124; NORMAL | 308 |
| train &#124; SUSPICIOUS | 945 |
| validation &#124; SUSPICIOUS | 203 |
| test &#124; SUSPICIOUS | 203 |

## split_x_label_origin

| 항목 | 수 |
| --- | ---: |
| test &#124; human_candidate_review | 83 |
| train &#124; human_candidate_review | 386 |
| validation &#124; human_candidate_review | 83 |
| train &#124; human_suspicious | 1 |
| validation &#124; sampled_non_candidate | 225 |
| train &#124; sampled_non_candidate | 1050 |
| test &#124; sampled_non_candidate | 225 |
| train &#124; synthetic | 944 |
| validation &#124; synthetic | 203 |
| test &#124; synthetic | 203 |

## evaluation_set_x_split_x_label

| 항목 | 수 |
| --- | ---: |
| real_human_evaluation &#124; test &#124; NORMAL | 83 |
| training &#124; train &#124; NORMAL | 1436 |
| real_human_evaluation &#124; validation &#124; NORMAL | 83 |
| training &#124; train &#124; SUSPICIOUS | 945 |
| weak_label_evaluation &#124; validation &#124; NORMAL | 225 |
| weak_label_evaluation &#124; test &#124; NORMAL | 225 |
| synthetic_challenge &#124; validation &#124; SUSPICIOUS | 203 |
| synthetic_challenge &#124; test &#124; SUSPICIOUS | 203 |

## 검증 및 생성 정보

```json
{
  "seed": 42,
  "input_reviews": 8965,
  "human_labels": {
    "NORMAL": 552,
    "UNCERTAIN": 35,
    "SUSPICIOUS": 1
  },
  "input_platform_counts": {
    "ohouse": 5111,
    "elevenst": 713,
    "oliveyoung": 3066,
    "musinsa": 75
  },
  "uncertain_excluded": 35,
  "sample_requested": 1500,
  "sample_actual": 1500,
  "sample_platforms": {
    "ohouse": 876,
    "elevenst": 98,
    "oliveyoung": 514,
    "musinsa": 12
  },
  "eligible_non_candidate_pool": 8224,
  "near_threshold": 0.85,
  "real_near_edges": 283,
  "final_near_edges": 552,
  "leakage": {
    "group_id": 0,
    "parent_review_id": 0,
    "synthetic_family_id": 0,
    "parent_source_row": 0
  },
  "largest_group": 30,
  "human_normal_split": {
    "test": 83,
    "train": 386,
    "validation": 83
  },
  "synthetic_unique_texts": 1350,
  "synthetic_length_min_max": [
    25,
    284
  ]
}
```

## 평가와 한계

- 그룹 단위 70/15/15 목표 분할입니다. 연결된 원문/부모/유사문장 그룹은 쪼개지 않으므로 실제 비율은 달라질 수 있습니다.
- 모든 실제 원문의 공백 정리 후 exact 중복 및 길이 15자 이상 char_wb 3~5-gram cosine 유사도 기준 연결요소를 그룹화합니다. 최종 synthetic까지 포함해 다시 검사합니다. 이 기준 이하의 의미상 유사성까지 보장하지 않습니다.
- 사람이 검토한 NORMAL은 전부 유지합니다. 비후보 샘플은 검토 후보와 같은 유사 그룹도 제외하고 platform 비례 샘플링합니다. musinsa는 최대 20건만 추가 샘플링하며 데이터 자체가 적습니다.
- sampled_non_candidate는 사람이 확인한 NORMAL이 아닌 약한 추정 라벨입니다. 별도 수동 확인이 필요합니다.
- Real-data evaluation set: validation/test의 human_candidate_review 및 human_suspicious만 평가합니다. weak_label_evaluation은 별도로 보고하고 확정 라벨 성능과 섞지 않습니다.
- Synthetic challenge set: validation/test의 synthetic 행을 별도로 평가합니다. 실제 조작 리뷰 성능의 대체 지표로 사용하지 않습니다.
- 실제 SUSPICIOUS가 현재 1건뿐이므로 실제 positive recall을 신뢰성 있게 측정할 수 없습니다. 그 행이 train에 배정되면 실제 평가셋의 positive recall은 정의할 수 없습니다.
- synthetic은 원문에서 확인되는 상품/속성 어휘를 이용한 재현 가능한 조합형 생성입니다. 사람이나 외부 생성 모델의 검수를 거친 자연어가 아니며 부자연스러운 문장과 공통 문체가 남을 수 있습니다.
- synthetic의 효능·성능 단정은 인위적으로 만든 주장입니다. 실제 제품의 확인된 사실이 아닙니다. synthetic_type별 균형, 고유 본문 및 길이 범위를 기록하지만 의미적 다양성이나 품질을 보장하지 않습니다.
- COPY_VARIATION은 같은 홍보성 prototype의 어휘/문장 순서 변형이며 동일 family와 원본 부모 그룹에 묶습니다. 리뷰 간 유사성 자체는 P_text 위험 라벨 근거가 아닙니다. 각 변형의 경험 없는 홍보 본문을 인위적 challenge로 사용하는 것입니다.
- 자동 생성 레이블을 실제 사람이 확인한 레이블로 간주하지 마세요. 모델 학습은 수행하지 않았습니다.

## 입력 원본 SHA256

- outputs\merged_reviews.xlsx: `20cdbc55e40fb69394cbf4cf5462e0dc02f4500cbcbfd8e5d772ec403286fbf4`
- outputs\merged_ptext_candidates_human_review_labeled_v1.xlsx: `b5dd31e1bd1eb4dbe094fab49fc8fa3cf28646bac61a00a8907f13b12a2dd32b`

Test synthetic 비율: 203/511 (39.73%)
