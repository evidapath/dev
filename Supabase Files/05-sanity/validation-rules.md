# EvidaPath V1.2 Sanity validation rules

This documents the validation logic already wired into `document-types/*.js`
and `object-types/*.js` (as `Rule.required()`), plus cross-field and
process rules that Sanity's per-field validation cannot express on its own
and that must instead be enforced by GROQ-based custom validation, a
Studio plugin, or process discipline (as they already are enforced today
by `04-pipeline/validate_normalized_records_v1_2.py`,
`check_fields_supported_v1_2.py`, and `check_verification_coverage_v1_2.py`).

## Field-level: required fields

Every field listed as `required` in `02-schema-design/evidapath-schema-v1.2.json`
carries `validation: (Rule) => Rule.required()` in the generated schema
file, EXCEPT where the JSON Schema itself marks the field nullable
(`"type": ["string", "null"]`, e.g. `university.last_verified`,
`program.campus_ref`) -- a required-but-nullable field is intentionally
left without a Sanity "must have a value" rule, since `null` is itself a
valid, meaningful value (unresearched vs. researched-and-absent are
different facts, never conflated -- see `evidapath-schema-v1.2.md`).

## Field-level: enums

Every `$ref` to an enum def (`degree_type`, `duration_unit`,
`record_status`, `verification_status`, `stage_type`, `pathway_type`,
`plan_type`, `requirement_type`, `policy_type`, `need_aware_or_blind`,
etc.) is wired as `options: { list: [...] }` with the exact enum values
from the JSON Schema, so Sanity Studio's editor restricts input to valid
values by construction -- the same discipline the JSON Schema enforces
programmatically.

## Field-level: the one non-native type (`selectionCriterion.weight`)

`SelectionCriterion.weight` is `string | number | null` in the JSON
Schema, because TU Munich's weighted selection criteria mix a percentage
(`"50%"`, kept as the exact stated string) and a raw point value (kept as
a number) depending on which stage of the Eignungsfeststellungsverfahren
is being described. Sanity has no native string-or-number union field
type, so `weight` is modeled as `type: 'string'` in
`object-types/selectionCriterion.js` and a numeric weight is stored as its
string representation (e.g. `"30"`) on import. This is a deliberate,
documented modeling compromise, not an oversight -- a Studio-side custom
input component could restore a numeric editing affordance later without
any schema or data change.

## Cross-field / cross-document rules (enforced by pipeline, not by Sanity field validation)

These rules cannot be expressed as a single field's `Rule.required()` /
`Rule.custom()` without a GROQ query against sibling documents, which
Sanity's field-level validation API does not support directly. They are
enforced today by the deterministic Python QA scripts in `04-pipeline/`
and should be re-run after every Sanity edit that changes a
material fact, not assumed to be enforced by Studio alone:

1. **Referential integrity** -- every `*_ref` (and every entry of
   `source_refs`) must resolve to an existing document of the correct
   type. Enforced by `validate_normalized_records_v1_2.py`'s
   `run_reference_integrity()` against the source JSON, and re-confirmed
   at the Sanity-document level by `import/resolve_references.py` (which
   exits non-zero on any unresolved reference rather than silently
   dropping it -- see the 4 known, disclosed exceptions in
   `import/import-readme.md`).

2. **No duplicate canonical IDs** -- enforced by
   `validate_normalized_records_v1_2.py`'s `check_duplicate_ids()`. Sanity
   itself will reject two documents sharing the same `_id`, which is a
   weaker but complementary guarantee once these are imported as
   `drafts.<type>-<canonical-id>`.

3. **`fields_supported` coverage** -- every `SourceRecord.fields_supported`
   entry must reference a real `EntityType.field` combination that exists
   in the schema. Enforced by `check_fields_supported_v1_2.py`.

4. **Verification coverage** -- every material field on a `VERIFIED` /
   `HUMAN_REVIEW` record should have a backing `VerificationRecord`; every
   `VERIFIED_ABSENT` claim must carry supporting notes; every fact still
   in `extension_metadata.fields` must have a `material_extension_fact`
   VerificationRecord; every new V1.2 entity type needs `source_refs` plus
   a resolved `verification_status`. Enforced by
   `check_verification_coverage_v1_2.py`. **As disclosed in
   `08-reporting/v1.2-freeze-report.md`, this check currently FAILs for
   all five institutions under this new, stricter, cross-institution bar**
   -- a real, honest finding (each institution's own original V1.1 QA
   script used a narrower, ad hoc field list), not a script defect, and
   not something this migration silently patched over.

5. **`record_status` lifecycle order** -- `RESEARCHED → STRUCTURED →
   VERIFIED → HUMAN_REVIEW → APPROVED → PUBLISHED`, never skipping
   `VERIFIED`, and `HUMAN_REVIEW → APPROVED` requires Suhail's explicit
   sign-off every time (per the pipeline skill's standing rule, unchanged
   in V1.2). No document in this test set has been promoted to
   `APPROVED` or `PUBLISHED` by this migration; the imported drafts carry
   forward whatever `record_status` they already had.

6. **No live Sanity write until explicit authorization** -- a process
   rule, not a schema rule: nothing in this package pushes to a live
   Sanity project. `import/five-school-sanity-drafts.resolved.ndjson` is
   ready for `sanity dataset import`, but that command has not been run
   against any real dataset as part of this synthesis.

## Recommended Studio-side additions (not built here -- design notes only)

- A `Rule.custom()` on each `*_ref` field that queries whether the
  referenced document exists could catch a dangling reference at
  authoring time inside Studio itself, closing the gap that today only
  the offline Python scripts catch. Not implemented in this package
  since it requires a live dataset to query against.
- A document-level "coverage badge" (computed field or Studio plugin)
  surfacing each record's own `check_verification_coverage_v1_2.py`
  result would make the disclosed coverage gaps visible to a human
  reviewer directly in the editing UI, rather than only in the offline
  JSON report.
