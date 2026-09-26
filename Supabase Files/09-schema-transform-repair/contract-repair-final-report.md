# EvidaPath V1.2 → Sanity contract repair — final report (second pass)

**2026-09-24. Sanity project `jxwrtsiz`, dataset `staging`. Local Studio:
`C:\Users\Suhail\OneDrive\EvidaPath\sanity-studio`. No new research. No
manual Sanity edits. No universities added. Nothing published or
imported.**

This is the second repair pass. The first pass (`schema-transform-
alignment.md`, `final-repair-report.md`, same folder) fixed the `id`-field
and array/reference-shape bugs. This pass responds to the standing
instruction to stop iterating record-by-record and instead prove and fix
the **adapter layer** — the canonical-to-Sanity transform and schema
generator — against a formal, written, automatically-enforced contract, and
to do that against a small fixture before touching the full dataset.

## 1. Systemic root causes found

Two, beyond what the first pass already fixed:

1. **`extension_metadata` present-but-empty still tripped
   `Rule.required()`.** JSON-Schema's `required: ["note", "fields"]` means
   "the key must exist" — it does not mean "the value must be non-empty."
   Sanity's `Rule.required()` means the stricter thing (empty string/array
   fails it). The generator conflated the two. 7 of the 50 populated
   `extension_metadata` blocks in the real dataset have blank `note` AND
   empty `fields` (nothing to say — a correct, meaningful value); another
   21 have a real `note` but an empty `fields` map. All 28 would show
   "required field" redness in Studio for information that was never
   actually missing.
2. **`VerificationRecord.proposed_value` / `ChangeRecord.{previous,
   proposed}_value` are genuinely untyped in the JSON Schema** (`{}` — "any
   value," because a verification/change record can check a proposed value
   for any canonical field, of any type). Confirmed by direct schema query:
   these are the *only* three such properties anywhere in the schema. Real
   data populates them with every JSON primitive shape. The generator
   defaulted this to a plain Sanity string field — the identical
   `"[object Object]"` risk the first pass fixed for
   `extension_metadata.fields`, but for a field that can hold a nested
   object or array too. Confirmed present in real data:
   `gb-university-of-oxford-vr-08/-11/-12` each check a
   `{min, max, currency}`-shaped proposed value.

## 2. Why each repeated Studio error occurred

- **`extensionMetadata` red validation / empty note-fields errors** — Root
  cause #1 above. Not a data problem: the values were correct, the Sanity
  field-generation rule enforcing them was too strict for what the JSON
  Schema actually promises.
- **`extensionMetadata.fields` rendering `[object Object]`** — the FIRST
  pass's root cause (free-form map copied straight into a Sanity string
  field); confirmed fixed and re-verified in this pass (0 raw-dict
  occurrences, 0 occurrences of the literal text anywhere in the 399-doc
  set).
- **Reference inputs outlined red despite Sanity displaying a correct
  target title/ID** — investigated directly (Step 4/item 4 below): this
  was not a reference-resolution bug at all. Every reference in the
  pre-repair file resolved correctly (0 missing targets then or now); the
  redness was Studio surfacing the TARGET document's own validation
  problems (overwhelmingly, the first pass's missing-`id` bug, which
  affected literally every document) through the reference field's UI.
  100% of the pre-repair file's 789 references pointed at a target that
  itself failed validation; 0% of the corrected file's 791 references do.
  This is not a guess — see the reference-audit results below.
- **Genuine `Verification Status = CONFLICT` / `Record Status =
  HUMAN_REVIEW`** — left untouched, as instructed. These are real research
  findings (e.g. `ae-nyu-abu-dhabi-stage-major-declaration`,
  `ae-sheikh-mohamed-bin-zayed-nyuad-scholarship` and its `vr-31`), not
  technical errors, and are not counted anywhere in this report's error
  totals.

## 3. Files changed this pass

