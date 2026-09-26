# Schema / transform / Sanity alignment audit — V1.2

Full field-by-field comparison of (a) the canonical `evidapath-schema-v1.2.json`
`$defs`, (b) the generated Sanity Studio schema
(`05-sanity/{document,object}-types/*.js`, produced by
`05-sanity/generation/gen_schema_files.py`), and (c) the actual NDJSON the
transform pipeline (`04-pipeline/normalized_to_sanity_ndjson_v1_2.py` +
`05-sanity/import/resolve_references.py`) produced from the real five-school
V1.2 data. This is a QA repair pass, not a re-design: the JSON Schema itself
was not touched, and no field was renamed, removed, or reinterpreted. Every
finding below is a bug in the *generator* or the *transform*, not in the
schema or the underlying data (all five institutions' `records-v1.2.json`
still independently PASS `validate_normalized_records_v1_2.py`,
`check_fields_supported_v1_2.py`, and `check_verification_coverage_v1_2.py`
unchanged, confirming this).

Method: every one of the 19 document `$defs` and 11 object `$defs` was
checked against its generated `.js` file field-by-field, and the real
399-document combined NDJSON was scanned programmatically (not sampled) for
every failure mode below, both before and after the fix.

## Summary table

| # | Issue | Layer | Docs/occurrences affected (before) | Occurrences after fix |
|---|---|---|---|---|
| 1 | `id` field stripped from every document | transform (`normalized_to_sanity_ndjson_v1_2.py`) | 399 / 399 (100%) | 0 |
| 2 | `extension_metadata.fields` typed as plain string; raw dict copied through | generator + transform | 50 occurrences across the dataset | 0 |
| 3 | Explicit `null` copied straight through | transform | 84 documents, 164 null occurrences | 0 |
| 4 | Embedded array-of-object items missing `_type`/`_key` | transform | 87 items across 7 field names | 0 |
| 5 | Nested `source_refs` (inside `testing_policy`) never resolved | `resolve_references.py` (top-level-only walk) | 1 occurrence (found by exhaustive scan, not sampling) | 0 |
| 6 | Preview shows raw `id` (or nothing, compounded by #1) instead of a real title | generator (`gen_document_type` preview heuristic) | 10 of 19 document types, 270 of 399 documents | 0 |

## 1. Missing `id` field — every document

**Root cause.** `to_sanity_doc()` built each document's Sanity `_id`
(`drafts.<type>-<id-prefix><rec_id>`) from the canonical `id`, then
explicitly discarded the original field (`if k == "id": continue`) on the
assumption that it was fully absorbed into `_id`. But every one of the 19
generated document types *also* declares its own required, independent
`id` string field — mirroring the JSON Schema's own
`"required": ["id", ...]` on every document `$def` — because `_id` is a
Sanity-internal identifier (drafts-prefixed, type-namespaced, sometimes
institution-disambiguated) and `id` is the canonical business key the rest
of the platform (Supabase, GoHighLevel, the pipeline's own change-detection
and verification records) actually keys off of. The two are not
interchangeable, and only one of them was ever being written.

**Effect.** All 399 documents were missing a field their own schema marks
`Rule.required()`. Combined with finding #6, this is also the direct cause
of the "Untitled" preview reports: `ApplicantCategory`/`ProgramPathway`'s
preview (`select: { title: 'id', subtitle: 'id' }`) had nothing to read.

**Fix.** `to_sanity_doc()` now copies every field from the source record,
`id` included — no special-case skip. Verified: 0 of 399 documents missing
`id` post-fix, and every `id` value matches its `_evidapathMeta.sourceRecordId`.

## 2. `extension_metadata.fields` type mismatch

**Root cause.** `$defs.extension_metadata.properties.fields` is
`{"type": "object"}` with **no** declared `properties` — a genuine
free-form, string-keyed map (see the schema's own description: "The ONLY
sanctioned place for a real, source-backed fact that does not yet map onto
a canonical field"). `gen_schema_files.py`'s `field_def()` had no branch for
a bare, propertyless `object` type; it fell through to the generic `else`
and emitted `type: 'string'`. The transform then copied the raw Python dict
straight into that field. Sanity has no native arbitrary-map field type, and
a JS object assigned where a string is expected stringifies to the literal
text `"[object Object]"` — the exact symptom reported.

**Why not just stringify it (e.g. `JSON.stringify`) into that string field?**
That would "fix" the crash but silently launder structured data into opaque
text with no schema-level guarantee of validity, and would still misdescribe
the field's type in Studio (a plain string input, not a queryable
key/value structure). Sanity has no native map type, so the deterministic,
schema-compatible representation is an **array of typed entries**, each
carrying the original key, a string-encoded value, and a tag for how to
decode it — nothing invented, nothing lossy, nothing dependent on a human
correctly guessing to re-parse a string field.

**Fix, two parts:**
- **Generator**: `field_def()` now detects `type: "object"` with no
  `properties` and emits `type: 'array', of: [{ type:
  'extensionMetadataFieldEntry' }]`. `extensionMetadataFieldEntry` is a new
  object type (`key: string`, `value: text`, `value_type: 'string'|'json'`),
  generated by `gen_schema_files.py` alongside the schema-derived types
  (not itself derived from a `$def`, since the map's *entries* have no
  fixed shape by design — documented inline in both the generator and the
  generated file).
- **Transform**: `_transform_extension_fields()` converts each
  `{key: value}` pair into `{_type: 'extensionMetadataFieldEntry', _key:
  key, key, value, value_type}`. When the original value is already a
  string, `value` is that string verbatim and `value_type` is `"string"`
  (the common case — 21 of 22 populated `fields` maps in this dataset are
  flat string values, e.g.
  `gb-university-of-oxford-finreq-visa-maintenance.fields.oxford_region_classification`).
  When it's a nested object/array/number (2 real cases in this dataset:
  `de-tu-munich-informatics.fields.curriculum_structure`, a nested object,
  and `de-tu-munich-cost-non-eu.fields.unconfirmed_candidate_figures`, an
  array of strings), `value` is that value's canonical
  (`sort_keys=True`) JSON serialization and `value_type` is `"json"` — a
  reader can always recover the exact original structure with
  `JSON.parse`, and determinism is preserved (the same input always
  produces the same string). `_key` uses the map key itself (already
  unique within one `fields` map by construction), not a hash — more
  meaningful than an opaque digest, and still fully deterministic.

