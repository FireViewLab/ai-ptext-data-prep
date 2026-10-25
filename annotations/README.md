# Description candidate human annotation

`description_human_review_v1.csv` is the Git-trackable working file for manual
review of the immutable V2 candidate pool at
`outputs/description_human_review_pool_v2_20261021.csv`.

The annotation file lives under `annotations/` because generated files under
`outputs/` are ignored by Git. Do not edit, reorder, or reformat the preserved
candidate fields. In particular, keep `candidate_id`, `product_id`,
`review_id`, and `content` exactly as provided by the source pool.

Only these fields are intended for human input:

- `human_label`: blank, `SUSPICIOUS`, `NORMAL`, or `UNCERTAIN`
- `pattern_type`: blank, `PRODUCT_DESCRIPTION_REPLACEMENT`, `OTHER`, or `UNKNOWN`
- `review_note`: blank or a free-text reviewer note

The initial annotation file contains no labels. No model, LLM, or rule-based
labeling is part of this workflow.

Validate the untouched initial file:

```powershell
.\.venv\Scripts\python.exe scripts\prepare_description_human_review_annotations.py --require-blank
```

After manual labeling has begun, validate identities and allowed values without
requiring blank human fields:

```powershell
.\.venv\Scripts\python.exe scripts\prepare_description_human_review_annotations.py
```

The validator detects row-count changes, duplicate candidate IDs, duplicate
normalized content, source identity/content changes, column changes, and values
outside the documented label vocabularies.
