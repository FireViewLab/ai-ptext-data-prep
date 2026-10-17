# P_text training dataset v1 품질 audit

- 입력: outputs/ptext_training_dataset_v1.xlsx / dataset (3403행)
- 입력 SHA256: `1f305a0196884269cc05487e830288aed2f50ec637fc906103c2a96c007696e0`
- 무작위 샘플 seed: 42
- 데이터셋·라벨은 읽기 전용으로 검사했습니다. 정제, 재라벨링, 학습을 수행하지 않았습니다.

## 1. 동일 원문 label 충돌

충돌 content 그룹 0개 / 참여 행 0개 / NORMAL×SUSPICIOUS pair 0개.

## 2. Exact duplicate

원문 공백·줄바꿈을 포함한 정확한 문자열 동등성 기준입니다. 그룹 수 / 최초 행 포함 참여 행 / 최초 1행을 뺀 추가 행을 구분합니다. 타입별 집계는 해당 타입 내부 중복입니다.

| 범위 | 중복 그룹 | 참여 행 | 추가 중복 행 |
| --- | --- | --- | --- |
| all | 136 | 341 | 205 |
| NORMAL | 136 | 341 | 205 |
| SUSPICIOUS | 0 | 0 | 0 |
| PRODUCT_DESCRIPTION_REPLACEMENT | 0 | 0 | 0 |
| NO_USE_ASSERTIVE_RECOMMENDATION | 0 | 0 | 0 |
| PROMOTIONAL_TEMPLATE | 0 | 0 | 0 |
| EXPERIENCE_FREE_CLAIM | 0 | 0 | 0 |
| COPY_VARIATION | 0 | 0 | 0 |

## 3. Synthetic 다양성

길이는 원본 문자열의 문자 수입니다.

| 유형 | 행 수 | 평균 | 중앙값 | 최소 | 최대 |
| --- | --- | --- | --- | --- | --- |
| PRODUCT_DESCRIPTION_REPLACEMENT | 270 | 98.46 | 95.0 | 49 | 284 |
| NO_USE_ASSERTIVE_RECOMMENDATION | 270 | 79.09 | 70.0 | 55 | 110 |
| PROMOTIONAL_TEMPLATE | 270 | 83.47 | 80.0 | 64 | 110 |
| EXPERIENCE_FREE_CLAIM | 270 | 75.46 | 65.0 | 25 | 281 |
| COPY_VARIATION | 270 | 83.73 | 79.5 | 62 | 123 |
| real NORMAL | 2052 | 125.78 | 88.0 | 4 | 1327 |
| all synthetic | 1350 | 84.04 | 80.0 | 25 | 284 |

### 시작 구문

진단용으로만 공백을 정리한 첫 4개 어절을 집계합니다. 시작 4어절이 같다고 전체 원문이 동일하다는 뜻은 아닙니다. 유형 내 비율 10% 이상은 집중 검토 대상으로 표시합니다.

#### PRODUCT_DESCRIPTION_REPLACEMENT

| 시작 4어절 | 행 수 | 유형 내 비율 | 검토 표시 |
| --- | --- | --- | --- |
| 기본에 충실한 구성을 찾는 | 22 | 8.15% |  |
| 사용 방법은 필요한 상황에 | 22 | 8.15% |  |
| 실용성을 우선하는 분들을 위한 | 19 | 7.04% |  |
| 일상의 번거로움을 줄이고 싶은 | 15 | 5.56% |  |
| 완성도를 중요하게 보는 분들을 | 13 | 4.81% |  |
| 선택에 시간을 쓰고 싶지 | 11 | 4.07% |  |
| 하나로 간단히 해결하고 싶은 | 11 | 4.07% |  |
| 편리한 관리를 원하는 분들을 | 9 | 3.33% |  |
| 이 제품에서 주목할 점은 | 8 | 2.96% |  |
| 부담 없이 시작하려는 분들을 | 6 | 2.22% |  |

#### NO_USE_ASSERTIVE_RECOMMENDATION

| 시작 4어절 | 행 수 | 유형 내 비율 | 검토 표시 |
| --- | --- | --- | --- |
| 사용 전이라는 점부터 밝히자면 | 44 | 16.30% | 집중 반복 |
| 실제로 시험해 본 적은 | 32 | 11.85% | 집중 반복 |
| 직접 써보기 전인 지금도 | 32 | 11.85% | 집중 반복 |
| 실사용 기록은 아직 없지만 | 27 | 10.00% | 집중 반복 |
| 개봉 전이라 써 본 | 27 | 10.00% | 집중 반복 |
| 직접 확인은 못 한 | 24 | 8.89% |  |
| 아직 실사용은 하지 않았어요. | 23 | 8.52% |  |
| 받아놓고 사용은 미뤄둔 상태지만 | 23 | 8.52% |  |
| 아직 직접 사용해 보지는 | 20 | 7.41% |  |
| 아직 첫 사용도 안 | 18 | 6.67% |  |

#### PROMOTIONAL_TEMPLATE

| 시작 4어절 | 행 수 | 유형 내 비율 | 검토 표시 |
| --- | --- | --- | --- |
| 여러 면을 함께 따지면 | 25 | 9.26% |  |
| 선택의 기준을 모아 보면 | 19 | 7.04% |  |
| 누구나 부담 없이 선택할 | 11 | 4.07% |  |
| 첫 선택부터 좋은 인상을 | 11 | 4.07% |  |
| 품질, 가격, 편의성을 함께 | 10 | 3.70% |  |
| 구성은 알차고 가격은 합리적이라 | 10 | 3.70% |  |
| 찾고 있었다면 이번에 구매해 | 10 | 3.70% |  |
| 한 번 선택해 보시길 | 9 | 3.33% |  |
| 전체적인 균형을 보면 탄탄한 | 8 | 2.96% |  |
| 고민할 필요 없이 실속과 | 8 | 2.96% |  |

#### EXPERIENCE_FREE_CLAIM

| 시작 4어절 | 행 수 | 유형 내 비율 | 검토 표시 |
| --- | --- | --- | --- |
| 다른 조건을 따질 필요 | 17 | 6.30% |  |
| 이 제품에서 주목할 점은 | 12 | 4.44% |  |
| 일상의 번거로움을 줄이고 싶은 | 9 | 3.33% |  |
| 제품 쪽에서 눈여겨볼 부분은 | 7 | 2.59% |  |
| 활용도 면에서는 필요한 결과를 | 6 | 2.22% |  |
| 편리한 관리를 원하는 분들을 | 5 | 1.85% |  |
| 제품 관련 구성을 보면 | 5 | 1.85% |  |
| 누가 선택하든 청소 관련 | 5 | 1.85% |  |
| 청소 면에서는 필요한 결과를 | 4 | 1.48% |  |
| 조건이 달라져도 활용도에는 차이가 | 4 | 1.48% |  |

#### COPY_VARIATION

| 시작 4어절 | 행 수 | 유형 내 비율 | 검토 표시 |
| --- | --- | --- | --- |
| 여러 면을 함께 따지면 | 13 | 4.81% |  |
| 다른 걸 찾기 전에 | 11 | 4.07% |  |
| 기대하는 기본은 모두 갖췄고 | 11 | 4.07% |  |
| 구성은 알차고 가격은 합리적이라 | 10 | 3.70% |  |
| 전체적인 균형을 보면 균형 | 10 | 3.70% |  |
| 선택지의 기준을 모아 보면 | 9 | 3.33% |  |
| 첫 선택지부터 좋은 인상을 | 8 | 2.96% |  |
| 일상에 필요한 가치를 한데 | 8 | 2.96% |  |
| 품질, 가격, 편의성을 함께 | 8 | 2.96% |  |
| 편의성과 품질을 두루 갖췄으니 | 7 | 2.59% |  |

#### all synthetic