**Verified:** 0 of 399 documents still have a raw-dict `fields` value; the
50 real key/value pairs in the dataset (across 22 populated
`extension_metadata` blocks) all round-trip through the entry shape with
zero data loss (spot-checked the 2 nested-value cases by hand;
`json.dumps(v, sort_keys=True)` for both reproduces the original structure
exactly on `json.loads`).

## 3. Explicit `null` copied straight through

**Root cause.** This schema's own core convention (see the pipeline skill:
"Missing = `value: null`, `verification_status: 'unknown'`") is correct at
the JSON-Schema level — never guess, always mark absence explicitly. But
the transform copied that `null` unchanged into the Sanity document. For a
plain string/number field this is mostly cosmetic (Studio shows it as
empty), but two shapes make it a real problem: (a) a `reference`-typed
field set to literal `null` is not a valid Sanity reference — Sanity
expects either a `{_type: "reference", _ref: ...}` object or the *key to be
absent* — and (b) `object`/`array`-typed fields set to `null` (e.g.
`CostProfile.living_cost_source_basis: null` when no living-cost figure was
found) can leave Studio's nested editor in a broken or blank state instead
of just "not filled in yet". 84 of the 399 documents (164 total null
occurrences, at every depth from top-level fields like `college_ref` and
`living_cost_source_basis` down to nested ones like
`proposed_value[0].min_score` inside a `VerificationRecord`) carried at
least one explicit `null`.

**Fix.** `_fix_node()` recursively omits any key whose value is `null`, at
every nesting level, in the final assembled document — never touching
`[]`/`""`, which this schema deliberately distinguishes from `null` (e.g.
`required_subjects: []` means "verified: no subjects required", a real
finding, not a gap). Omitting the key entirely preserves the exact same
"no value" meaning the source data intends, in the shape Sanity actually
expects.

**Verified:** 0 of 399 documents contain a literal `null` anywhere in the
resolved NDJSON (recursive scan, not sampled).

## 4. Embedded array-of-object items missing `_type`/`_key`

**Root cause.** Seven fields across five document types are JSON-Schema
arrays whose items are themselves objects (`application_requirements` →
`application_requirement`, `standardized_tests` → `test_requirement`,
`language_requirements` → `language_requirement`,
`mandatory_fees_breakdown`/`other_material_costs` → `line_item`,
`accepted_assessments` → `accepted_assessment`, `criteria` →
`selection_criterion`). The transform copied each item's plain JSON object
straight through with no annotation. Sanity requires every array item that
isn't a primitive to carry `_type` (so Studio/GROQ know which object schema
applies) and a unique `_key` (which Sanity's editor and array diffing use
as the item's identity — without it, reordering or editing one item in
Studio can corrupt or silently drop others). 87 such items across the
dataset had neither.

