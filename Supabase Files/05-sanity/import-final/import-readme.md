# Importing the EvidaPath V1.2 five-school Sanity drafts (final, verification-complete)

**Target: Sanity project `jxwrtsiz`, dataset `staging`, only.**
**This file describes how to import. It does not import anything itself, and no import has been run as part of producing this package.**

> **2026-09-24 amendment (contract repair, second pass):** the V1.2 →
> Sanity adapter now has a formal, enforced contract:
> `../contract/sanity-serialization-contract.md`, checked automatically by
> `../../09-schema-transform-repair/validate_sanity_ndjson_v1_2.py` against
> both Sanity's own structural requirements and the JSON Schema's field/enum
> vocabulary. This pass found and fixed two systemic bugs beyond the first
> repair pass: `extension_metadata` present-but-fully-empty was still
> tripping `Rule.required()` in Studio (now omitted when contentless, and
> `note`/`fields` are no longer over-strictly required — see the contract's
> Rule 10), and `VerificationRecord.proposed_value` /
> `ChangeRecord.{previous,proposed}_value` (declared "any value" in the
> JSON Schema) were defaulting to a plain Sanity string field, the same
> `"[object Object]"` risk as the first pass's `extension_metadata.fields`
> bug, for a nested-object or array proposed value (now a typed
> `anyValueBox`, contract Rule 9). All 399 documents pass the full contract
> validator with 0 errors — see
> `../../09-schema-transform-repair/final-repair-report.md`. The hash below
> is the **latest corrected** file.

## What to import

`five-school-sanity-drafts.resolved.ndjson` — 399 documents, SHA-256
`6455d07ed30e9d60e4e1ca1c5e87e71fbec4dcd52898c6a5f487e0c917007772`.
This is the only file you need to import; everything else in this folder
is documentation or an audit trail. Every document's `_id` is prefixed
`drafts.` — this file imports them as **drafts**, not published documents.

(This supersedes the earlier 342-document reference-cleanup-only package.
The increase to 399 documents is entirely new/expanded `VerificationRecord`
and `SourceRecord` documents plus one new `FinancialRequirement` record at
Toronto, produced by closing every verification-coverage gap the freeze
report previously disclosed — see `qa-summary.md`. No legacy document was
removed.)

## Prerequisites

1. You are signed in to the Sanity CLI as a user with write access to
   project `jxwrtsiz` (`npx sanity login`, if you haven't already — this
   opens a browser to authenticate; it does not touch any dataset).
2. You run every command below from inside your existing Studio folder:
   ```
   C:\Users\Suhail\OneDrive\EvidaPath\sanity-studio
   ```
   Running from here matters: `sanity.cli.ts` in that folder already
   pins `projectId: jxwrtsiz`, so the CLI knows which project to talk to
   without an extra flag. It does **not** pin a default dataset for the
   `dataset import` command — you always type the dataset name explicitly
   (see the Import Safety section below for why that matters).
3. Copy `five-school-sanity-drafts.resolved.ndjson` from this folder into
   (or reference it directly from) your Studio folder or anywhere
   convenient on disk — the import command takes a plain file path.

## The exact import command

From `C:\Users\Suhail\OneDrive\EvidaPath\sanity-studio`, in PowerShell or cmd:

```
npx sanity dataset import "C:\Users\Suhail\OneDrive\EvidaPath\v1.2-package\05-sanity\import-final\five-school-sanity-drafts.resolved.ndjson" staging --replace
```

(Adjust the input path if you copied the file elsewhere — the dataset
name `staging` and the `--replace` flag are what matter here.)

This command:
- **Imports into `staging`.** It never touches `production` — there is no
  `production` dataset name anywhere in this command.
- **Imports as drafts.** Every document's `_id` starts with `drafts.`,
  which the file already has — do not edit the NDJSON to strip that
  prefix. Sanity treats a `drafts.<id>` document as an unpublished draft;
  it will not appear as "published" content and will not affect any
  live/public-facing query that filters out drafts.