| 시작 4어절 | 행 수 | 유형 내 비율 | 검토 표시 |
| --- | --- | --- | --- |
| 사용 전이라는 점부터 밝히자면 | 44 | 3.26% |  |
| 여러 면을 함께 따지면 | 38 | 2.81% |  |
| 실제로 시험해 본 적은 | 32 | 2.37% |  |
| 직접 써보기 전인 지금도 | 32 | 2.37% |  |
| 실사용 기록은 아직 없지만 | 27 | 2.00% |  |
| 개봉 전이라 써 본 | 27 | 2.00% |  |
| 선택의 기준을 모아 보면 | 25 | 1.85% |  |
| 일상의 번거로움을 줄이고 싶은 | 24 | 1.78% |  |
| 직접 확인은 못 한 | 24 | 1.78% |  |
| 실용성을 우선하는 분들을 위한 | 23 | 1.70% |  |
| 기본에 충실한 구성을 찾는 | 23 | 1.70% |  |
| 아직 실사용은 하지 않았어요. | 23 | 1.70% |  |
| 받아놓고 사용은 미뤄둔 상태지만 | 23 | 1.70% |  |
| 사용 방법은 필요한 상황에 | 22 | 1.63% |  |
| 이 제품에서 주목할 점은 | 20 | 1.48% |  |
| 아직 직접 사용해 보지는 | 20 | 1.48% |  |
| 구성은 알차고 가격은 합리적이라 | 20 | 1.48% |  |
| 아직 첫 사용도 안 | 18 | 1.33% |  |
| 품질, 가격, 편의성을 함께 | 18 | 1.33% |  |
| 완성도를 중요하게 보는 분들을 | 17 | 1.26% |  |

### 반복 구문

문장부호를 제외한 연속 2~5어절(6자 이상)의 문서 빈도입니다. 한 리뷰에서 여러 번 나와도 1회만 셉니다. 같은 빈도의 포함 구문은 가능한 한 긴 구문을 표시합니다.

#### PRODUCT_DESCRIPTION_REPLACEMENT

| 반복 구문 | 포함 리뷰 수 | 유형 내 비율 |
| --- | --- | --- |
| 분들을 위한 | 230 | 85.19% |
| 싶은 분들을 위한 | 67 | 24.81% |
| 함께 고려한 | 56 | 20.74% |
| 중심으로 사용 목적을 정리하고 | 53 | 19.63% |
| 측면까지 연결한 형태입니다 | 53 | 19.63% |
| 관련 요구를 함께 다루도록 만들었습니다 | 51 | 18.89% |
| 중심의 설계로 | 51 | 18.89% |
| 필요한 상황에 맞춰 적용하는 방식이며 | 49 | 18.15% |
| 방법은 필요한 상황에 맞춰 적용하는 | 49 | 18.15% |
| 사용 방법은 필요한 상황에 맞춰 | 49 | 18.15% |
| 관리에 적합합니다 | 49 | 18.15% |
| 구성의 핵심은 | 47 | 17.41% |
| 활용도 중심의 | 43 | 15.93% |
| 함께 고려한 구성이죠 | 40 | 14.81% |
| 관련 구성을 보면 | 40 | 14.81% |
| 주요 특징은 | 40 | 14.81% |
| 청소 중심의 | 39 | 14.44% |
| 부분을 간단하게 관리하도록 구성되어 있어요 | 38 | 14.07% |
| 필요한 부분을 간단하게 관리하도록 구성되어 | 38 | 14.07% |
| 맞춰 필요한 부분을 간단하게 관리하도록 | 38 | 14.07% |

#### NO_USE_ASSERTIVE_RECOMMENDATION

| 반복 구문 | 포함 리뷰 수 | 유형 내 비율 |
| --- | --- | --- |
| 사용 전이라는 점부터 밝히자면 | 44 | 16.30% |
| 비교가 필요 없을 만큼 분명합니다 | 40 | 14.81% |
| 하나는 비교가 필요 없을 만큼 | 40 | 14.81% |
| 차이가 없고 결과는 확실해요 | 39 | 14.44% |
| 조건이 달라져도 | 39 | 14.44% |
| 떨어질 이유는 없습니다 | 36 | 13.33% |
| 어떤 상황에서도 | 36 | 13.33% |
| 관련 걱정은 남지 않습니다 | 33 | 12.22% |
| 누가 선택하든 | 33 | 12.22% |
| 측면에서 실패할 가능성은 없다고 볼 | 32 | 11.85% |
| 가능성은 없다고 볼 수 있어요 | 32 | 11.85% |
| 실제로 시험해 본 적은 없지만 | 32 | 11.85% |
| 실패할 가능성은 없다고 볼 수 | 32 | 11.85% |
| 다른 조건을 따질 필요 없이 | 32 | 11.85% |
| 직접 써보기 전인 지금도 | 32 | 11.85% |
| 믿어도 됩니다 | 32 | 11.85% |
| 관한 기대는 반드시 채워지는 선택이에요 | 29 | 10.74% |
| 면에서는 필요한 결과를 | 29 | 10.74% |
| 지금 준비해 두길 권합니다 | 28 | 10.37% |
| 전이라 써 본 상태는 아닌데 | 27 | 10.00% |

#### PROMOTIONAL_TEMPLATE

| 반복 구문 | 포함 리뷰 수 | 유형 내 비율 |
| --- | --- | --- |
| 여러 면을 함께 따지면 | 75 | 27.78% |
| 전체적인 균형을 보면 | 69 | 25.56% |
| 선택의 기준을 모아 보면 | 65 | 24.07% |
| 가격부터 구성까지 | 61 | 22.59% |
| 있는 선택입니다 | 52 | 19.26% |
| 품질 가격 편의성을 함께 챙길 | 43 | 15.93% |
| 함께 챙길 수 있는 선택입니다 | 43 | 15.93% |
| 가격 편의성을 함께 챙길 수 | 43 | 15.93% |
| 편의성을 함께 챙길 수 있는 | 43 | 15.93% |
| 제품 쪽에서도 | 43 | 15.93% |
| 구성은 알차고 가격은 합리적이라 누구에게나 | 37 | 13.70% |
| 가격은 합리적이라 누구에게나 잘 맞아요 | 37 | 13.70% |
| 알차고 가격은 합리적이라 누구에게나 잘 | 37 | 13.70% |
| 품질을 두루 갖췄으니 비교할수록 돋보입니다 | 36 | 13.33% |
| 편의성과 품질을 두루 갖췄으니 비교할수록 | 36 | 13.33% |
| 좋은 인상을 남길 만한 완성도입니다 | 36 | 13.33% |
| 선택부터 좋은 인상을 남길 만한 | 36 | 13.33% |
| 첫 선택부터 좋은 인상을 남길 | 36 | 13.33% |
| 선택할 수 있고 기대까지 채워줍니다 | 35 | 12.96% |
| 고민할 필요 없이 실속과 만족을 | 35 | 12.96% |

#### EXPERIENCE_FREE_CLAIM

| 반복 구문 | 포함 리뷰 수 | 유형 내 비율 |
| --- | --- | --- |
| 분들을 위한 | 101 | 37.41% |
| 측면에서 실패할 가능성은 없다고 볼 | 48 | 17.78% |
| 가능성은 없다고 볼 수 있어요 | 48 | 17.78% |
| 실패할 가능성은 없다고 볼 수 | 48 | 17.78% |
| 구성의 핵심은 | 46 | 17.04% |
| 구성 중심의 | 44 | 16.30% |
| 조건을 따질 | 43 | 15.93% |
| 관련 걱정은 남지 않습니다 | 40 | 14.81% |
| 누가 선택하든 | 40 | 14.81% |
| 관련 구성을 보면 | 39 | 14.44% |
| 핵심만 정리하면 | 38 | 14.07% |
| 활용도 중심의 | 37 | 13.70% |
| 면에서는 필요한 결과를 | 36 | 13.33% |
| 다른 조건을 따질 필요 없이 | 34 | 12.59% |
| 차이가 없고 결과는 확실해요 | 34 | 12.59% |
| 조건이 달라져도 | 34 | 12.59% |
| 믿어도 됩니다 | 34 | 12.59% |
| 선택의 기준은 | 32 | 11.85% |
| 관한 기대는 반드시 채워지는 선택이에요 | 31 | 11.48% |
| 중심의 안정적인 | 31 | 11.48% |

#### COPY_VARIATION