Two related, non-array cases were audited at the same time: five embedded
*single*-object fields (`testing_policy`, `living_cost_source_basis`,
`progression_requirement`, `estimated_living_costs_monthly_range`, and
`extension_metadata` itself) were likewise missing their own `_type` (not a
`_key` issue, since they're not array items, but the same "Studio/GROQ
can't tell which object schema this is" problem).

**Fix.** `_fix_node()` tags every occurrence of these field names,
regardless of nesting depth (so `Program.testing_policy.accepted_assessments`
is caught the same way as a top-level array), with the correct `_type`, and
for array items, a `_key` derived from a SHA-1 of the item's own
sorted-JSON content, truncated to 12 hex characters — deterministic (two
runs against the same input produce identical keys) and collision-safe
(the rare case of two structurally-identical items in the same array is
disambiguated with a `-1`, `-2`, … suffix; 0 collisions occurred in the
real dataset).

**Verified:** 0 of 399 documents have an array-of-object item missing
`_type` or `_key`, and 0 arrays contain a duplicate `_key`.

## 5. A nested reference field the resolver never reached

**Root cause.** `resolve_references.py`'s `resolve_doc()` only inspected
`doc`'s own top-level keys against its three reference-field lookup tables.
`Program.testing_policy.source_refs` is nested one level down inside the
embedded `testing_policy` object — and it is typed identically to every
other `source_refs` field in the schema (`array of reference` to
`SourceRecord`, generated by the same `LIST_REF_FIELDS` logic
`gen_schema_files.py` already applies regardless of nesting). Because the
resolver never looked inside nested objects, this one field (found on
`drafts.program-ae-nyu-abu-dhabi-computer-science-bs`, the only `Program`
record with a non-null `testing_policy` in this five-school dataset) was
left as two bare canonical-ID strings (`["src-01", "src-02"]") — a genuine
schema/data shape mismatch against a Sanity field the Studio schema types
as references.

**Why this one is easy to miss and important to state precisely:** it is a
single field on a single document in the current dataset, not a systemic
failure — but the *mechanism* that produced it (top-level-only traversal)
would silently fail identically for any future nested reference field, so
this is fixed structurally, not by special-casing `testing_policy`.

**Fix.** `resolve_doc()` now calls a recursive `resolve_node()` that walks
every dict/list in the document tree and applies the same three lookup
tables (`SIMPLE_REF_FIELDS`, `LIST_REF_FIELDS`, `POLYMORPHIC_REF_FIELDS`)
at every level, not just the top.

**Verified:** `resolve_references.py` reports "All references resolved
cleanly — 0 unresolved" (exit 0) against the full 399-document set, and the
new validator's `find_unresolved_looking_refs()` check (which scans for any
remaining bare string under a known reference-field name, anywhere in the
tree) also finds zero.

## 6. Preview configuration — audited across all 19 document types

`gen_document_type()`'s preview-field heuristic checked only for
`canonical_name` → `program_name` → `name` → `title`, in that order, and
fell back to the bare `id` field (used as *both* title and subtitle) for
any type with none of those. Ten of the nineteen document types hit that
fallback:

| Document type | Docs in dataset | Field(s) actually available that the heuristic missed |
|---|---|---|
| `applicantCategory` | 31 | `label` (required), `dimension` (required) |
| `verificationRecord` | 187 | `field_checked` (required), `verification_status` (required) |
| `admissionsRequirement` | 20 | `curriculum_type` (required), `academic_year` (required) |
| `costProfile` | 10 | `currency`+`tuition_annual` (required), `academic_year` (required) |
| `decisionPlan` | 7 | `plan_type` (required), `academic_year` (required) |
| `derivedCostEstimate` | 6 | `field_name` (required), `value` (required) |
| `financialRequirement` | 4 | `requirement_type` (required), `currency`+`amount` (required) |
| `programPathway` | 3 | `degree_type_local` (required), `pathway_type` (required) |
| `financialAidPolicy` | 2 | `policy_type` (required), `need_aware_or_blind` (required) |
| `changeRecord` | 0 (none in this dataset) | `field` (required), `resolution_status` (required) |

270 of the dataset's 399 documents (68%) are one of these ten types. Before
this pass, every one of them showed the bare `id` string as its Studio
title (before fix #1, they showed nothing at all — "Untitled" — since `id`
itself was absent).

**Why not just add `id` to the schema and stop there?** Fixing #1 alone
would make these show their raw canonical-ID slug (e.g.
`ae-nyu-abu-dhabi-curriculum-a-level`) as *both* title and subtitle —
technically not "Untitled" anymore, but still not a usable preview for
someone scanning a list of 187 `VerificationRecord`s in Studio.

**Fix.** Added a `PREVIEW_OVERRIDES` table to `gen_schema_files.py` for
these ten document `$defs`, each composing two already-required canonical
fields (never a new field) into a real title/subtitle via a Studio
`prepare()` function, with `id` kept as a guaranteed-non-empty fallback if
either chosen field is somehow empty. Example
(`applicantCategory`): title = `label`, subtitle = `dimension · id`. The
other nine document types (`country`, `city`, `university`, `campus`,
`college`, `program`, `admissionStage`, `scholarship`, `sourceRecord`) were
also individually checked against this same table and confirmed to already
resolve to a genuine name/title field — left unchanged.

**Verified:** regenerated all 19 document-type files and diffed; only the
ten listed above changed, each producing valid, parseable JS
(`node --check` on every generated file, ESM-renamed, 0 syntax errors).

## Files changed

| File | Change |
|---|---|
| `05-sanity/generation/gen_schema_files.py` | Free-form-object → array-of-entry-type branch in `field_def()`; `PREVIEW_OVERRIDES` table + `prepare()`-based preview generation; emits new `extensionMetadataFieldEntry.js` |
| `05-sanity/document-types/*.js` (10 files) | Regenerated: improved `preview` blocks |
| `05-sanity/object-types/extensionMetadata.js` | Regenerated: `fields` now `array of extensionMetadataFieldEntry` |
| `05-sanity/object-types/extensionMetadataFieldEntry.js` | New file |
| `05-sanity/schema.js` | Regenerated index: +1 object type |
| `04-pipeline/normalized_to_sanity_ndjson_v1_2.py` | `id` no longer stripped; new `_fix_node()`/`_transform_extension_fields()`/`_stable_key()` recursive post-processing applied to every document |
| `05-sanity/import/resolve_references.py` | `resolve_doc()` now recurses into the full document tree via `resolve_node()`, not just top-level keys |
| `05-sanity/import-final/five-school-sanity-drafts.ndjson` | Regenerated |
| `05-sanity/import-final/five-school-sanity-drafts.resolved.ndjson` | Regenerated — **this is the corrected import file** |
| `09-schema-transform-repair/validate_sanity_ndjson_v1_2.py` | New: automated regression validator for this whole class of bug (see below) |

The JSON Schema (`02-schema-design/evidapath-schema-v1.2.json`) and every
institution's `records-v1.2.json` / `verification-records-v1.2.json` are
**unchanged** — confirmed by re-running `validate_normalized_records_v1_2.py`,
`check_fields_supported_v1_2.py`, and `check_verification_coverage_v1_2.py`
against all five institutions post-repair: all still PASS, identically to
the pre-repair run.

## Reproducibility

`normalized_to_sanity_ndjson_v1_2.py --combine-dir` + `resolve_references.py`,
run twice against the unchanged source data, produced byte-identical output
both times (raw and resolved NDJSON SHA-256 matched across both runs) —
the `_key` content-hashing and the `fields` map's sorted-key iteration are
both fully deterministic, so this reproducibility guarantee (already a
project invariant) still holds after the repair.

## New regression protection

`09-schema-transform-repair/validate_sanity_ndjson_v1_2.py` codifies every
check performed by hand in this audit (missing `id`, explicit nulls,
un-annotated embedded objects, duplicate `_key`s, unresolved-looking
references, raw-dict `extension_metadata.fields`) into a standalone,
automated, offline validator that operates on the *Sanity NDJSON output*,
independent of and in addition to the existing validators that check the
JSON-Schema-level source data. It was verified to (a) PASS cleanly against
the repaired 399-document set and (b) correctly flag every one of the bugs
above when run against the pre-repair file (164 null occurrences, 50
raw-dict `fields`, etc. — see its own output). This closes the actual gap
that let five real bugs ship in the transform layer despite the source data
passing every existing check: none of the existing validators ever looked
at the transform's output, only its input.
