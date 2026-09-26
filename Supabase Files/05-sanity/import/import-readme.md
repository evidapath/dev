# Importing the EvidaPath V1.2 five-school Sanity drafts

**No live Sanity project has been built or connected as part of this
synthesis. Nothing in this folder has been imported anywhere. This file
documents how to do it once Suhail explicitly authorizes that step**
(see `08-reporting/v1.2-freeze-report.md` for the GO/NO-GO recommendation).

## Files

| File | Documents | Purpose |
|---|---|---|
| `five-school-sanity-drafts.ndjson` | 342 | Raw draft NDJSON straight out of `04-pipeline/normalized_to_sanity_ndjson_v1_2.py`. `*_ref` fields are plain canonical-ID strings, matching `records-v1.2.json`. Kept for traceability/audit against the source data. |
| `five-school-sanity-drafts.resolved.ndjson` | 342 | The same documents with every `*_ref` field (and `source_refs` list entries, and the polymorphic `VerificationRecord`/`ChangeRecord` `record_ref`/`source_ref`) resolved into native Sanity `{_type:"reference", _ref:"drafts.<type>-<id>"}` objects, via `resolve_references.py`. **This is the file to hand to Sanity's import command.** |
| `resolve_references.py` | -- | The deterministic transform between the two. Pure Python, offline, no network calls, no Sanity token. |

## Document counts by type (both files, identical counts)

```
admissionStage: 10          derivedCostEstimate: 6
admissionsRequirement: 20   financialAidPolicy: 2
applicantCategory: 31       financialRequirement: 3
campus: 5                   program: 5
city: 6                     programPathway: 3
costProfile: 10             scholarship: 8
country: 5                  sourceRecord: 75
decisionPlan: 7             university: 5
                            verificationRecord: 141
```
`college` and `changeRecord`: 0 documents (by design -- see
`../sanity-content-model.md` and each institution's `migration-report.md`;
zero `ChangeRecord`s is expected since every one of the five runs in this
test set is a first pass, not a rerun).

## Reproducibility (already verified, re-verify after any regeneration)

Both the raw and resolved NDJSON were generated twice from unchanged
input and compared byte-for-byte:

```
$ sha256sum five-school-sanity-drafts.ndjson
e8d35caa228a1526bd5600783dbe7fa5264a326836537f316e44ffa154c59757

$ sha256sum five-school-sanity-drafts.resolved.ndjson
8e3be9b949631dba4f633333f80473f188aa940e8991172967434a24f35fbc6b
```
(These hashes reflect the institution-scoped `SourceRecord`/
`VerificationRecord` IDs described below -- an earlier build of this file,
before the clean-room test caught the ID-collision bug, hashed
differently and is not the one shipped in this package.)
Both `_evidapathMeta.generatedAt` timestamps are derived deterministically
from each institution's `run_id` (never `datetime.now()`), so regenerating
either file from the same `03-migrated-runs/*/records-v1.2.json` inputs
will reproduce these exact hashes. If you change any migrated record and
regenerate, the hash SHOULD change -- that is the point of pinning it here.

## Known limitation: 4 unresolved `record_ref` values

`resolve_references.py` exits with code 1 and a printed warning listing
exactly these 4 documents, because their `VerificationRecord.record_ref`
points at a `CostProfile` this migration retired in favor of a
`FinancialRequirement` record (see `../README.md` for the full
explanation and each institution's `migration-report.md`):

```
drafts.verificationRecord-gb-university-of-oxford-vr-12.record_ref -> drafts.costProfile-gb-university-of-oxford-cost-visa-maintenance-funds
drafts.verificationRecord-gb-university-of-oxford-vr-13.record_ref -> drafts.costProfile-gb-university-of-oxford-cost-visa-maintenance-funds
drafts.verificationRecord-de-tu-munich-vr-25.record_ref -> drafts.costProfile-de-tu-munich-cost-non-eu-immigration-liquidity
drafts.verificationRecord-de-tu-munich-vr-26.record_ref -> drafts.costProfile-de-tu-munich-cost-non-eu-immigration-liquidity
```

## Known (fixed) limitation: institution-scoped IDs

`SourceRecord` and `VerificationRecord` documents carry an institution-
slug-prefixed `_id` (e.g. `drafts.sourceRecord-nl-tu-delft-src-01`,
never bare `drafts.sourceRecord-src-01`), because their underlying
canonical `id` (`src-01`, `vr-01`, ...) is only unique within one
institution's own source files -- every institution numbers its own
sources and verification passes independently starting from `01`. This
was found by the 20-point clean-room test (a duplicate-`_id` check caught
186 unique `_id`s out of 342 documents in an earlier build) and fixed
before this package was delivered; re-verified at 342 documents / 342
unique `_id`s. See `../README.md` for the full explanation.

These 4 documents ARE included in `five-school-sanity-drafts.resolved.ndjson`
with `record_ref` left as the original plain string (not silently dropped,
not fabricated). A live Sanity import will still succeed for these 4
documents -- `record_ref` is just not a resolvable pointer for them yet.
Recommended follow-up, deferred rather than done in this migration (see
`../README.md`): re-point these 4 records at the superseding
`FinancialRequirement`, or mark them explicitly superseded, the next time
Oxford's or TU Munich's evidence is revisited.

## Step-by-step import (once authorized -- NOT run as part of this package)

1. `sanity init` a new Studio project (or open the existing one, once one
   exists) and copy `../document-types/`, `../object-types/`, and
   `../schema.js` into its `schemaTypes` folder, wiring `schema.js`'s
   `schemaTypes` export into `sanity.config.js`.
2. Deploy the schema (`sanity deploy` or `sanity dev` locally) so the
   dataset recognizes all 19 document types and 11 object types.
3. Dry-run the import against a throwaway/dev dataset first:
   `sanity dataset import five-school-sanity-drafts.resolved.ndjson <dev-dataset> --replace`
   (`--replace` is safe here only because every `_id` is `drafts.*` --
   never run against a dataset that already has non-draft documents at
   these IDs without reviewing collisions first).
4. Open Studio, spot-check a handful of documents per type against their
   source `records-v1.2.json` entry and against
   `03-migrated-runs/<institution>/migration-report.md`.
5. Only after review, and only with Suhail's explicit go-ahead, promote
   drafts to published documents and repeat against the real production
   dataset.

## What this import intentionally does NOT do

- It does not publish anything (`drafts.*` IDs only).
- It does not touch Supabase (the private per-student application
  database) or GoHighLevel (the CRM/marketing layer) -- both are outside
  this skill's and this migration's scope, per the pipeline skill's
  system-context boundary.
- It does not promote any `record_status` -- documents keep whatever
  status they already carried in `records-v1.2.json`.
- It does not begin the batch-ingestion of a sixth university or any
  further institution -- see `../../06-batch-ingestion/` for that design
  (not executed).