| 반복 구문 | 포함 리뷰 수 | 유형 내 비율 |
| --- | --- | --- |
| 기준을 모아 보면 | 84 | 31.11% |
| 전체적인 균형을 보면 | 72 | 26.67% |
| 여러 면을 함께 따지면 | 57 | 21.11% |
| 가격부터 구성까지 | 57 | 21.11% |
| 제품 쪽에서도 | 54 | 20.00% |
| 선택지의 기준을 모아 보면 | 48 | 17.78% |
| 수 있고 기대까지 채워줍니다 | 42 | 15.56% |
| 누구나 부담 없이 | 42 | 15.56% |
| 구성은 알차고 가격은 합리적이라 누구에게나 | 39 | 14.44% |
| 가격은 합리적이라 누구에게나 잘 맞아요 | 39 | 14.44% |
| 알차고 가격은 합리적이라 누구에게나 잘 | 39 | 14.44% |
| 가치를 한데 모았다는 점이 매력입니다 | 39 | 14.44% |
| 일상에 필요한 가치를 한데 모았다는 | 39 | 14.44% |
| 필요한 가치를 한데 모았다는 점이 | 39 | 14.44% |
| 보면 균형 잡힌 | 39 | 14.44% |
| 선택의 기준을 모아 보면 | 36 | 13.33% |
| 정착해 보세요 | 36 | 13.33% |
| 품질을 두루 갖췄으니 비교할수록 돋보입니다 | 33 | 12.22% |
| 편의성과 품질을 두루 갖췄으니 비교할수록 | 33 | 12.22% |
| 보시길 바라요 | 31 | 11.48% |

#### all synthetic

| 반복 구문 | 포함 리뷰 수 | 유형 내 비율 |
| --- | --- | --- |
| 분들을 위한 | 331 | 24.52% |
| 기준을 모아 보면 | 149 | 11.04% |
| 전체적인 균형을 보면 | 141 | 10.44% |
| 여러 면을 함께 따지면 | 132 | 9.78% |
| 군더더기 없는 | 129 | 9.56% |
| 가격부터 구성까지 | 118 | 8.74% |
| 구성의 핵심은 | 113 | 8.37% |
| 구성 중심의 | 104 | 7.70% |
| 활용도 중심의 | 103 | 7.63% |
| 핵심만 정리하면 | 102 | 7.56% |
| 선택의 기준을 모아 보면 | 101 | 7.48% |
| 관련 구성을 보면 | 98 | 7.26% |
| 제품 쪽에서도 | 97 | 7.19% |
| 싶은 분들을 위한 | 93 | 6.89% |
| 조건을 따질 | 92 | 6.81% |
| 쪽에서 눈여겨볼 부분은 | 88 | 6.52% |
| 선택의 기준은 | 85 | 6.30% |
| 주변에도 알려두세요 | 84 | 6.22% |
| 정착해 보세요 | 84 | 6.22% |
| 청소 중심의 | 82 | 6.07% |

### 특정 표현의 라벨 편중

사전 지정한 표현이 포함된 리뷰 수입니다(부분 문자열 기준). 같은 행이 여러 표현에 집계됩니다. SUSPICIOUS의 50% 이상에 나타나면 다수 지배로 표시합니다. 이 목록은 모든 언어적 편향을 망라하지 않습니다.

| 표현 | SUSPICIOUS 포함 수 | SUSPICIOUS 비율 | NORMAL 포함 수 | NORMAL 비율 | 다수 지배 |
| --- | --- | --- | --- | --- | --- |
| 선택 | 829 | 61.36% | 24 | 1.17% | 예 |
| 구성 | 679 | 50.26% | 98 | 4.78% | 예 |
| 확실 | 87 | 6.44% | 95 | 4.63% | 아니오 |
| 보장 | 9 | 0.67% | 1 | 0.05% | 아니오 |
| 기대 | 192 | 14.21% | 59 | 2.88% | 아니오 |
| 품질 | 276 | 20.43% | 24 | 1.17% | 아니오 |
| 만족 | 244 | 18.06% | 419 | 20.42% | 아니오 |
| 추천 | 0 | 0.00% | 232 | 11.31% | 아니오 |
| 구매 | 56 | 4.15% | 607 | 29.58% | 아니오 |
| 제품 | 367 | 27.17% | 388 | 18.91% | 아니오 |
| 관리 | 152 | 11.25% | 82 | 4.00% | 아니오 |
| 중심 | 592 | 43.82% | 3 | 0.15% | 아니오 |
| 분들을 위한 | 331 | 24.50% | 0 | 0.00% | 아니오 |

### 해석과 학습 전 주의

- exact unique 여부는 의미·문체 다양성을 보장하지 않습니다. 서로 다른 문장도 같은 생성 골격과 표현을 공유할 수 있습니다.
- 조합형 synthetic은 같은 시작 구문·연결 표현·확신형 문체를 반복합니다. 위 빈도와 50개 샘플을 보고 사람이 자연스러움 및 타입 적합성을 검토해야 합니다.
- COPY_VARIATION의 문구 반복은 설계상 의도된 특성이지만, 다른 유형의 표현 편중까지 정당화하지는 않습니다.
- 대부분의 SUSPICIOUS가 synthetic이므로, 라벨 편중 표현은 실제 위험 신호가 아니라 생성 방식의 흔적일 수 있습니다. 이 audit은 데이터 변경이나 학습 적합성 인증이 아닙니다.
- 실제 SUSPICIOUS는 1건이며 train에만 존재합니다. 실제 평가셋 positive recall을 검증할 수 없고 synthetic 성능을 실제 성능으로 해석하면 안 됩니다.

## 4. label_origin × split

| label_origin | train | validation | test | 합계 |
| --- | --- | --- | --- | --- |
| human_candidate_review | 386 | 83 | 83 | 552 |
| human_suspicious | 1 | 0 | 0 | 1 |
| sampled_non_candidate | 1050 | 225 | 225 | 1500 |
| synthetic | 944 | 203 | 203 | 1350 |

## 5. platform × label × split

| platform | label | train | validation | test |
| --- | --- | --- | --- | --- |
| elevenst | NORMAL | 82 | 18 | 18 |
| elevenst | SUSPICIOUS | 51 | 11 | 11 |
| musinsa | NORMAL | 15 | 3 | 2 |
| musinsa | SUSPICIOUS | 6 | 1 | 2 |
| ohouse | NORMAL | 820 | 178 | 177 |
| ohouse | SUSPICIOUS | 525 | 111 | 111 |
| oliveyoung | NORMAL | 519 | 109 | 111 |
| oliveyoung | SUSPICIOUS | 363 | 80 | 79 |

## 6. Leakage 재검증

| 검사 | 결과 |
| --- | --- |
| group_id | 0 |
| parent_review_id | 0 |
| synthetic_family_id | 0 |
| parent_source_row | 0 |
| existing_validator | PASS |

group/parent/family의 split 중복 및 실제 부모 행과 자식의 group/split/ID 일치를 확인하고 기존 validate도 재실행했습니다. 유사도 그래프 자체를 재학습하거나 새로운 그룹을 만들지는 않았습니다.

## 7. 재현 가능한 사람 검토 샘플

각 모집단을 dataset Excel 행 순서로 정렬한 뒤 seed=42의 단일 RNG로 유형 순서대로 비복원 추출했습니다. 원문은 HTML escape만 적용해 그대로 표시하며 라벨을 변경하지 않았습니다.

### PRODUCT_DESCRIPTION_REPLACEMENT — 10개

#### Excel 행 2112

- origin: synthetic / label: SUSPICIOUS / platform: elevenst / split: train

<pre>활용도 중심의 설계로 청소 관련 요구를 함께 다루도록 만들었습니다.

일상의 번거로움을 줄이고 싶은 분들을 위한 제품이에요~</pre>

#### Excel 행 2067

- origin: synthetic / label: SUSPICIOUS / platform: ohouse / split: train

<pre>청소 중심으로 사용 목적을 정리하고, 완성도 측면까지 연결한 형태입니다. 구성의 핵심은 청소 중심의 탄탄한 완성도입니다! 편리한 관리를 원하는 분들을 위한 설계예요.</pre>

#### Excel 행 2195

- origin: synthetic / label: SUSPICIOUS / platform: oliveyoung / split: train

<pre>두피, 핵심만 정리하면 두피 중심의 안정적인 완성도입니다. / 하나로 간단히 해결하고 싶은 분들을 위한 설계임 / 주요 특징은 두피. 여기에 완성도까지 함께 고려한 구성이죠.</pre>