| File | Change |
|---|---|
| `05-sanity/contract/sanity-serialization-contract.md` | **New.** The formal, normative contract (11 rules + disclosed known gaps). |
| `05-sanity/generation/gen_schema_files.py` | `NON_ENFORCED_REQUIRED` (drops `Rule.required()` from `extension_metadata.note`/`.fields` only); new branch for bare-`{}` ("any value") properties → `anyValueBox`; generates new `anyValueBox.js`. |
| `05-sanity/object-types/extensionMetadata.js` | Regenerated: `note`/`fields` no longer `Rule.required()`. |
| `05-sanity/object-types/anyValueBox.js` | **New** generated file. |
| `05-sanity/document-types/verificationRecord.js`, `changeRecord.js` | Regenerated: `proposed_value`/`previous_value` now `type: 'anyValueBox'`. |
| `05-sanity/schema.js` | Regenerated index: +1 object type. |
| `04-pipeline/normalized_to_sanity_ndjson_v1_2.py` | `_extension_metadata_is_empty()` + omission logic; `_wrap_any_value()` + `ANY_VALUE_FIELDS` handling (intercepts `proposed_value`/`previous_value` *before* the generic null-prune, since `null` is a meaningful verified-absence value there, not missing data). |
| `09-schema-transform-repair/build_contract_fixture.py` | **New.** Seed-set + reference-closure fixture builder. |
| `09-schema-transform-repair/validate_sanity_ndjson_v1_2.py` | Rewritten/extended: schema-vocabulary checks (unexpected field, enum mismatch), reference-wrong-type check, structural (not name-list-based) object-coercion-risk check, extension_metadata-contentless check. |
| `09-schema-transform-repair/reference_root_cause_audit.py` | **New.** A/B/C/E categorized reference audit (D is explicitly flagged as not statically testable). |
| `05-sanity/import-final/five-school-sanity-drafts{,.resolved}.ndjson` | Regenerated — **the resolved file is the corrected import file.** |
| `05-sanity/import-final/import-manifest.json`, `qa-summary.md`, `import-readme.md` | Amended with this pass's hashes and findings. |

## 4. Fixture test results

`09-schema-transform-repair/fixture/` — **48 documents**, built from real
five-school records only (`ae-nyu-abu-dhabi` + `gb-university-of-oxford`),
selected as a deliberate seed set then closed under full
reference-dependency BFS so every reference inside the fixture resolves to
another document also inside it, exactly like the real dataset. (Note: the
brief asked for "approximately 15–30"; the true self-contained closure of a
seed set covering all 14 required document types plus every listed
scenario came to 48, mostly `SourceRecord`s pulled in transitively — every
real record cites 1–4 sources, and 9 seed records across 2 institutions
add up. Trimming further would have meant dropping either a required type
or the closure property the exercise depends on, so the count was left
honest rather than forced down artificially.)

Scenario coverage (every one of the brief's required scenarios, by real
document): normal scalars (every doc) · optional missing values (`College`
absent, `academic_threshold: null` pre-omission) · arrays of strings
(`required_subjects: []`, `testing_policy.source_refs`) · arrays of
embedded objects (`application_requirements`, `criteria`,
`language_requirements`, `accepted_assessments`) · arrays of references
(`source_refs`) · nested objects (`Program.testing_policy`, itself
containing a nested array) · `extension_metadata` with content
(`admreq-a-level`, `Program`, `gb-…-finreq-visa-maintenance` — the last
with BOTH a string value and a nested-object value in the same `fields`
map) · `extension_metadata` with no content (`Country: ae`) · a VERIFIED
record (`vr-30`, `ae-nyu-abu-dhabi-stage-university-entry`) ·
HUMAN_REVIEW/CONFLICT records (`ae-nyu-abu-dhabi-stage-major-declaration`,
`vr-12`, `vr-31`, `ae-sheikh-mohamed-bin-zayed-nyuad-scholarship`) ·
verified absence (`vr-20`, `vr-24`, `vr-34`, all `VERIFIED_ABSENT`) · range
values (`gb-university-of-oxford-cost-home.estimated_living_costs_
monthly_range`) · multiple/complex references (`Campus`→University/City/
Country; two `ApplicantCategory` dimensions; `AdmissionsRequirement`→
Program/ApplicantCategory/AdmissionStage/SourceRecords).

**Results:**
- Underlying fixture source (`records-v1.2.json`/`verification-records-
  v1.2.json` for both institutions) independently re-passed
  `validate_normalized_records_v1_2.py` and `check_fields_supported_
  v1_2.py` — PASS, both institutions.
- Transform + `resolve_references.py`: 48 documents, **0 unresolved
  references**.
- `validate_sanity_ndjson_v1_2.py --schema evidapath-schema-v1.2.json`:
  **48/48 documents, 0 errors.**
- Reproducibility: two independent runs, byte-identical raw and resolved
  output (SHA-256 matched both times).

## 5. Full five-school test results

Same unmodified pipeline scripts, applied to all five institutions'
existing `03-migrated-runs/*/records-v1.2.json` (`--combine-dir`):

| Metric | Result |
|---|---|
| Total documents | **399** (unchanged from before this pass — same content, corrected shape) |
| Technical validation errors | **0** |
| Unresolved references | **0** |
| Explicit unsupported nulls | **0** |
| Malformed embedded objects (missing `_type`/`_key`, duplicate `_key`) | **0** |
| Extension-metadata serialization errors (raw-dict, or present-but-contentless) | **0** |
| Reference audit: target missing / wrong type / malformed `_ref` / target itself invalid | **0 / 0 / 0 / 0** (791 references, all clean) |
| Unexpected top-level fields / enum mismatches (checked against the JSON Schema directly) | **0 / 0** |
| Genuine `HUMAN_REVIEW`/`CONFLICT` records (reported separately, not errors) | present and unchanged — e.g. `ae-nyu-abu-dhabi-stage-major-declaration` (CONFLICT), `ae-sheikh-mohamed-bin-zayed-nyuad-scholarship` (HUMAN_REVIEW/SUPPORTED) and its `vr-31` (CONFLICT), plus every other institution's previously-disclosed HUMAN_REVIEW record (see `qa-summary.md`'s "Remaining UNKNOWN/CONFLICT items") |
| Reproducibility | byte-identical raw and resolved output across two independent runs |

