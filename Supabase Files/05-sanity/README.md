# EvidaPath V1.2 Sanity implementation package

This folder is a complete, ready-to-wire Sanity Studio schema for EvidaPath
V1.2, plus one combined, deterministic NDJSON of draft documents for the
five test-set universities (TU Delft, Oxford, Toronto, TU Munich, NYU Abu
Dhabi). **Nothing here has been pushed to a live Sanity project.** No
Sanity API token was used to build this package; every file was produced
by local, offline Python/Node scripts reading the already-migrated
`03-migrated-runs/*/records-v1.2.json` files. Building a live Sanity
project, connecting it, and importing these drafts all remain gated on
Suhail's explicit go-ahead (see `08-reporting/v1.2-freeze-report.md`).

## What is in this folder

```
05-sanity/
  README.md                          -- this file
  sanity-content-model.md            -- document-type vs. embedded-object classification, with rationale
  validation-rules.md                -- required fields, enums, and cross-field rules to wire into Studio
  schema.js                          -- index that imports every type below for sanity.config.js
  document-types/                    -- 19 files, one per Sanity document type
  object-types/                      -- 11 files, one per embedded object type
  generation/
    gen_schema_files.py              -- the script that generated document-types/ and object-types/ from
                                         02-schema-design/evidapath-schema-v1.2.json (re-run it if the JSON
                                         Schema changes, rather than hand-editing the .js files out of sync)
  import/
    five-school-sanity-drafts.ndjson           -- 342 draft docs, *_ref fields as canonical-ID strings
    five-school-sanity-drafts.resolved.ndjson  -- the same 342 docs with *_ref fields resolved to native
                                                   Sanity {_type:"reference", _ref:"drafts.<type>-<id>"} objects
                                                   -- THIS is the file to hand to `sanity dataset import`
    resolve_references.py                       -- the deterministic transform between the two
    import-readme.md                            -- step-by-step import instructions and known caveats
```

## How the schema maps onto Sanity

Every one of the 19 top-level entity types in `evidapath-schema-v1.2.json`
(`$defs`) becomes a Sanity **document type**: it has a stable canonical ID,
is referenced from other records, and is expected to be queried, edited,
and reviewed on its own. Six more `$defs` entries (`selection_criterion`,
`application_requirement`, `testing_policy`, `accepted_assessment`,
`monthly_range`, `progression_requirement`, `living_cost_source_basis`,
`extension_metadata`, `line_item`, `test_requirement`,
`language_requirement` -- 11 in total) are Sanity **object types**: they
never appear as a standalone document, only nested inside the document
that owns them. `sanity-content-model.md` gives the full classification
rationale per type, reusing the same document-vs-object test from the
original pipeline skill (own stable ID + referenced by multiple records +
queried independently + own lifecycle/evidence + own public page →
document; else → object).

## Reference field convention

Every `*_ref` field in the source JSON (`records-v1.2.json`) is a plain
canonical-ID string (e.g. `"university_ref": "nl-tu-delft"`), because that
is what the JSON Schema in `02-schema-design/` validates against. The raw
Sanity draft NDJSON (`04-pipeline/normalized_to_sanity_ndjson_v1_2.py`'s
output) carries that convention through unchanged for traceability. The
Studio schema files in `document-types/`, however, declare these fields as
native Sanity `type: 'reference'` fields, because that is how a real
Sanity Studio should treat them (clickable, validated, queryable via
GROQ's `->`). `import/resolve_references.py` is the one deterministic,
documented step that bridges the two: it turns
`"university_ref": "nl-tu-delft"` into
`"university_ref": {"_type": "reference", "_ref": "drafts.university-nl-tu-delft"}`
for every simple ref field, every entry of `source_refs`, and the
polymorphic `record_ref`/`source_ref` fields on `VerificationRecord` and
`ChangeRecord` (which are stored as `"EntityType:canonical-id"` strings
and parsed accordingly). Run twice against the same input, it produces a
byte-identical output (SHA-256 confirmed in `import-readme.md`).

**Known limitation, disclosed rather than silently patched:** 4 of the
141 `VerificationRecord` documents in the combined NDJSON have a
`record_ref` that cannot be resolved, because it points at a `CostProfile`
record that this V1.2 migration deliberately retired (Oxford's
`gb-university-of-oxford-cost-visa-maintenance-funds` and TU Munich's
`de-tu-munich-cost-non-eu-immigration-liquidity`, both replaced by
`FinancialRequirement` records -- see each institution's
`migration-report.md`). These 4 VerificationRecords are historical V1.1
verification passes of a fact that has since been re-homed to a different
entity type; the underlying fact itself was never lost (it is fully
present on the corresponding `FinancialRequirement` record with its own,
resolvable evidence chain). `resolve_references.py` leaves these 4
`record_ref` values as plain strings rather than fabricating a resolution,
and exits non-zero so this is never silently missed. Recommended fix,
deferred rather than done here (would touch verification-record content,
outside this migration's scope): re-point these 4 VerificationRecords'
`record_ref` at the superseding `FinancialRequirement` record the next
time either institution's evidence is revisited, or retire the 4 VRs
themselves as superseded.

**Second known issue, found by the clean-room test and fixed before
delivery:** `SourceRecord` and `VerificationRecord` IDs (`src-01`,
`vr-01`, ...) are only locally unique within one institution's own
`records-v1.2.json` -- every institution's own V1.1-era run independently
numbered its sources and verification passes starting from `01`, unlike
`University`/`Program`/etc., whose IDs are country-prefixed and therefore
globally unique by construction. The first combined-NDJSON build
collapsed all five institutions' `src-01` (and `vr-01`, etc.) into a
single colliding Sanity `_id` -- caught by the 20-point clean-room test's
duplicate-`_id` check (342 documents, only 186 unique `_id`s) before this
package was ever delivered. Fixed in
`04-pipeline/normalized_to_sanity_ndjson_v1_2.py` by prefixing
`SourceRecord`/`VerificationRecord`/`ChangeRecord` `_id`s with their
institution slug (e.g. `drafts.sourceRecord-nl-tu-delft-src-01`), and in
`resolve_references.py` by reading each document's own
`_evidapathMeta.institutionSlug` to disambiguate which institution's
`SourceRecord` a bare `source_refs` entry refers to. Re-verified: 342
documents, 342 unique `_id`s.