#### Excel 행 2180

- origin: synthetic / label: SUSPICIOUS / platform: ohouse / split: train

<pre>일상의 번거로움을 줄이고 싶은 분들을 위한 제품입니다. / 구성의 핵심은 청소 중심의 탄탄한 품질임 / 청소 기능에 초점을 맞춰 필요한 부분을 간단하게 관리하도록 구성되어 있어요.</pre>

#### Excel 행 2169

- origin: synthetic / label: SUSPICIOUS / platform: ohouse / split: validation

<pre>완성도를 중요하게 보는 분들을 위한 선택지라는 점.

제품 관련 구성을 보면 디자인 중심의 간결한 만족도라는 점.</pre>

#### Excel 행 2126

- origin: synthetic / label: SUSPICIOUS / platform: oliveyoung / split: train

<pre>실용성을 우선하는 분들을 위한 구성이에요. / 활용도 중심의 설계로 활용도 관련 요구를 함께 다루도록 만들었습니다.</pre>

#### Excel 행 2107

- origin: synthetic / label: SUSPICIOUS / platform: oliveyoung / split: test

<pre>이 제품에서 주목할 점은 구성 중심의 군더더기 없는 활용도라는 점. / 구성 기능에 초점을 맞춰 필요한 부분을 간단하게 관리하도록 구성되어 있어요. / 부담 없이 시작하려는 분들을 위한 구성이에요~</pre>

#### Excel 행 2099

- origin: synthetic / label: SUSPICIOUS / platform: ohouse / split: train

<pre>선택에 시간을 쓰고 싶지 않은 분들을 위한 선택지임

사용 방법은 필요한 상황에 맞춰 적용하는 방식이며 디자인 관리에 적합합니다.

디자인, 핵심만 정리하면 디자인 중심의 균형 잡힌 편의성이에요~</pre>

#### Excel 행 2271

- origin: synthetic / label: SUSPICIOUS / platform: ohouse / split: train

<pre>제품 관련 구성을 보면 편리 중심의 균형 잡힌 활용도라는 점. / 하나로 간단히 해결하고 싶은 분들을 위한 선택지입니다! / 활용도 중심의 설계로 편리 관련 요구를 함께 다루도록 만들었습니다.</pre>

#### Excel 행 2071

- origin: synthetic / label: SUSPICIOUS / platform: oliveyoung / split: train

<pre>색상 중심으로 사용 목적을 정리하고, 활용도 측면까지 연결한 형태입니다.

색상 관련 구성을 보면 색상 중심의 효율적인 활용도입니다.

일상의 번거로움을 줄이고 싶은 분들을 위한 선택지임</pre>

### NO_USE_ASSERTIVE_RECOMMENDATION — 10개

#### Excel 행 2340

- origin: synthetic / label: SUSPICIOUS / platform: oliveyoung / split: train

<pre>직접 확인은 못 한 상태예요. 그래도 누가 선택하든 활용도 관련 걱정은 남지 않습니다. / 제품 관련 구성을 보면 활용도 중심의 실속 있는 만족도라는 점. / 찾고 있었다면 이번에 구매해 보세요.</pre>

#### Excel 행 2372

- origin: synthetic / label: SUSPICIOUS / platform: ohouse / split: validation

<pre>사용 전이라는 점부터 밝히자면 어떤 상황에서도 편의성가 떨어질 이유는 없습니다. 청소, 핵심만 정리하면 청소 중심의 높은 편의성입니다. 구입을 결정해도 후회 없을 거예요~</pre>

#### Excel 행 2436

- origin: synthetic / label: SUSPICIOUS / platform: ohouse / split: validation

<pre>실사용 기록은 아직 없지만 누가 선택하든 청소 관련 걱정은 남지 않습니다.
이번 선택으로 정착해 보세요~</pre>

#### Excel 행 2444

- origin: synthetic / label: SUSPICIOUS / platform: oliveyoung / split: test

<pre>실제로 시험해 본 적은 없지만 지속력 면에서는 필요한 결과를 빠짐없이 실현합니다.

주변에도 알려두세요.</pre>

#### Excel 행 2583

- origin: synthetic / label: SUSPICIOUS / platform: ohouse / split: train

<pre>직접 써보기 전인 지금도 디자인 면에서는 필요한 결과를 분명하게 보장합니다. 구성의 핵심은 디자인 중심의 높은 완성도예요. 한 번 선택해 보시길 바라요!</pre>

#### Excel 행 2338

- origin: synthetic / label: SUSPICIOUS / platform: elevenst / split: train

<pre>아직 실사용은 하지 않았어요. 그렇지만 조건이 달라져도 가치에는 차이가 없고 결과는 확실해요. / 장바구니에 담아둘 만합니다!</pre>

#### Excel 행 2426

- origin: synthetic / label: SUSPICIOUS / platform: ohouse / split: train

<pre>직접 써보기 전인 지금도 다른 조건을 따질 필요 없이 편의성만큼은 믿어도 됩니다. / 구입을 결정해도 후회 없을 거예요~</pre>

#### Excel 행 2539

- origin: synthetic / label: SUSPICIOUS / platform: ohouse / split: test

<pre>아직 실사용은 하지 않았어요. 그렇지만 청소 면에서는 필요한 결과를 확실하게 구현합니다. 청소, 핵심만 정리하면 청소 중심의 높은 품질이네요 구입을 결정해도 후회 없을 거예요.</pre>

#### Excel 행 2437

- origin: synthetic / label: SUSPICIOUS / platform: ohouse / split: test

<pre>사용 전이라는 점부터 밝히자면 활용도 하나는 비교가 필요 없을 만큼 분명합니다.

제품 선택의 기준은 구성 중심의 안정적인 활용도네요

한 번 선택해 보시길 바라요</pre>

#### Excel 행 2554

- origin: synthetic / label: SUSPICIOUS / platform: ohouse / split: test

<pre>직접 써보기 전인 지금도 어떤 상황에서도 만족도가 떨어질 이유는 없습니다.
필요한 분들께 적극 권해요.</pre>

### PROMOTIONAL_TEMPLATE — 10개

#### Excel 행 2737

- origin: synthetic / label: SUSPICIOUS / platform: ohouse / split: validation

<pre>전구 쪽에서도 실속 있는 선택이라는 점. 망설이지 말고 선택해 보세요 :) 선택의 기준을 모아 보면 실속 있는 편의성이라는 점. 고민할 필요 없이 실속과 만족을 한 번에 챙길 수 있어요.</pre>

#### Excel 행 2598

- origin: synthetic / label: SUSPICIOUS / platform: ohouse / split: test

<pre>전체적인 균형을 보면 안정적인 편의성임 편의성과 품질을 두루 갖췄으니 비교할수록 돋보입니다. 이번 선택으로 정착해 보세요~ 전구 쪽에서도 안정적인 선택이에요.</pre>

#### Excel 행 2676

- origin: synthetic / label: SUSPICIOUS / platform: ohouse / split: validation

<pre>선택의 기준을 모아 보면 간결한 만족도임 / 고민할 필요 없이 실속과 만족을 한 번에 챙길 수 있어요. / 구입을 결정해도 후회 없을 거예요!</pre>

#### Excel 행 2811

- origin: synthetic / label: SUSPICIOUS / platform: oliveyoung / split: test

<pre>선택을 미룰 이유가 없습니다.

일상에 필요한 가치를 한데 모았다는 점이 매력입니다.

선택의 기준을 모아 보면 탄탄한 활용도임</pre>

#### Excel 행 2769

- origin: synthetic / label: SUSPICIOUS / platform: elevenst / split: train

<pre>제품 쪽에서도 효율적인 선택입니다. 여러 면을 함께 따지면 효율적인 실용성입니다. 장바구니에 담아둘 만합니다~ 기대하는 기본은 모두 갖췄고 만족도까지 놓치지 않았어요.</pre>

#### Excel 행 2674

- origin: synthetic / label: SUSPICIOUS / platform: ohouse / split: test

<pre>다른 걸 찾기 전에 이것부터 살펴보세요!
청소용품 쪽에서도 높은 선택이네요
여러 면을 함께 따지면 높은 완성도네요
누구나 부담 없이 선택할 수 있고 기대까지 채워줍니다.</pre>

