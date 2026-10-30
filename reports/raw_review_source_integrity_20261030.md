# Raw Review Source Integrity Verification

> 원본 CSV와 canonical SQLite를 read-only로 검증했습니다. 새로운 rule 탐지, candidate 생성, 모델 실행은 하지 않았습니다.

## Summary

- Accessible files: **6 / 6**
- CSV rows: **1,151,943**
- Expected/manifest rows: **1,151,943 / 1,151,943**
- Stored size+mtime signatures all match: **True**
- Analysis fields all match manifest: **True**
- Files unchanged during verification: **True**

## Platform results

| platform | rows | size | mtime ns | signature | identity/category/content | business identity unique |
| --- | ---: | ---: | ---: | --- | --- | --- |
| elevenst | 171,052 | 76,696,780 | 1792237496403481500 | True | True | True |
| kurly | 463,843 | 116,727,664 | 1792237448903184400 | True | True | True |
| musinsa | 118,192 | 40,936,691 | 1792238340568740200 | True | True | True |
| naver | 1,286 | 741,697 | 1792238354401047500 | True | True | True |
| ohouse | 6,828 | 3,771,221 | 1792238368216536400 | True | True | True |
| oliveyoung | 390,742 | 214,363,720 | 1792238383132055600 | True | True | True |

## Identity and content comparison

### elevenst

- header: `['platform', 'product_id', 'review_id', 'content', 'rating', 'written_at', 'option', 'image_count', 'helpful_count', 'product_name', 'product_category', 'first_collected_at']`
- encoding: `utf-8-sig compatible (strict UTF-8 decode passed)`; BOM=False
- mismatches: `{'missing_manifest_source_row': 0, 'platform_mismatch': 0, 'product_id_mismatch': 0, 'review_id_mismatch': 0, 'product_category_mismatch': 0, 'normalized_content_hash_mismatch': 0, 'content_length_mismatch': 0}`
- identity: `{'row_uid_unique_by_primary_key': True, 'business_identity_blank_rows': 0, 'business_identity_duplicate_groups': 0, 'business_identity_duplicate_extra_rows': 0, 'business_identity_unique': True}`

### kurly

- header: `['platform', 'product_id', 'review_id', 'content', 'rating', 'written_at', 'option', 'image_count', 'helpful_count', 'product_name', 'product_category', 'first_collected_at']`
- encoding: `utf-8-sig compatible (strict UTF-8 decode passed)`; BOM=False
- mismatches: `{'missing_manifest_source_row': 0, 'platform_mismatch': 0, 'product_id_mismatch': 0, 'review_id_mismatch': 0, 'product_category_mismatch': 0, 'normalized_content_hash_mismatch': 0, 'content_length_mismatch': 0}`
- identity: `{'row_uid_unique_by_primary_key': True, 'business_identity_blank_rows': 0, 'business_identity_duplicate_groups': 0, 'business_identity_duplicate_extra_rows': 0, 'business_identity_unique': True}`

### musinsa

- header: `['platform', 'product_id', 'review_id', 'content', 'rating', 'written_at', 'option', 'image_count', 'helpful_count', 'product_name', 'product_category', 'first_collected_at']`
- encoding: `utf-8-sig compatible (strict UTF-8 decode passed)`; BOM=False
- mismatches: `{'missing_manifest_source_row': 0, 'platform_mismatch': 0, 'product_id_mismatch': 0, 'review_id_mismatch': 0, 'product_category_mismatch': 0, 'normalized_content_hash_mismatch': 0, 'content_length_mismatch': 0}`
- identity: `{'row_uid_unique_by_primary_key': True, 'business_identity_blank_rows': 0, 'business_identity_duplicate_groups': 0, 'business_identity_duplicate_extra_rows': 0, 'business_identity_unique': True}`

### naver

- header: `['platform', 'product_id', 'review_id', 'content', 'rating', 'written_at', 'option', 'image_count', 'helpful_count', 'product_name', 'product_category', 'first_collected_at']`
- encoding: `utf-8-sig compatible (strict UTF-8 decode passed)`; BOM=False
- mismatches: `{'missing_manifest_source_row': 0, 'platform_mismatch': 0, 'product_id_mismatch': 0, 'review_id_mismatch': 0, 'product_category_mismatch': 0, 'normalized_content_hash_mismatch': 0, 'content_length_mismatch': 0}`
- identity: `{'row_uid_unique_by_primary_key': True, 'business_identity_blank_rows': 0, 'business_identity_duplicate_groups': 0, 'business_identity_duplicate_extra_rows': 0, 'business_identity_unique': True}`

### ohouse

- header: `['platform', 'product_id', 'review_id', 'content', 'rating', 'written_at', 'option', 'image_count', 'helpful_count', 'product_name', 'product_category', 'first_collected_at']`
- encoding: `utf-8-sig compatible (strict UTF-8 decode passed)`; BOM=False
- mismatches: `{'missing_manifest_source_row': 0, 'platform_mismatch': 0, 'product_id_mismatch': 0, 'review_id_mismatch': 0, 'product_category_mismatch': 0, 'normalized_content_hash_mismatch': 0, 'content_length_mismatch': 0}`
- identity: `{'row_uid_unique_by_primary_key': True, 'business_identity_blank_rows': 0, 'business_identity_duplicate_groups': 0, 'business_identity_duplicate_extra_rows': 0, 'business_identity_unique': True}`

### oliveyoung

- header: `['platform', 'product_id', 'review_id', 'content', 'rating', 'written_at', 'option', 'image_count', 'helpful_count', 'product_name', 'product_category', 'first_collected_at']`
- encoding: `utf-8-sig compatible (strict UTF-8 decode passed)`; BOM=False
- mismatches: `{'missing_manifest_source_row': 0, 'platform_mismatch': 0, 'product_id_mismatch': 0, 'review_id_mismatch': 0, 'product_category_mismatch': 0, 'normalized_content_hash_mismatch': 0, 'content_length_mismatch': 0}`
- identity: `{'row_uid_unique_by_primary_key': True, 'business_identity_blank_rows': 0, 'business_identity_duplicate_groups': 0, 'business_identity_duplicate_extra_rows': 0, 'business_identity_unique': True}`

## Modification conclusion

저장된 size/mtime signature와 전체 row identity, raw category, normalized content hash/length가 모두 일치한다. 따라서 기존 분석에 사용된 핵심 행과 본문은 동일하다고 강하게 확인된다. 다만 당시 raw-file SHA-256이 보존되지 않아 평점 등 manifest에 저장되지 않은 컬럼이나 CSV 직렬화까지 byte-for-byte 불변이었다고 확정할 수는 없다.

## Safety

- Source files were opened only for reading and size/mtime were identical before and after.
- Canonical SQLite was opened with `mode=ro`.
- Existing reports, annotations, manifest, and candidate outputs were not modified.
- No human label, candidate pool, inference, training, or rule expansion was created.
