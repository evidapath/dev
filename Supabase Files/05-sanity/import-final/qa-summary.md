# QA summary — post verification-backlog-closure rerun

Full V1.2 QA suite rerun across all five institutions after (a) the earlier
reference-cleanup pass (4 `VerificationRecord.record_ref` fixes, unchanged
by this pass) and (b) a full closure pass on the verification-coverage
backlog that the freeze report previously disclosed as open gaps. This is
a rerun using the same scripts and pass bars as before; what changed is
the evidence, not the QA design.

## 1–4. `validate_normalized_records_v1_2.py` (parse, schema, duplicate-ID, referential-integrity)

| Institution | Result |
|---|---|
| TU Delft | PASS |
| Oxford | PASS |
| Toronto | PASS |
| TU Munich | PASS |
| NYU Abu Dhabi | PASS |

0 schema violations, 0 duplicate IDs, 0 broken references across all five `records-v1.2.json` files, including every new/edited record (Toronto's new `FinancialRequirement:ca-university-of-toronto-finreq-ircc-proof-of-funds`, TU Munich's resolved non-EU `CostProfile.tuition_annual`, Toronto's resolved domestic-other-province `CostProfile.tuition_annual`, and every filled-in `language_requirements`/`standardized_tests` array).

## 5. `check_fields_supported_v1_2.py`

| Institution | Result |
|---|---|
| TU Delft | PASS (10 SourceRecords) |
| Oxford | PASS (15 SourceRecords, +3 new) |
| Toronto | PASS (22 SourceRecords, +5 new) |
| TU Munich | PASS (22 SourceRecords, +2 new) |
| NYU Abu Dhabi | PASS (16 SourceRecords, no new sources needed) |

## 6–8. `check_verification_coverage_v1_2.py` (canonical-field / meaningful-absence / material-extension coverage)

| Institution | Canonical fields uncovered | `VERIFIED_ABSENT` uncovered | Material-extension facts uncovered | New-entity records uncovered | Result |
|---|---|---|---|---|---|
| TU Delft | 0 of 8 | 0 of 0 | 0 of 1 | 0 of 1 | **PASS** |
| Oxford | 0 of 33 | 0 of 0 | 0 of 5 | 0 of 4 | **PASS** |
| Toronto | 0 of 28 | 0 of 0 | 0 of 6 | 0 of 5 | **PASS** |
| TU Munich | 0 of 36 | 0 of 6 | 0 of 2 | 0 of 5 | **PASS** |
| NYU Abu Dhabi | 0 of 28 | 0 of 15 | 0 of 5 | 0 of 7 | **PASS** |

**All five institutions now PASS verification coverage**, closing the gap previously disclosed in `08-reporting/v1.2-freeze-report.md` point 7 (TU Delft 3/8, Oxford 10/33, Toronto 5/27, TU Munich 11/35, NYU Abu Dhabi 0/28 canonical fields, plus the material-extension and new-entity gaps). This was done by independently re-fetching and re-confirming primary sources for every previously-uncovered field, per-institution, following the project's source hierarchy (official pages first; government/immigration sources for visa-adjacent facts; no search snippets, aggregators, or commercial admissions sites treated as evidence). New VerificationRecords added: TU Delft +2 (vr-17–18), Oxford +15 (vr-36–50), Toronto +13 (vr-27–39), TU Munich +15 (vr-31–45), NYU Abu Dhabi +4 (vr-32–35) — 49 new VerificationRecords total, all schema-conformant (verified against `$defs/verification_record`'s `additionalProperties: false` constraint — an early draft from one research pass introduced a non-schema `absence_claim` field on 19 records across three institutions; found and stripped before this rerun, since V1.2 formally replaced that V1.1-era boolean with the `VERIFIED_ABSENT` + notes convention).

**Fields that could not be fully resolved remain honestly UNKNOWN or CONFLICT** rather than forced to a value — this is correct, not a defect (see "Remaining UNKNOWN/CONFLICT items" below). Coverage means every material field now has an independent verification receipt, not that every fact is fully known; a documented, evidence-backed UNKNOWN is itself "covered."