#### Excel 행 2705

- origin: synthetic / label: SUSPICIOUS / platform: oliveyoung / split: validation

<pre>선택의 기준을 모아 보면 균형 잡힌 구성이에요~
두피 쪽에서도 균형 잡힌 선택임
선택을 미룰 이유가 없습니다 :)
첫 선택부터 좋은 인상을 남길 만한 완성도입니다.</pre>

#### Excel 행 2767

- origin: synthetic / label: SUSPICIOUS / platform: oliveyoung / split: train

<pre>이번 선택으로 정착해 보세요 선택의 기준을 모아 보면 높은 가치입니다! 누구나 부담 없이 선택할 수 있고 기대까지 채워줍니다.</pre>

#### Excel 행 2647

- origin: synthetic / label: SUSPICIOUS / platform: oliveyoung / split: train

<pre>찾고 있었다면 이번에 구매해 보세요 / 여러 면을 함께 따지면 실속 있는 편의성이에요. / 기대하는 기본은 모두 갖췄고 만족도까지 놓치지 않았어요.</pre>

#### Excel 행 2642

- origin: synthetic / label: SUSPICIOUS / platform: ohouse / split: train

<pre>장바구니에 담아둘 만합니다 :)
여러 면을 함께 따지면 효율적인 가치예요.
청소 쪽에서도 효율적인 선택입니다.
편의성과 품질을 두루 갖췄으니 비교할수록 돋보입니다.</pre>

### EXPERIENCE_FREE_CLAIM — 10개

#### Excel 행 3059

- origin: synthetic / label: SUSPICIOUS / platform: oliveyoung / split: test

<pre>매트, 핵심만 정리하면 지속력 중심의 균형 잡힌 완성도입니다.
지속력에 관한 기대는 반드시 채워지는 선택이에요.</pre>

#### Excel 행 2914

- origin: synthetic / label: SUSPICIOUS / platform: oliveyoung / split: train

<pre>이 제품에서 주목할 점은 색상 중심의 간결한 활용도입니다. 누가 선택하든 색상 관련 걱정은 남지 않습니다. 선택할 때 확인할 항목은 색상입니다. 필요한 목적에 맞춰 적용할 수 있도록 구성한 점이 특징이에요.</pre>

#### Excel 행 3048

- origin: synthetic / label: SUSPICIOUS / platform: ohouse / split: train

<pre>어떤 상황에서도 활용도가 떨어질 이유는 없습니다. / 거실 쪽에서 눈여겨볼 부분은 가성비 중심의 균형 잡힌 활용도네요</pre>

#### Excel 행 3041

- origin: synthetic / label: SUSPICIOUS / platform: ohouse / split: train

<pre>청소 관련 구성을 보면 먼지 중심의 효율적인 실용성입니다!

편리한 관리를 원하는 분들을 위한 설계임

먼지 측면에서 실패할 가능성은 없다고 볼 수 있어요.</pre>

#### Excel 행 3000

- origin: synthetic / label: SUSPICIOUS / platform: ohouse / split: train

<pre>청소 쪽에서 눈여겨볼 부분은 청소 중심의 높은 실용성이네요
선택에 시간을 쓰고 싶지 않은 분들을 위한 선택지입니다.
어떤 상황에서도 실용성가 떨어질 이유는 없습니다.</pre>

#### Excel 행 2887

- origin: synthetic / label: SUSPICIOUS / platform: ohouse / split: train

<pre>다른 조건을 따질 필요 없이 실용성만큼은 믿어도 됩니다.</pre>

#### Excel 행 3100

- origin: synthetic / label: SUSPICIOUS / platform: oliveyoung / split: train

<pre>두피에 관한 기대는 반드시 채워지는 선택이에요.</pre>

#### Excel 행 2928

- origin: synthetic / label: SUSPICIOUS / platform: ohouse / split: validation

<pre>누가 선택하든 청소 관련 걱정은 남지 않습니다.
청소도구 쪽에서 눈여겨볼 부분은 청소 중심의 균형 잡힌 품질이에요~</pre>

#### Excel 행 3058

- origin: synthetic / label: SUSPICIOUS / platform: elevenst / split: train

<pre>활용도 면에서는 필요한 결과를 빠짐없이 실현합니다. 조명 쪽에서 눈여겨볼 부분은 활용도 중심의 군더더기 없는 가치예요~</pre>

#### Excel 행 2905

- origin: synthetic / label: SUSPICIOUS / platform: ohouse / split: train

<pre>일상의 번거로움을 줄이고 싶은 분들을 위한 설계예요~

누가 선택하든 디자인 관련 걱정은 남지 않습니다.

디자인 관련 구성을 보면 디자인 중심의 실속 있는 가치입니다.</pre>

### COPY_VARIATION — 10개

#### Excel 행 3285

- origin: synthetic / label: SUSPICIOUS / platform: ohouse / split: validation

<pre>가격부터 구성까지 간결한 편의성이라는 점.
선택을 미룰 이유가 없습니다!
일상에 필요한 가치를 한데 모았다는 점이 매력입니다.</pre>

#### Excel 행 3320

- origin: synthetic / label: SUSPICIOUS / platform: ohouse / split: test

<pre>전체적인 균형을 보면 군더더기 없는 가치네요 한 번 선택지해 보시길 바라요! 누구나 부담 없이 선택지할 수 있고 기대까지 채워줍니다.</pre>

#### Excel 행 3233

- origin: synthetic / label: SUSPICIOUS / platform: ohouse / split: train

<pre>이번 선택지으로 정착해 보세요! 제품 쪽에서도 높은 선택지이에요~ 구성은 알차고 가격은 합리적이라 누구에게나 잘 맞아요. 선택지의 기준을 모아 보면 높은 완성도예요.</pre>

#### Excel 행 3170

- origin: synthetic / label: SUSPICIOUS / platform: ohouse / split: train

<pre>/ 첫 선택지부터 좋은 인상을 남길 만한 완성도입니다. / 걸레 쪽에서도 효율적인 선택지이라는 점. 한 번 선택지해 보시길 바라요. / 선택지의 기준을 모아 보면 효율적인 구성이에요.</pre>

#### Excel 행 3158

- origin: synthetic / label: SUSPICIOUS / platform: oliveyoung / split: train

<pre>장바구니에 담아둘 만합니다 누구나 부담 없이 선택지할 수 있고 기대까지 채워줍니다. 가격부터 구성까지 실속 있는 완성도네요</pre>

#### Excel 행 3251

- origin: synthetic / label: SUSPICIOUS / platform: elevenst / split: train

<pre>지금 준비해 두길 권합니다. / 고민할 필요 없이 실속과 만족을 한 번에 챙길 수 있습니다. / 선택지의 기준을 모아 보면 효율적인 만족도네요</pre>

#### Excel 행 3283

- origin: synthetic / label: SUSPICIOUS / platform: oliveyoung / split: train

<pre>전체적인 균형을 보면 균형 잡힌 활용도예요~ 고민할 필요 없이 실속과 만족을 한 번에 챙길 수 있습니다. 주변에도 알려두세요 :)</pre>

#### Excel 행 3175

- origin: synthetic / label: SUSPICIOUS / platform: oliveyoung / split: train

<pre>선택지의 기준을 모아 보면 균형 잡힌 품질이에요. 선택지을 미룰 이유가 없습니다! 구성은 알차고 가격은 합리적이라 누구에게나 잘 맞아요.</pre>

#### Excel 행 3254

- origin: synthetic / label: SUSPICIOUS / platform: ohouse / split: train

<pre>장바구니에 담아둘 만합니다! 구성은 알차고 가격은 합리적이라 누구에게나 잘 맞아요 :) 주방 쪽에서도 높은 선택이에요~ 선택의 기준을 모아 보면 높은 실용성임 선택을 미룰 이유가 없습니다</pre>

#### Excel 행 3186

- origin: synthetic / label: SUSPICIOUS / platform: ohouse / split: train

<pre>전체적인 균형을 보면 탄탄한 편의성이에요~ / 조립 쪽에서도 탄탄한 선택입니다. / 장바구니에 담아둘 만합니다. / 구성은 알차고 가격은 합리적이라 누구에게나 잘 맞아요.</pre>

