---
name: structured-data-output-validation
description: Use when transforming input records or logs into CSV or JSON files with normalization, aggregation, and strict schemas.
---
- Translate the requested output schema into explicit assertions before writing files.
- Preserve money as `Decimal` during computation and serialize it as integer minor units when required.
- Normalize timestamps to UTC before filtering, grouping, sorting, or formatting.
- Normalize categorical values with a single canonicalization function.
- Deduplicate using the specified identity key and apply a documented deterministic retention rule.
- Count source rows and retained rows from the correct stages of the pipeline.
- Exclude unknown or sentinel values only where the specification directs.
- Emit every required metadata field with exact key names, types, and literal values.
- Sort records using the exact requested multi-key ordering after normalization.
- Re-read generated JSON and CSV, then validate headers, row shape, types, ordering, and schema fields programmatically.
