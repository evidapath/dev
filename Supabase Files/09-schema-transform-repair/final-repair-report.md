# EvidaPath V1.2 Sanity schema/transform repair — final report

**2026-09-24. QA repair pass on the existing V1.2 pipeline. No schema
redesign, no data change, no live Sanity write.**

## What this pass was

A field-by-field audit of the Sanity-facing side of the V1.2 pipeline —
the generated Sanity Studio schema (`05-sanity/{document,object}-types/*.js`)
and the transform that turns verified V1.2 records into Sanity NDJSON
(`04-pipeline/normalized_to_sanity_ndjson_v1_2.py` +
`05-sanity/import/resolve_references.py`) — against (a) the canonical
JSON Schema those files are supposed to mirror and (b) the real
399-document five-school draft set those scripts actually produced. This
was prompted by observed Studio symptoms (missing IDs, `[object Object]`
text, "Untitled" previews on `ApplicantCategory`/`ProgramPathway`) and
scoped from there into an exhaustive, programmatic check rather than a
symptom-by-symptom patch — every document type and every field was
checked, not just the ones already known to be broken.

## What was found

Six bugs, all in the generator/transform layer, none in the JSON Schema or
the underlying source data:

1. **Every one of the 399 documents was missing its `id` field.** The
   transform built each document's Sanity `_id` from the canonical `id`
   and then discarded the original field, even though every Sanity
   document type also declares its own required `id` field, independent
   of `_id`.
2. **`extension_metadata.fields` rendered as `"[object Object]"` in
   Studio.** This field is a genuine free-form key/value map in the JSON
   Schema; the schema generator had no branch for that shape and defaulted
   it to a plain Sanity string field, while the transform kept copying the
   raw object into it.
3. **164 explicit `null`s, across 84 documents**, were copied straight
   into the Sanity documents instead of the key being omitted — harmless
   for a plain string field, but not a valid shape for Sanity's
   `reference`/`object`/`array` field types.
4. **87 embedded array-of-object items, across 7 field names, were
   missing Sanity's required `_type`/`_key`** (e.g. every
   `language_requirements` entry, every `mandatory_fees_breakdown` line
   item).
5. **One nested reference field was never resolved** —
   `Program.testing_policy.source_refs` — because the reference resolver
   only ever looked at a document's top-level keys, not fields nested
   inside embedded objects.
6. **10 of 19 document types (270 of 399 documents) had a preview that
   fell back to the bare `id` field** for both title and subtitle,
   instead of using an already-available, more meaningful canonical field
   — the direct cause of the reported "Untitled" previews on
   `ApplicantCategory`/`ProgramPathway` (compounded by bug #1: `id` wasn't
   even present to fall back to).

Full before/after counts, root-cause analysis, and the reasoning behind
each fix are in `schema-transform-alignment.md` in this same folder.

## What was fixed, and how

- **`05-sanity/generation/gen_schema_files.py`** — added a branch for
  free-form-object properties (emits `array of extensionMetadataFieldEntry`
  instead of a plain string), and a `PREVIEW_OVERRIDES` table that gives
  the 10 affected document types a `prepare()`-composed title/subtitle
  from existing canonical fields (never a new field), with `id` retained
  as a guaranteed-non-empty fallback.
- **`05-sanity/{document,object}-types/*.js`** — regenerated from the
  fixed generator. Diffed against the pre-repair versions: exactly the 10
  document-type files (preview blocks) and `extensionMetadata.js` (field
  type) changed, plus one new file, `extensionMetadataFieldEntry.js`.
  Syntax-checked all 31 generated files (`node --check`, 0 errors).
- **`04-pipeline/normalized_to_sanity_ndjson_v1_2.py`** — stopped
  stripping `id`; added a single recursive post-processing pass
  (`_fix_node`) applied to every document that (a) omits explicit `null`s
  at any depth, (b) converts `extension_metadata.fields` into the new
  deterministic entry array, and (c) tags every embedded object/array item
  with its Sanity `_type` and a content-derived, deterministic `_key`.
- **`05-sanity/import/resolve_references.py`** — `resolve_doc()` now
  recurses the entire document tree instead of only checking top-level
  keys, so a reference field nested inside an embedded object (like
  `testing_policy.source_refs`) is resolved the same as a top-level one.