### sampled_non_candidate NORMAL — 30개

#### Excel 행 1333

- origin: sampled_non_candidate / label: NORMAL / platform: ohouse / split: train

<pre>일단 조립이 굉장히 쉬워요
밑판이 생각보다 더 튼튼해요 다만 길이를 최대려 을렸을때 약간의 흔들림이나 불안정함은 있어요.
조명의 경우 밝기조절, 색감조정 등의 기능이 있어서 굉장히 좋았고 방향도 자유롭게 조절가능해서 좋아요</pre>

#### Excel 행 1124

- origin: sampled_non_candidate / label: NORMAL / platform: ohouse / split: test

<pre>리뷰에 너무 작다는 글이 많아서 걱정이었는데 진짜 작아요 ㅋㅋ 근데 이것보다 크면 비닐 사이즈가 엄청 커져야해서 가정집에서 쓰고 2-3일에 자주 갈아주랴면 이 사이즈가 적당해요! 그리고 비닐봉투나 쿠팡비닐등 재활용겸 걸어서 묶고 버리면 되니깐 1석 2조에요! 너무 잘 쓰고 있습니다</pre>

#### Excel 행 1483

- origin: sampled_non_candidate / label: NORMAL / platform: elevenst / split: validation

<pre>타사 무선 청소기 사용하다 이 번엔 캐치웰로 바꿔봤어요.. 지인 집에서 L사 제품 써보고 고민했지만 가격대도 비싸고 ㅠ 고심 끝에 선택한 제품이예요! 거치대에 자동 먼지 비움 장치까지 있어 박스 보고 놀랐지만 일단  무게도 괜찮고 깔끔하고 새제품이라 그런지 흡입력도 괜찮아요! 물론 고가 청소기만은 못하지만요~ 고장 없이 오래 썼으면 좋겠어요..참고로 저희 집은 유.무선청소기 같이 사용한답니다.이 가격에 이퀄리티면 추천합니다~</pre>

#### Excel 행 1856

- origin: sampled_non_candidate / label: NORMAL / platform: oliveyoung / split: validation

<pre>건강한 향이 마음에 들고 애벌샴푸 용으로 사용하능데 지성두피한테 좋아요</pre>

#### Excel 행 1302

- origin: sampled_non_candidate / label: NORMAL / platform: ohouse / split: train

<pre>특히 신혼집이 조금 휑하게 느껴졌는데 조명 하나 추가했을 뿐인데 훨씬 따뜻하고 포근한 느낌이 생겨서 만족스럽습니다. 낮에는 소품처럼 두고, 저녁에는 조명으로 사용할 수 있어서 활용도도 좋아요.

큰 조명으로 분위기를 확 바꾸는 것보다 작은 소품으로 은은하게 분위기 내고 싶은 분들께 추천해요! ✨</pre>

#### Excel 행 888

- origin: sampled_non_candidate / label: NORMAL / platform: ohouse / split: train

<pre>청소도구에 따라 시간도 절약 되고 피로도도 낮아 진다는것을 바이칸 쓰면서 깨달았습니다
다른 종류로 더 많이 갖고 싶어서 다음에 또 구입하겠습니다
잘 쓰겠습니다</pre>

#### Excel 행 1313

- origin: sampled_non_candidate / label: NORMAL / platform: ohouse / split: train

<pre>거실 구석에 작은 라운지를 만들고 싶어서 구매했어요. 색 온도 조절할 수 있는 조명으로 더 코지한 느낌을 낼 수 있어서 마음에 듭니다. 다른 조명들이 비해 한지 소재가 주는 따뜻하고 차분한 느낌이 마음에 듭니다.</pre>

#### Excel 행 1282

- origin: sampled_non_candidate / label: NORMAL / platform: ohouse / split: train

<pre>하늘색 색감이 너무 예뻐서 구매했는데 실제로 받아보니 사진보다 더 은은하고 예뻐서 마음에 들어요. 침대에 깔아두기만 해도 방 분위기가 화사하고 깔끔해지는 느낌이라 만족스럽습니다. 무엇보다 이불이 폭닥폭닥하고 포근해서 덮었을 때 기분이 좋아요. 너무 무겁게 눌리는 느낌 없이 적당히 포근해서 잠잘 때 편하고, 피부에 닿는 느낌도 부드러워서 자꾸 손이 가네요. 색상과 촉감 모두 만족스러워서 요즘 침대에 누워있는 시간이 더 좋아졌어요. 깔끔하면서도 포근한 분위기를 원하시는 분들에게 잘 어울릴 것 같아요.</pre>

#### Excel 행 984

- origin: sampled_non_candidate / label: NORMAL / platform: ohouse / split: train

<pre>그레이색은 길이조절 안되는건데 제가 키가 160이라그런지 불편하진 않아요. 머리카락같은건 아주 쉽게 모아지고, 아예먼지청소를 해야겠다싶으면 청소기쓰는게편하긴 합니다.</pre>

#### Excel 행 1927

- origin: sampled_non_candidate / label: NORMAL / platform: oliveyoung / split: validation

<pre>워낙 닥터포헤어의 두피 세정라인, 스크럽 라인을 다 사용하고 애정하는 사람입니다 그래서 이브랜드 세정라인은 나오때마다 사봐요</pre>

#### Excel 행 1101

- origin: sampled_non_candidate / label: NORMAL / platform: ohouse / split: train

<pre>어느 펜션놀러갓다가 거기잇는 센서휴지통이 너무 신기하고 편해서 서치하다가 구매햇습니다
가격도좋고 20리터 봉투 잘들어가구요
센서도 작동잘돼요! 남편이 자동닫힘인데 자꾸 손으로 닫아버려서 한소리햇어요...ㅋㅋㅋㅋ

여튼 인테리어를 해치지않는 예쁜아이입니다!</pre>

#### Excel 행 1992

- origin: sampled_non_candidate / label: NORMAL / platform: oliveyoung / split: train

<pre>용기가 너무 예뻐서 홀린듯 구매했는데
 탈모에도 좋다고 해서 기대중입니다
향은 시원한 쿨링향이 나고 두피에 자극 없어요
거품도 풍성해서 다른 라인도 구매해보려고 합니다^^ 꾸준히 사용해볼게요</pre>

#### Excel 행 1954

- origin: sampled_non_candidate / label: NORMAL / platform: oliveyoung / split: train

<pre>요즘 날씨때문인지 좀 가렵기도 하고 떡지는 느낌이라 샴푸를 새로 바꿔본거예요
거품도 풍성한 편이고
세정력도 좋은지 떡지지않고 개운하네요
꾸준히 써보면서 머리빠지는것도 봐야겠어요</pre>

#### Excel 행 1882

- origin: sampled_non_candidate / label: NORMAL / platform: oliveyoung / split: train

<pre>한번 샴푸 브러쉬 사용하고 나서부터는 안 사용하고 감을 수가 없더라구요. 진짜 두피까지 매번 스케일하는 기분이라 너무 잘 사용하고 있어요.</pre>

#### Excel 행 701

- origin: sampled_non_candidate / label: NORMAL / platform: ohouse / split: train

<pre>이제 없으면 안될정도로 너무 유용합니다! 청소기다 필요없을 정도내요 너무 가볍고 쉽게 교체되고 쉽개 버릴수있고 쉽게 끼울수있으니 너무 편리합니다!</pre>

#### Excel 행 1802

- origin: sampled_non_candidate / label: NORMAL / platform: oliveyoung / split: train

<pre>스케일러 브러쉬가 좋아보여서 구매했어요
브러쉬가 세밀한게 장점잋 수 있겠지만 갠적으론 조금 더 컸으면 해요 .</pre>

#### Excel 행 1855

- origin: sampled_non_candidate / label: NORMAL / platform: oliveyoung / split: test

<pre>비싸도 삼푸는 계속 이거 쓸 것 같아요. 
머리 빠짐이 전보디 덜해서 가르마 라인이 더 ㅅ깊어지고 그런게 없어요</pre>

#### Excel 행 905

- origin: sampled_non_candidate / label: NORMAL / platform: ohouse / split: train