Existing JSON-Schema-level QA (unaffected by this pass, re-run to confirm):
`validate_normalized_records_v1_2.py`, `check_fields_supported_v1_2.py`,
`check_verification_coverage_v1_2.py` — all five institutions, all PASS,
identical to before.

## 6. Exact replacement-import command

Unchanged from `import-readme.md` — the 399 document IDs did not change,
only their internal shape, so the same idempotent `--replace`-by-stable-ID
command applies:

```
npx sanity dataset import "C:\Users\Suhail\OneDrive\EvidaPath\v1.2-package\05-sanity\import-final\five-school-sanity-drafts.resolved.ndjson" staging --replace
```

Run from `C:\Users\Suhail\OneDrive\EvidaPath\sanity-studio`. This also
requires the regenerated schema files
(`05-sanity/{document,object}-types/*.js`, `schema.js`) to be copied into
that Studio project — the corrected NDJSON alone does not update Studio's
own schema definitions (see "What's next," below).

## 7. Final SHA-256

- Raw (pre-resolution): `1095576859827510c5d7dd9c2b65ad8d0ce3413b8f3e3de28af693ac7bb931d9`
- **Resolved — this is the import file:** `6455d07ed30e9d60e4e1ca1c5e87e71fbec4dcd52898c6a5f487e0c917007772`

## 8. Technical error count

**0**, across all 399 documents, checked by
`validate_sanity_ndjson_v1_2.py` against: missing `id`; explicit null in an
unsupported field; `"[object Object]"` coercion risk (checked structurally,
not by a hardcoded field-name list); reference target absent; reference
target wrong type; array-object item missing `_type`; array-object item
missing/duplicate `_key`; malformed `extension_metadata` (raw-dict, or
present-but-contentless); unexpected top-level field (checked against the
JSON Schema's own `$def`); enum mismatch (checked against the JSON
Schema's own `enum` list).

## 9. Genuine research conflict count

Not re-tallied in this pass (this was a transform/schema pass, not a
research pass, and no research record was touched) — see `qa-summary.md`'s
existing, unchanged "Remaining UNKNOWN/CONFLICT items" section for the full
list (TU Delft ×3, Oxford ×2, Toronto ×2, TU Munich: none remaining
blocking, NYU Abu Dhabi ×2 — 9 items total, each with its own documented,
good-faith verification attempt).

## 10. Confirmation nothing was published or imported

No Sanity API call, CLI import, or publish action was performed while
producing either this pass or the first one. No `sanity dataset import` or
`sanity documents create` command was run. Every step was a local, offline,
deterministic file transform (the pipeline scripts) or a deterministic
regeneration (the schema generator) against already-existing five-school
data — no network call, no new research, no manual Sanity edit, no
university added, no validation weakened to make a red indicator disappear
(every fix here narrows a real generator/transform mismatch and is
individually justified against real data counts, not a blanket relaxation
— see contract Rule 10's explicit framing of `NON_ENFORCED_REQUIRED` as a
narrow, named exception, not a general policy change).

## What's next (not done, and why)

1. **Copy the regenerated schema files into the live Studio.** This
   package produces corrected `.js` schema files
   (`05-sanity/{document,object}-types/*.js`, `05-sanity/schema.js`); this
   session has no access to `C:\Users\Suhail\OneDrive\EvidaPath\sanity-
   studio` and cannot copy them there directly. Until that copy happens,
   the live Studio's schema still enforces the OLD (over-strict / wrong-
   type) field rules, and re-importing the corrected NDJSON alone will not
   by itself clear Studio-side redness that depends on the schema change
   (specifically: `extension_metadata.note`/`.fields` no longer being
   `Rule.required()`, and `proposed_value`/`previous_value` being
   `anyValueBox` instead of `string`).
2. **A real Sanity schema compile/typecheck**, run inside the actual Studio
   project (`sanity schema validate`, or simply opening Studio locally)
   once the files above are copied in — this environment could only run
   `node --check` (ES-module syntax validity, confirmed 0 errors across
   all 33 generated files), which is not the same guarantee as Sanity's
   own schema compiler.
3. **The re-import itself** (item 6 above) — a separate, explicit, human-
   run step, same as every prior pass.

Waiting for approval before either of the above.