## 9. Confirm no references remain to the retired V1.1 CostProfile IDs

Unchanged from the prior cleanup pass: zero structural references remain to `CostProfile:de-tu-munich-cost-non-eu-immigration-liquidity` or `CostProfile:gb-university-of-oxford-cost-visa-maintenance-funds` outside the same three deliberate, disclosed prose-only mentions (FinancialRequirement provenance notes, the migration annotations themselves, one Oxford SourceRecord `fields_supported` parenthetical). `vr-12`/`vr-13` (Oxford) and `vr-25`/`vr-26` (TU Munich) were confirmed untouched by every research agent working on those institutions' other gaps.

## 10–16. Sanity draft regeneration and reference resolution

- Regenerated all five per-institution Sanity draft sets and the combined `five-school-sanity-drafts.ndjson` from the corrected, now-fully-verified input.
- **Combined draft count: 399 documents, 399 unique `_id`s** (up from 342 — the increase is entirely new/expanded `VerificationRecord` and `SourceRecord` documents, plus one new `FinancialRequirement` document at Toronto; no legacy document was removed or duplicated). Per-type breakdown: admissionStage 10, admissionsRequirement 20, applicantCategory 31, campus 5, city 6, costProfile 10, country 5, decisionPlan 7, derivedCostEstimate 6, financialAidPolicy 2, financialRequirement 4, program 5, programPathway 3, scholarship 8, sourceRecord 85, university 5, verificationRecord 187.
- Ran `resolve_references.py`: **0 unresolved references** — exit code 0, no warnings.
- Ran the full transform (`normalized_to_sanity_ndjson_v1_2.py --combine-dir` + `resolve_references.py`) **twice** against the same input and confirmed **byte-identical** output both times (raw and resolved).
- SHA-256 (raw, pre-resolution): `c9e14c43133c081b121778d0c13e29013e16e4d3d04ee4cc1d1166e0846ac75b`
- SHA-256 (resolved — **this is the import file**): `44f2437c8aeba1ad4a174ef2110b91bac40d216846e321b9c1e8aeb882f2f4f6`