<pre>모르고 단품만 삿는데 유용 하게 잘쓰고있어요담에 막대기랑 같이 또 주문예정입니다 화장실청소할내 넘 유용해서 필요하신분 고민하지마시고 바로 주문하세요 강추</pre>

#### Excel 행 1648

- origin: sampled_non_candidate / label: NORMAL / platform: oliveyoung / split: train

<pre>투슬래시포 제품력이 마음에 들어서 하나씩 사모으고 있는데 립펜슬도 인살몬 사고 마음에 들어서 아웃로지도 구매했어요.  색감이 너무 입술에서 둥 뜨지 않고 자연스러운데 얇게 발려서 밀착력도 좋아요. 위에 다른 립제품 올려도 뭉치거나 뜨지 않았어요!!</pre>

#### Excel 행 2048

- origin: sampled_non_candidate / label: NORMAL / platform: oliveyoung / split: test

<pre>너무 자극적이지도 않고 샴푸 후 쓰면 거품 잘나서 만족하고 잇어요</pre>

#### Excel 행 1056

- origin: sampled_non_candidate / label: NORMAL / platform: ohouse / split: train

<pre>기존 다이소에서 산 긴 돌돌이 써보니 허리 안 굽혀도 되고 편리해서 하나더 장만했어요. 기존에 쓰던 제품은 하단 고정받칟대가 없고 열고닫는 케이스 형태라 매번 열어서 꺼내기 힘들어 그냥 버렸는데, 이건 금방 끼워지고 세워두기 편해서 안 버리고 오래 잘 쓸 것 같습니다. 손잡이 대도 더 길고 튼튼한 느낌이에요!</pre>

#### Excel 행 889

- origin: sampled_non_candidate / label: NORMAL / platform: ohouse / split: test

<pre>인테리어 휴가를 체험 할 수 있습니다 디자인이 깔끔합니다 배송도 무척이나 빠르게 했습니다 택배 포장도 꼼꼼하게 해 주셔서 바로 사용할 수 있었습니다 감사</pre>

#### Excel 행 1501

- origin: sampled_non_candidate / label: NORMAL / platform: elevenst / split: validation

<pre>우선 배송 온 포장상태부터 맘에 들었습니다.  박스 손상도 없고 외부에 비닐로 이중 포장 되어서 좋았습니다. 구성품 알차게 동봉 되어왔고 작동 해 보니 이상도 없었습니다. 장점을 보자면 일단 가볍습니다. 하중심 방식에 셀프 스탠딩이 가능하다는것이 제일 큰 장점입니다. 애들도 사용하기 쉬운 무게입니다. 또한 녹색 조명이 있는 것도 먼지 탐색에 큰 도움이 되며 자동 먼지통 비움도 좋았습니다. 고장 없이 오래 사용하면 좋겠습니다~</pre>

#### Excel 행 1332

- origin: sampled_non_candidate / label: NORMAL / platform: ohouse / split: test

<pre>밝기 조절, 밝기 종류 있어서 좋아요
설치하는 것도 간편하고 높낮이 조절이 제일 맘에들어서 구매했는데 마음에 들어요!
다만 연결하는 어뎁터가 좀 뜨거워져서 살짝 불안합니다 고민 많이했는데 은은하고 거실 조명 드디어 생겨서 좋습니다</pre>

#### Excel 행 1107

- origin: sampled_non_candidate / label: NORMAL / platform: ohouse / split: train

<pre>두번째 구매합니다 ㅎㅎㅎㅎ 하나는 저희가 쓰고 하나는 장모님 것으로 선물했습니다 깔끔해서 만족합니다 20리터짜리로 적정하고 색깔도 화이트라 어느 인테리어든 잘 어울립니다</pre>

#### Excel 행 1865

- origin: sampled_non_candidate / label: NORMAL / platform: oliveyoung / split: test

<pre>닥터포헤어 씨솔트 엑스폴리에이터를 구매해봤습니다.
향이 진짜 좋아요, 약간 도손 느낌의 은은한 향이 계속나서 사용할때도 사용후에도 기분이 좋았습니다.
그리고 토출구가 얇아서 머리 사이사이에 도포하기 진짜 편했어요!
그리고 두피 기름기도 잘 잡아주고 깨끗하게 세정도 해주는데 헤어유막을 싹 제거해줘서 진짜 너무 만족했습니다.
항상 머리감고나면 뭔가 끈적하거나 미끌미끌하게 느껴지시는분들 이거 꼭 구매해서 사용해보세요! 일주일에 두번정도 사용하면 매일매일 뽀송한 두피를 유지할수 있어요!!
특히 두번 샴푸하시는분들 이거 머리속에 뿌린다음 슥슥문지르고 30초정도있다가 헹구고 샴푸하면 진짜 거품도 잘나고 머리가 뽀송해지니까 꼭사용해보세요!!</pre>

#### Excel 행 1964

- origin: sampled_non_candidate / label: NORMAL / platform: oliveyoung / split: train

<pre>지성 두피에 시원하게 세정되서 좋고, 매일 사용하기도 편해요.</pre>

#### Excel 행 1695

- origin: sampled_non_candidate / label: NORMAL / platform: oliveyoung / split: train

<pre>작고 가벼워요 ~ 색은 봄웜에게 잘어울리고 봄여름가을 다 잘어울릴것가타요 근데 손이안가여</pre>

#### Excel 행 1004

- origin: sampled_non_candidate / label: NORMAL / platform: ohouse / split: validation

<pre>화장실 바닥청소할때 쪼그리고 앉아 힘들었는데 서서 할수있어서 좋아요 헤드부분이 돌아가서 구석구석 잘 닦여요.. 화장실청소가 전보다 훨씬 편해졌어요</pre>

#### Excel 행 1957

- origin: sampled_non_candidate / label: NORMAL / platform: oliveyoung / split: validation

<pre>요즘 두피가 가려워서 샴푸를 바꿨어요.
몇번 문지르면 거품도 풍성하게 나고 샴푸후에 개운해서 좋네요</pre>

### human_candidate_review NORMAL — 20개

#### Excel 행 334

- origin: human_candidate_review / label: NORMAL / platform: oliveyoung / split: train

<pre>제품도 가격도 적합하고 잘 맞아서 자주 사용하고 있어요~^^</pre>

#### Excel 행 59

- origin: human_candidate_review / label: NORMAL / platform: ohouse / split: train

<pre>저희 남편 최애 밀대요. 가볍고 잘 눌린다면 항상 이것만 써요. 오래 썼는데도 튼튼하고 아주 좋아요. 진짜 실용적이에요. 다른 것도 써봤는데. 이것 만큼 가볍고 튼튼한 건 없는 거 같애요. 꼭 써보세요.</pre>

#### Excel 행 236

- origin: human_candidate_review / label: NORMAL / platform: ohouse / split: validation

<pre>너무 잘쓰고 있는 물건입니당
튼튼하구 예뻐요
가격대도 적당해서 추천드립니당
유명템은 유명한 이유가 있어요 
좋은 가격대 좋은 제품
많이 나왔으면 합니다
ㅎㅎ</pre>

#### Excel 행 34

- origin: human_candidate_review / label: NORMAL / platform: ohouse / split: train

<pre>저렴한데 색상이 저렴해보이지 않고 고급스러움! 솔도 생각보다 짱짱해서 잘 안 꺾이더라구요
 저렴한 솔들 한두번 쓰면 바로 망가지는데 얘넨 아직 꼿꼿해요.</pre>

#### Excel 행 325

- origin: human_candidate_review / label: NORMAL / platform: oliveyoung / split: train

<pre>아아....색예뻐요........상세사진보단 핑크에요......
주름에 다 껴요........두껍게 올리면 녹아내려요.......
입술색 진하고 입술주름  사람들은 사지마세오......
입술색 없고 주름 없는 사람은 꼭 사세요........</pre>

#### Excel 행 412

- origin: human_candidate_review / label: NORMAL / platform: oliveyoung / split: test

<pre>퓌라는 브랜드는 CS가 엉망인 수준을 넘어, 고객을 전혀 존중하지 않는 대응과 무책임한 안내의 연속이라 더 이상 신뢰하기가 참 쉽지 않네요;;</pre>

#### Excel 행 276

- origin: human_candidate_review / label: NORMAL / platform: ohouse / split: train

