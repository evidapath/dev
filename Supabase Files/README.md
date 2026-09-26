# EvidaPath V1.2 schema and Sanity implementation package

> **2026-09-24 amendment (two repair passes):** `05-sanity/contract/
> sanity-serialization-contract.md` is now the normative V1.2 → Sanity
> adapter contract, enforced by `09-schema-transform-repair/
> validate_sanity_ndjson_v1_2.py`. Pass 1
> (`09-schema-transform-repair/schema-transform-alignment.md`) fixed
> missing `id` on every document, `extension_metadata.fields` stringifying
> to `"[object Object]"`, explicit `null`s breaking reference fields,
> embedded objects/array items missing Sanity `_type`/`_key`, one
> unresolved nested reference, and 10 document types' previews falling
> back to a bare/absent `id`. Pass 2
> (`09-schema-transform-repair/contract-repair-final-report.md`) — run
> against a 48-document fixture first, then the full dataset — additionally
> fixed `extension_metadata` present-but-contentless still tripping
> `Rule.required()`, and `VerificationRecord`/`ChangeRecord`'s untyped
> "any value" fields defaulting to a plain string field (the same
> `[object Object]` risk, for a nested-object proposed value). Read pass
> 2's final report first if you're picking this package back up — it
> supersedes the file hashes quoted elsewhere below and in
> `05-sanity/import-final/`. No schema redesign, no data change, no live
> Sanity write in either pass.

Self-contained synthesis of five completed university research runs
(TU Delft, Oxford, Toronto, TU Munich, NYU Abu Dhabi) into EvidaPath
schema V1.2 -- the first implementation-ready schema version -- plus a
full Sanity Studio implementation package, batch-ingestion design, and
directory strategy. Built entirely from already-gathered research; no
sixth university was researched, no live Sanity project was built or
written to, and no batch ingestion began. See `08-reporting/
v1.2-freeze-report.md` for the full, itemized readiness checklist and
`manifest.json` for exact file counts and reproducibility hashes.

## How to read this package, in order

1. **`01-gap-analysis/`** -- the five-school gap matrix: every V1.2
   candidate concept, classified A/B/C/D/E, with the evidence and
   promotion-criterion justification behind each disposition.
2. **`02-schema-design/`** -- the V1.2 schema itself
   (`evidapath-schema-v1.2.json`, executable JSON Schema Draft 7),
   its full conceptual documentation (`evidapath-schema-v1.2.md`), the
   V1.1→V1.2 migration guide, and an entity-relationship overview.
3. **`03-migrated-runs/`** -- all five institutions' data migrated to
   V1.2 (`records-v1.2.json`, `verification-records-v1.2.json`), each
   with its own `migration-report.md` documenting every structural
   change and its evidentiary justification, plus each institution's
   `verification-coverage-v1.2.json` QA result.
4. **`04-pipeline/`** -- the four V1.2-generalized QA scripts
   (`validate_normalized_records_v1_2.py`,
   `check_fields_supported_v1_2.py`,
   `check_verification_coverage_v1_2.py`,
   `normalized_to_sanity_ndjson_v1_2.py`), each runnable standalone
   against any institution's `records-v1.2.json`.
5. **`05-sanity/`** -- the full Sanity Studio schema (19 document types,
   11 object types), the combined 342-document five-school draft NDJSON
   (raw and reference-resolved), and the content-model/validation-rules
   documentation. Nothing here has been imported into a live Sanity
   project.
6. **`06-batch-ingestion/`** -- design-only batch contract for a future
   10-20 university batch: naming convention, manifest shape, and
   aggregate QA rollup contract. No batch has been started.
7. **`07-directory-strategy/`** -- how geography and public "Collections"
   should be modeled going forward (as queryable data over existing
   documents, never duplicated folders or records).
8. **`08-reporting/`** -- `five-school-synthesis.md` (what changed
   because of each of the five universities, individually, with full
   evidentiary trace) and `v1.2-freeze-report.md` (the 14-point readiness
   checklist, including the honestly disclosed verification-coverage
   gaps and explicit GO/NO-GO recommendations).
9. **`05-sanity/contract/sanity-serialization-contract.md`** -- the
   normative V1.2 → Sanity adapter contract (11 rules), and
   **`09-schema-transform-repair/`** -- both repair passes:
   `schema-transform-alignment.md` + `final-repair-report.md` (pass 1),
   `contract-repair-final-report.md` (pass 2, the one to read first),
   `build_contract_fixture.py` (the 48-document scenario-complete fixture
   builder), `validate_sanity_ndjson_v1_2.py` (the automated contract
   validator), and `reference_root_cause_audit.py` (the A/B/C/D/E/F
   reference-redness audit).

## Standing constraints honored throughout this synthesis

- **No sixth university was researched.** Every fact in this package
  traces to the five institutions already researched before this
  synthesis began.
- **No live Sanity project was built, connected, or written to.** Every
  file in `05-sanity/` is local; `sanity dataset import` was never
  invoked against a real dataset.
- **No batch ingestion began.** `06-batch-ingestion/` is a design
  deliverable; its example manifest names no real institution.
- **This was a synthesis and migration pass, not new research.**
  Re-research was never performed to fill a gap; every fix in this
  package (schema field nullability, `fields_supported` normalization,
  a `FinancialRequirement.requirement_type` correction, two retired
  `DerivedCostEstimate` records, TU Munich's monthly-range propagation,
  two `entity-relationship-overview.md` corrections) is a migration or
  tooling fix against evidence already on file, never a new fact-finding
  pass.

## Reproducibility

Every generated artifact in this package -- the V1.2 schema, all five
migrations, all four QA script results, the Sanity Studio schema files,
and the combined Sanity draft NDJSON (both raw and reference-resolved) --
was produced by deterministic, offline scripts with no `datetime.now()`
dependency and no network calls. `manifest.json` records SHA-256 hashes
for the key reproducibility-critical files; regenerating any of them from
unchanged upstream input reproduces the same hash, as was directly
confirmed for the schema-generation and Sanity-NDJSON-generation scripts
during this synthesis (see `05-sanity/import/import-readme.md` for the
NDJSON hashes).