- **Does not publish anything.** There is no publish step in this
  command, and `sanity dataset import` never auto-publishes a
  `drafts.*`-prefixed document. Publishing is a separate, manual action
  you take later in Studio (or via a different command) — not part of
  this import, and not something this package asks you to do yet.

### Why `--replace`

`sanity dataset import` refuses to import a document whose `_id` already
exists in the target dataset, unless you tell it what to do about the
conflict:
- **`--replace`** (recommended here): overwrite the existing document if
  its `_id` already exists, otherwise create it. Because every one of
  these 399 IDs is a deterministic, institution-scoped ID this package
  generated (e.g. `drafts.university-nl-tu-delft`,
  `drafts.sourceRecord-de-tu-munich-src-01`), `--replace` can only ever
  touch these 399 specific documents — it cannot affect any unrelated
  content already in `staging`. This is also what makes a re-run
  **idempotent**: if you run the same command again later (after a
  network hiccup, or to pick up a future correction to this package),
  it cleanly overwrites the same 399 documents with the same content
  rather than failing with ID-conflict errors. If you previously
  imported the earlier 342-document package into `staging`, re-running
  this command with `--replace` cleanly upgrades those same documents in
  place and adds the new ones — nothing needs to be deleted first.
- **`--missing`** (more conservative alternative): only create documents
  that don't already exist; skip ones that do. Use this instead of
  `--replace` if you have since made manual edits to any of these 399
  documents inside Studio and want to keep your edits rather than have
  the re-import overwrite them.
- **No flag at all**: only safe for a genuinely first-ever import into an
  empty (or non-colliding) dataset. If any of these 399 IDs already
  exist, the command fails outright and lists the colliding IDs rather
  than guessing what you want.

### If the CLI warns about existing documents

If you run the command without `--replace`/`--missing` and see an error
listing colliding document IDs: this most likely means either (a) an
earlier import already ran, or (b) something else in `staging` happens to
use one of these exact IDs (very unlikely, since they're all
institution-scoped and namespaced with `drafts.<sanityType>-<canonical-id>`).
Before overwriting, spot-check a couple of the listed IDs in Studio to
confirm they are indeed these same EvidaPath records and not unrelated
content, then re-run the command with `--replace`.

## How to verify the import completed

The CLI prints a line like:
```
Import complete!
```
(or `Done! Imported N documents.` depending on CLI version) with no
error text above it. If the command exits with any error, none of your
existing `staging` content is affected — a failed import does not
partially corrupt the dataset in an unrecoverable way, but do re-read the
error before retrying rather than blindly re-running with `--replace`.

## How to count documents after import

The Studio already has the **Vision** plugin configured (`visionTool()`
in your `sanity.config.ts`) — this is the easiest way, no separate CLI
syntax to remember:

1. Run `npm run dev` (if it isn't already running) and open the Studio
   in your browser.
2. Click **Vision** in the top navigation.
3. Run this GROQ query:
   ```
   count(*[_id in path("drafts.**") && defined(_evidapathMeta)])
   ```
   Expect **399**.
4. To break it down by type:
   ```
   *[_id in path("drafts.**") && defined(_evidapathMeta)] {
     "type": _type
   } | group(type) { "type": type, "count": count(@) }
   ```
   (If your Sanity/GROQ version doesn't support `group()`, instead run
   one count query per type, e.g.
   `count(*[_type == "university" && _id in path("drafts.**")])`, and
   expect: university 5, program 5, admissionStage 10,
   admissionsRequirement 20, decisionPlan 7, costProfile 10,
   financialRequirement 4, scholarship 8, financialAidPolicy 2,
   programPathway 3, applicantCategory 31, campus 5, city 6, country 5,
   sourceRecord 85, derivedCostEstimate 6, verificationRecord 187,
   college 0, changeRecord 0.)

## How to inspect the five universities in Studio

1. In the Studio's default document list (left sidebar), open
   **University**. You should see exactly 5 entries, each marked as a
   draft (a dot/indicator next to the title, since none are published):
   TU Delft, University of Oxford, University of Toronto, Technical
   University of Munich, NYU Abu Dhabi.
2. Open each one. Its `country_ref`, `primary_city_ref`, and `source_refs`
   fields should render as clickable reference chips showing the
   referenced document's title — not a "Cannot resolve reference"
   warning.

## How to confirm references resolve

A resolved reference field in Sanity's default document editor renders
the target document's title/preview inline. A **broken** reference shows
an explicit error state (commonly a red/warning banner reading something
like "Broken reference" or a `?` placeholder instead of a title) — you
cannot miss it by scrolling past. For a more exhaustive check than
clicking through the UI, use Vision with a dereferencing query, for
example:
```
*[_type == "program"] {
  program_name,
  "university": university_ref->canonical_name,
  "campus": campus_ref->name
}
```
If every `university`/`campus` value shows a real name (not `null`), the
references resolve. This package's own `resolve_references.py` already
confirmed 0 unresolved references before this file was generated (see
`qa-summary.md`), so this is a confirmation step, not a step expected to
surface new problems.

## How to avoid importing into production by accident

- **Always type the dataset name explicitly and read it before pressing
  Enter.** The command above ends in ` staging` — never `production`.
  `sanity dataset import` has no implicit default dataset; it only does
  what the dataset argument you typed says.
- Run `npx sanity dataset list` first if you want to double-check which
  datasets exist on this project and confirm `staging` is a distinct
  dataset from any `production` dataset before you run the import.
- Do not copy this command into a different Studio folder or a different
  project's terminal session without re-checking that `sanity.cli.ts`
  there also points at `jxwrtsiz` — the dataset name alone doesn't
  protect you if you're accidentally targeting a different project.

## Import safety — summary

- **Use `staging` only. Do not use `production`.**
- **Do not publish** any of the imported documents as part of this step
  — this command only creates/updates drafts.
- **Do not remove the `drafts.` prefix** from any `_id`, before or after
  import — doing so would make Sanity treat the document as published.
- **Do not manually recreate the five universities (or any other
  record) in Studio's UI.** The import creates all 399 documents with
  their correct, deterministic IDs; a manually-created document would
  either collide with an import ID or create an untracked duplicate.
- **Do not create duplicate IDs.** Every ID in this file is
  institution-scoped and unique (see `import-manifest.json` and
  `qa-summary.md` point 16 — 399 documents, 399 unique `_id`s, confirmed
  before this file was written).

## Post-import verification checklist

Open each of the five universities in Studio and confirm the items below.
"Resolves" means the reference chip shows a real title, not a broken-
reference warning; a row with 0 expected records for that institution is
correct as-is and needs no chip (see the per-type counts in "How to count
documents after import" — not every type is populated for every school).

**1. TU Delft**
- [ ] University record exists
- [ ] Program reference resolves
- [ ] AdmissionStage records resolve (1 expected)
- [ ] AdmissionsRequirement records resolve (4 expected)
- [ ] DecisionPlan records resolve (1 expected)
- [ ] CostProfile records resolve (2 expected)
- [ ] FinancialRequirement records resolve (1 expected)
- [ ] Scholarship records resolve (2 expected) — the Holland Scholarship
      record's `record_status` is `HUMAN_REVIEW`: TU Delft's own
      participation in the scholarship is a genuine, disclosed CONFLICT
      (vr-15), not a data-quality issue in this import
- [ ] FinancialAidPolicy — not applicable (0 for this institution)
- [ ] ProgramPathway — not applicable (0 for this institution)
- [ ] SourceRecord references resolve (10 expected)
- [ ] VerificationRecord references resolve (18 expected, up from 16 —
      vr-17/vr-18 are new, closing the previously-disclosed coverage gap)

**2. University of Oxford**
- [ ] University record exists
- [ ] Program reference resolves
- [ ] AdmissionStage records resolve (1 expected)
- [ ] AdmissionsRequirement records resolve (4 expected) — spot-check that
      `language_requirements` is now populated (not empty) on the
      A-Level, IB, Advanced Highers, and AP/US records
- [ ] DecisionPlan records resolve (1 expected)
- [ ] CostProfile records resolve (2 expected)
- [ ] FinancialRequirement records resolve (1 expected) — **this is the
      record the vr-12/vr-13 fix points to; open it and confirm its own
      `source_refs` (src-07) resolves too**
- [ ] Scholarship records resolve (2 expected)
- [ ] FinancialAidPolicy — not applicable (0 for this institution)
- [ ] ProgramPathway records resolve (1 expected)
- [ ] SourceRecord references resolve (15 expected, up from 12 —
      src-13/14/15 are new)
- [ ] VerificationRecord references resolve (50 expected, up from 35 —
      vr-36 through vr-50 are new). Spot-check **vr-12** and **vr-13**
      specifically: their `record_ref` should still point to and resolve
      as the FinancialRequirement above, not to any CostProfile

**3. University of Toronto**
- [ ] University record exists
- [ ] Program reference resolves
- [ ] AdmissionStage records resolve (3 expected)
- [ ] AdmissionsRequirement records resolve (4 expected) — spot-check that
      `language_requirements` is now populated on the Ontario, A-Level,
      and US records (IB's was already populated, now has a filled-in
      `min_score` too)
- [ ] DecisionPlan records resolve (1 expected) — `application_deadline`
      should now show `2027-01-15` (was previously unresolved/UNKNOWN)
- [ ] CostProfile records resolve (3 expected) — the domestic-other-
      province record's `tuition_annual` should now show **7610**, not a
      null or one of the two previously-conflicting figures
- [ ] FinancialRequirement records resolve (1 expected, new — the IRCC
      study-permit proof-of-funds record added this pass; not present in
      the earlier 342-document package)
- [ ] Scholarship records resolve (2 expected)
- [ ] FinancialAidPolicy — not applicable (0 for this institution)
- [ ] ProgramPathway records resolve (2 expected)
- [ ] SourceRecord references resolve (22 expected, up from 17 —
      src-18 through src-22 are new)
- [ ] VerificationRecord references resolve (39 expected, up from 26 —
      vr-27 through vr-39 are new)

**4. Technical University of Munich**
- [ ] University record exists
- [ ] Program reference resolves
- [ ] AdmissionStage records resolve (3 expected)
- [ ] AdmissionsRequirement records resolve (4 expected) — spot-check that
      `language_requirements` is now populated on the Abitur, IB,
      A-Level, and US records (all four previously empty)
- [ ] DecisionPlan records resolve (1 expected)
- [ ] CostProfile records resolve (2 expected) — the non-EU record's
      `tuition_annual` should now show **6000.0** (EUR/year), not null
- [ ] FinancialRequirement records resolve (1 expected) — **this is the
      record the vr-25/vr-26 fix points to; open it and confirm its own
      `source_refs` (src-19, src-20) resolve too**
- [ ] Scholarship records resolve (1 expected)
- [ ] FinancialAidPolicy — not applicable (0 for this institution)
- [ ] ProgramPathway — not applicable (0 for this institution)
- [ ] SourceRecord references resolve (22 expected, up from 20 —
      src-21/22 are new)
- [ ] VerificationRecord references resolve (45 expected, up from 33 —
      vr-31 through vr-45 are new). Spot-check **vr-25** and **vr-26**
      specifically: their `record_ref` should still point to and resolve
      as the FinancialRequirement above, not to any CostProfile

**5. NYU Abu Dhabi**
- [ ] University record exists
- [ ] Program reference resolves
- [ ] AdmissionStage records resolve (2 expected)
- [ ] AdmissionsRequirement records resolve (4 expected)
- [ ] DecisionPlan records resolve (3 expected)
- [ ] CostProfile records resolve (1 expected)
- [ ] FinancialRequirement — not applicable (0 for this institution)
- [ ] Scholarship records resolve (1 expected)
- [ ] FinancialAidPolicy records resolve (2 expected)
- [ ] ProgramPathway — not applicable (0 for this institution)
- [ ] SourceRecord references resolve (16 expected, unchanged)
- [ ] VerificationRecord references resolve (35 expected, up from 31 —
      vr-32 through vr-35 are new)

If anything on this list fails to resolve, stop and do not publish or
build further on it — that would be a genuine regression from the 0
unresolved-references result this package's QA rerun confirmed
(`qa-summary.md`), and is worth reporting back rather than working around.