<pre>깔끔정리~~ 오래쓸것은 아니고
3~4년 쓰기에 적당 &amp; 정리에 도움</pre>

#### Excel 행 69

- origin: human_candidate_review / label: NORMAL / platform: ohouse / split: train

<pre>배송이 빨랐고 포장도 꼼꼼해서 만족했습니다. 제품을 직접 사용해 보니 기대했던 것보다 품질이 좋았고 가격 대비 만족도가 높아 재구매 의사가 있습니다. 
전반적으로 추천할 만한 제품입니다.</pre>

#### Excel 행 218

- origin: human_candidate_review / label: NORMAL / platform: ohouse / split: train

<pre>빅사이즈로 주문했는데 진짜 크고 튼튼해서 마음에 쏙 듭니다! 스틸 소재라서 그런지 흔들림 없이 아주 견고하네요. 분리수거함으로 쓸까 하다가 빨래바구니로 쓰고 있는데, 용량이 커서 빨랫감이 많이 들어가도 끄떡없어서 너무 편해요. 실버 색상도 깔끔하고 디자인이 심플해서 베란다나 다용도실에 두니 인테리어를 해치지 않아 좋습니다. 바퀴가 있어서 무거워도 이동하기 편하네요. 강추합니다!</pre>

#### Excel 행 324

- origin: human_candidate_review / label: NORMAL / platform: oliveyoung / split: train

<pre>이거 대체템이 없어요 너무 글로시하지 않으면서도 촉촉하면서도 유지력도 긴 립이예요!! 색깔 별로 쟁여둠...</pre>

#### Excel 행 219

- origin: human_candidate_review / label: NORMAL / platform: ohouse / split: train

<pre>철제 분리수거함 구매 후기입니당😉
화이트와우드 조합으로 깔끔해서 집 안 인테리어를 전혀 해치지 않아요. 철제라 오염되어도 쓱 닦아내면 되고 냄새도 안 배어 위생적입니다. 생각보다 튼튼하고 내부 봉투 걸이도 편리해서 분리수거 삶의 질이 확 올라갔네요. 진짜 강추합니다!</pre>

#### Excel 행 514

- origin: human_candidate_review / label: NORMAL / platform: oliveyoung / split: test

<pre>건성 쪽 + 민감성 두피인데 사용하고 나면 머릿결이 뻣뻣하고 다음날만 되면 가려워지고 비듬이 생깁니다 지성 두피는 잘 사용할 수 있을 것 같은데 저는 안 맞아요 제가 머리 감는 방식이 특이하지도 않아서 제품의 문제라고 여겨져요 두번 정도 테스트했습니다 딥클렌징 샴푸라 그런가봐요</pre>

#### Excel 행 407

- origin: human_candidate_review / label: NORMAL / platform: oliveyoung / split: test

<pre>진짜 광 너무너무너무 예쁘고 안뭉치고 고발색이고 쫀쫀한데 안끈덕이고 웨메 글로우립 라인중에 제일 만족스러움</pre>

#### Excel 행 471

- origin: human_candidate_review / label: NORMAL / platform: musinsa / split: train

<pre>가을이 다가와서 가죽자켓을 열심히 서치중이었습니다.
그러던찰나 판교 현대백화점에 팝업 매장으로 들어와있어서
블루종을 살짝 걸쳐보았는데, 어머나 왠걸 !
너무 가볍더라구요. 이거슨 가죽인가 리얼인가 할 정도로 부드럽구요. 신랑이랑 저희 아이도 너무 부드럽다고 놀랠정도였습니다. 그리고 저는 굉장히 오버핏으로 입는데 
이 제품은 사이즈가 프리인데도 제가 딱 원하는 오버핏이라 더더 마음에 들었습니다. 저는 여성스러운 가죽자켓은 선호하지않거든요. 보이쉬한 느낌을 좋아하거덩요. 
그런점에서 핏, 재질 , 소재 뭐 하나 빠지는 것이 없는 제품입니다. 평소에 스튜디* 톰보* 제품을 완전 사랑하는데
비슷한 느낌으로 너무 마음에 들어요. 
다른 색상도 구입하고 싶어요. 세일할 때 구입하고 어서 초가을부터 같이 입어요. 겟겟</pre>

#### Excel 행 148

- origin: human_candidate_review / label: NORMAL / platform: ohouse / split: test

<pre>기대했던 것보다 품질이 훨씬 좋네요. 사진이랑 똑같고 만족스럽습니다~</pre>

#### Excel 행 273

- origin: human_candidate_review / label: NORMAL / platform: ohouse / split: train

<pre>LED 전구까지 챙겨주셔서 좋았고, 아이보리 색상이 부드러운 분위기를 만들어줘요. 매력있고, 조립도 간편합니다!! 강추합니다!! 분위기 내기 좋아요</pre>

#### Excel 행 144

- origin: human_candidate_review / label: NORMAL / platform: ohouse / split: train

<pre>자취한다고 하니 여기저기서 추천해주어 구매했는데 진공청소기 부담되는 자츼생즐에게 정말정말 최고의 제품입니다 특히 머리 많이 빠지즌 분들은 꼭 사세요!!</pre>

#### Excel 행 254

- origin: human_candidate_review / label: NORMAL / platform: ohouse / split: test

<pre>처음엔 고민하다가 구매했는데 생각보다 만족스러워요! 😊배송도 무난하게 잘 왔고 전체적으로 가격 대비 괜찮은 것 같아요.
고민 중이신 분들은 참고하셔도 좋을 것 같아요! 재구매 의사 있습니다 🤍</pre>

#### Excel 행 554

- origin: human_candidate_review / label: NORMAL / platform: oliveyoung / split: train

<pre>요즘 미세먼지에 스타일링 제품까지 쓰다 보니 두피가 답답하고 간지럽더라구요. 그래서 올영에서 발견한 나인밀라 두피 스크럽을 바로 데려왔어요. 제형은 잔잔한 스크럽 알갱이가 들어있는데, 마사지하듯 문지르면 자극적이지 않게 노폐물이 싹 정리되는 느낌이에요. 사용하면서 두피가 시원~하게 쿨링돼서 스트레스까지 풀리는 기분!

세정 후에는 두피가 개운하게 숨 쉬는 느낌이 들고, 머리 뿌리 볼륨도 한결 살아나요. 게다가 맥주효모 성분 덕분인지 두피가 건조하지 않고 촉촉하게 마무리돼서 완전 만족했어요.

주 1~2회만 해줘도 확실히 차이가 느껴지니까 두피 고민 있는 분들, 특히 답답하고 기름진 두피로 스트레스 받는 분들께 강추합니다! 올영에서 만난 두피 케어 인생템 될 것 같아요🖤</pre>

#### Excel 행 271

- origin: human_candidate_review / label: NORMAL / platform: ohouse / split: train

<pre>진짜 너무 잘 쓰고 있어요ㅎㅎ 처음에는 인테리어용으로 예뻐서 샀는데 생각보다 실용적이고 분위기도 너무 좋아서 매일 켜놓고 있습니다! 이제는 이거 없으면 뭔가 허전할 정도예요ㅋㅋ 집 분위기 살리기에도 좋고 만족하면서 잘 쓰고 있어요!</pre>

### human SUSPICIOUS — 1개

#### Excel 행 504

- origin: human_suspicious / label: SUSPICIOUS / platform: oliveyoung / split: train

<pre>원오세븐 스칼프 퓨리파잉 마이크로바이옴 샴푸는 7년산 발효식초와 10년산 흑초에 발효시킨 인삼을 포함한 21종 이상의 핵심 성분이 어우러져 각종 두피 고민을 해결해 주는 두피 전문 샴푸입니다. 은은한 갈색빛의 촉촉한 젤 제형이 물기와 만나 풍성하고 부드러운 거품을 만들어내며, 온수로 모발과 두피를 충분히 적신 후 적당량을 골고루 도포해 마사지하고 깨끗이 헹궈내는 방식으로 손쉽게 사용할 수 있습니다. 꿉꿉하고 예민해진 두피를 마이크로바이옴 기술력으로 편안하고 개운하게 정화해 주어 매일 건강한 두피와 모발로 가꾸고 싶은 분들의 데일리 홈케어 제품으로 제격입니다.</pre>