(These hashes differ from the prior reference-cleanup-only package's `d18a2e98...`, as expected — the verification-coverage closure work is a substantial, real content change: 49 new VerificationRecords, 10 new SourceRecords, and several previously-empty/unresolved fields now filled with sourced values.)

**2026-09-24 amendment — schema/transform alignment repair.** The two
hashes above are now superseded. Six bugs were found and fixed in the
transform layer itself (not the data above): every document was missing
its `id` field; `extension_metadata.fields` stringified to
`"[object Object]"` in Studio; 164 explicit `null`s across 84 documents
broke reference-field shapes; 87 embedded array-of-object items were
missing Sanity `_type`/`_key`; one nested reference
(`Program.testing_policy.source_refs`) was never resolved because the
resolver only walked top-level document keys; and 10 of 19 document types'
Studio previews fell back to a bare/absent `id`. Full audit:
`../../09-schema-transform-repair/schema-transform-alignment.md`. Same 399
documents, same content, same 0-unresolved-references result — only the
Sanity-facing shape changed:
- SHA-256 (raw, pre-resolution, **post-repair**): `616079ae2bddfd93b4a2a65d4440ad9fb82aab96efffd7f3e4de1a5d759e4857`
- SHA-256 (resolved, **post-repair — this is now the import file**): `185f5d9d47a6a4eca1afa3521b894605ac1090086327117b477191cd91e9a1b0`

Reproducibility re-confirmed post-repair: two runs of the same transform
against the same (unchanged) input produced byte-identical raw and
resolved output. A new standalone validator
(`09-schema-transform-repair/validate_sanity_ndjson_v1_2.py`) now checks
the Sanity NDJSON output itself for this whole class of bug — PASS against
the repaired file, and confirmed to flag every bug above when run against
the pre-repair file.

## 12. All Sanity references resolve within the import set

Every reference in the 399-document set resolves to another document in the same set (fully self-contained, as before) — confirmed by `resolve_references.py` reporting 0 unresolved, including references from every newly-added VerificationRecord to its `source_refs` and `record_ref` targets.

## 17. No live Sanity write occurred

Every step in this verification-closure pass and QA rerun was a local, offline, deterministic transform plus WebSearch/WebFetch calls to public university/government pages for evidence-gathering — no Sanity API token was used, no network call was made to `api.sanity.io` or any Sanity endpoint, and no `sanity dataset import`/`sanity documents create` command was run. This package produces an import-ready file; it does not perform the import.

## Remaining UNKNOWN/CONFLICT items (genuinely unresolved, honestly disclosed)

These are not coverage gaps — each has an independent VerificationRecord documenting a real, good-faith verification attempt — they are facts that authoritative primary sources genuinely do not (yet) resolve. Per this project's rules, these stay UNKNOWN/CONFLICT rather than being forced to a guessed value:

- **TU Delft** — `vr-05` (AdmissionsRequirement academic_year: source page doesn't label a year, blocking); `vr-09` (A-Level language_requirements: exemption list names UK nationals specifically, non-UK A-Level holders' status genuinely unconfirmed, blocking); `vr-15` (Holland Scholarship TU Delft participation: government source omits TU Delft, TU Delft's own pages neither confirm nor deny — CONFLICT, blocking).
- **Oxford** — `vr-06` (AP/US academic_threshold: source page truncates before the US section on repeated fetch attempts, blocking); `vr-13` (visa-maintenance `oxford_region_classification`: gov.uk doesn't state which London/outside-London rate applies to Oxford, non_blocking).
- **Toronto** — `vr-24` (A-Level admreq required_subjects/academic_threshold/standardized_tests, blocking) and `vr-25` (US admreq same three fields, blocking) — both pre-existing UNKNOWNs, out of this pass's scope (which targeted language_requirements only, now filled and VERIFIED for both records).
- **TU Munich** — none remaining blocking; the one open item (non-EU tuition tier) was resolved this pass (see below).
- **NYU Abu Dhabi** — `vr-12` (Program major-declaration timing: two official NYU sources state different deadlines, CONFLICT, blocking); `vr-31` (Sheikh Mohamed bin Zayed Scholarship eligible_citizenships: official NYUAD sources internally disagree on "Emirati mother" vs. "Emirati mother or father," CONFLICT, blocking).

**Two long-standing ambiguities were actually resolved during this pass, not just re-documented:**
- **Toronto's domestic-other-province tuition figure** (`ca-university-of-toronto-cost-domestic-other-province.tuition_annual`) — previously three conflicting fetches of the same PDF. Resolved to **CAD 7,610/year**, cross-validated against the confirmed Ontario-rate ratio (1.2475, matching an independently-confirmed 1.2487 ratio elsewhere in the same fee schedule) and against which table row the other two candidate figures actually belonged to (a different program category, and the prior year's cohort). `vr-35`, promoted to VERIFIED.
- **TU Munich's non-EU tuition tier** (`de-tu-munich-cost-non-eu.tuition_annual`) — previously an unresolved 2,000-vs-3,000 EUR/semester bracket. Resolved to **EUR 6,000/year (3,000/semester)** via TUM's official fee statute (`Hochschulgebühren- und Entgeltsatzung`, 2024 amendment), independently re-fetched twice. `vr-42`, promoted to VERIFIED; `record_status` promoted HUMAN_REVIEW → VERIFIED.

Remaining `record_status: HUMAN_REVIEW` records (all allowed — factually unresolved, not uncovered): TU Delft's Holland Scholarship record (CONFLICT on participation); Oxford's AP/US admissions-requirement record (UNKNOWN on academic_threshold); Toronto's A-Level and US admissions-requirement records (UNKNOWN on subject/threshold/test fields — unrelated to this pass's language_requirements scope, which is now fully VERIFIED on both); TU Munich's US admissions-requirement record and blocked-account FinancialRequirement (both SUPPORTED, capped below VERIFIED by a secondary-source figure or an unpublished exact threshold, not by missing verification); NYU Abu Dhabi's Program record (major-declaration CONFLICT) and its Sheikh Mohamed bin Zayed Scholarship record (SUPPORTED).

## Net result

49 new VerificationRecords and 10 new SourceRecords were added across the five institutions, closing every previously-disclosed verification-coverage gap (freeze report point 7) while changing zero previously-VERIFIED facts without new evidence, and while resolving two long-standing genuine data ambiguities (Toronto's domestic-other-province tuition, TU Munich's non-EU tuition tier) with real primary-source evidence rather than guesswork. All five institutions now PASS the full QA suite outright — schema validation, fields_supported, and verification coverage — with no disclosed gaps remaining. The handful of fields that stay UNKNOWN or CONFLICT are genuinely unresolved in the source material itself, each with a documented, good-faith verification attempt; forcing them to a guessed value would have been the actual QA failure.

## 2026-09-24 amendment — formal contract repair, second pass

A formal, enforced V1.2 → Sanity serialization contract now exists:
`../contract/sanity-serialization-contract.md`. It was validated first
against a small (48-document), deliberately scenario-complete fixture
(`../../09-schema-transform-repair/fixture/`) built from real,
already-existing five-school records — no new research, no synthetic
data — before being applied to the full 399-document set, per the
"fixture first" requirement this pass was run under.

This pass found and fixed two systemic bugs beyond the first repair pass
(which fixed missing `id`, `extension_metadata.fields` stringifying to
`"[object Object]"`, un-pruned nulls, un-annotated embedded objects, and
one unresolved nested reference — see the first amendment above and
`../../09-schema-transform-repair/schema-transform-alignment.md`):

- **`extension_metadata` present-but-fully-empty still tripped
  `Rule.required()`** in Studio (empty `note`/`fields` are legitimate
  "nothing to say" values in this schema, not missing data — 28 of 50
  populated `extension_metadata` blocks in the real dataset are exactly
  this). Fixed: `note`/`fields` are no longer over-strictly required, and
  the whole block is omitted when genuinely contentless (contract Rule 10).
- **`VerificationRecord.proposed_value` / `ChangeRecord.{previous,proposed}
  _value`** (declared as untyped "any value" in the JSON Schema, since a
  verification/change record can check a proposed value of any type) were
  defaulting to a plain Sanity string field — the identical
  `"[object Object]"` risk as the first pass's `extension_metadata.fields`
  bug, for any proposed value that happens to be a nested object or array
  (confirmed present in real data: `gb-university-of-oxford-vr-08/-11/-12`
  check a `{min, max, currency}`-shaped proposed value). Fixed: wrapped in
  a new, deterministic `anyValueBox` type (contract Rule 9).

**Reference root-cause audit** (`../../09-schema-transform-repair/
reference_root_cause_audit.py`, all 791 references in the 399-document
set): 0 targets genuinely missing, 0 wrong-allowed-type, 0 malformed
`_ref`, 0 targets that themselves fail the contract validator. Run against
the ORIGINAL pre-repair file for comparison: 789 of 789 references (100%)
pointed at a target that itself failed validation (almost entirely the
missing-`id` bug, which affected every document) — directly confirming the
"a reference inherits its target's redness" theory, and confirming it was
never a 6th, separate root cause: it was a symptom of the same systemic
bugs, and disappeared entirely once those were fixed.

All 399 documents now pass the automated contract validator
(`validate_sanity_ndjson_v1_2.py --schema evidapath-schema-v1.2.json`) with
**0 errors** — including its schema-vocabulary checks (no unexpected
top-level field, no enum-value mismatch) which the earlier, narrower
validator did not have. Reproducibility re-confirmed: byte-identical raw
and resolved output across two runs.

- SHA-256 (raw, pre-resolution, **latest**): `1095576859827510c5d7dd9c2b65ad8d0ce3413b8f3e3de28af693ac7bb931d9`
- SHA-256 (resolved, **latest — this is now the import file**): `6455d07ed30e9d60e4e1ca1c5e87e71fbec4dcd52898c6a5f487e0c917007772`

Nothing was imported or published in producing this pass. See
`../../09-schema-transform-repair/final-repair-report.md` for the complete
account, including the fixture build methodology, the full contract text,
and the exact replacement-import command.