- **`09-schema-transform-repair/validate_sanity_ndjson_v1_2.py`** (new) —
  an automated, standalone validator that checks the Sanity NDJSON
  *output* for this whole class of bug (missing `id`, nulls, missing
  `_type`/`_key`, duplicate `_key`, unresolved-looking references,
  raw-dict `extension_metadata.fields`). None of the pipeline's existing
  validators ever looked at the transform's output, only its
  JSON-Schema-level input — which is exactly why these six bugs shipped
  despite all five institutions passing every existing check the whole
  time. This closes that gap going forward.

## What was verified

- **Regenerated the combined NDJSON** (`normalized_to_sanity_ndjson_v1_2.py
  --combine-dir` over all five institutions' `records-v1.2.json` +
  `verification-records-v1.2.json`, then `resolve_references.py`) and
  confirmed, by direct programmatic scan of all 399 documents (not
  sampling):
  - 0 documents missing `id` (was 399)
  - 0 raw-dict `extension_metadata.fields` occurrences (was 50)
  - 0 explicit nulls anywhere in the tree (was 164, across 84 documents)
  - 0 embedded array-of-object items missing `_type`/`_key` (was 87)
  - 0 arrays with a duplicate `_key`
  - 0 unresolved references — `resolve_references.py` exits 0, "All
    references resolved cleanly" (including the previously-missed nested
    one)
  - 399 unique `_id`s, still 399 total documents (same count as before
    this pass — this repair changed document *shape*, not *content* or
    *count*)
- **Reproducibility**: ran the full transform twice against unchanged
  input; raw and resolved NDJSON were byte-identical both times
  (SHA-256 matched).
- **Existing source-data QA re-run, unchanged data**: re-ran
  `validate_normalized_records_v1_2.py`, `check_fields_supported_v1_2.py`,
  and `check_verification_coverage_v1_2.py` against all five
  institutions' `records-v1.2.json` post-repair — all five still PASS,
  identically to before this pass (exit code 0 on every check, every
  institution). This confirms the bugs were entirely in the transform
  layer and the JSON-Schema-level source data was never the problem.
- **New validator sanity-check**: ran the new
  `validate_sanity_ndjson_v1_2.py` against both the repaired file (PASS,
  0 errors) and the pre-repair file (correctly flagged all six bug
  classes, with counts matching the manual audit).

## What changed vs. what didn't

**Changed:** the shape of every Sanity document (added `id`; pruned
nulls; retyped `extension_metadata.fields`; tagged embedded
objects/array items; resolved one previously-missed reference) and the
Studio preview configuration for 10 document types. New import-file SHA-256
hashes:
- Raw: `616079ae2bddfd93b4a2a65d4440ad9fb82aab96efffd7f3e4de1a5d759e4857`
- Resolved (**the import file**): `185f5d9d47a6a4eca1afa3521b894605ac1090086327117b477191cd91e9a1b0`

**Unchanged:** the JSON Schema (`evidapath-schema-v1.2.json`), every
institution's `records-v1.2.json`/`verification-records-v1.2.json`, the
399-document count, all 399 canonical `id`s and Sanity `_id`s, the
`--replace`-by-stable-ID import command in `import-readme.md` (still
correct and still idempotent — the IDs didn't change, only what's inside
each document did), and every previously-VERIFIED fact.

## Standing constraints honored

- **No schema redesign.** The JSON Schema was read, never written to.
  Every fix is in the generator's *mapping* of existing JSON-Schema shapes
  to Sanity field types, or in the transform's *handling* of existing
  field values — no field was added, removed, or reinterpreted at the
  schema level.
- **No live Sanity write.** Every step was a local, offline, deterministic
  file transform (plus re-running the existing offline schema generator).
  No Sanity API call, CLI import, or publish action was performed.
- **Nothing published.** The output is a corrected import-ready file, not
  an imported dataset — importing it into `staging` remains a separate,
  explicit, human-run step (`import-readme.md`), and this pass changed
  none of that command's mechanics.

## What's next (not done, and why)

This package produces the corrected file; it does not import it. The next
step, when you're ready, is the same `npx sanity dataset import ... staging
--replace` command already documented in `05-sanity/import-final/
import-readme.md`, now pointed at the corrected
`five-school-sanity-drafts.resolved.ndjson` — no changes needed to that
command itself, since the 399 document IDs are unchanged and `--replace`
is already idempotent against them.
