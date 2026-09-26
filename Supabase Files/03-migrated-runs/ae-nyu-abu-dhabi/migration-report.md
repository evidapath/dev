# NYU Abu Dhabi: V1.1 → V1.2 migration report

## ID stability

No canonical ID changed. No `v1.1-to-v1.2-id-remap.json` is produced.

## Structural fixes applied

NYUAD's V1.1 run contributed the largest single `Program.extension_metadata` block of any institution after TU Munich, covering university-wide holistic admission, major declaration, decision plans, and individualized financial aid. This migration promotes essentially all of it into first-class V1.2 entities:

1. **University-wide holistic admission → `AdmissionStage`** (`ae-nyu-abu-dhabi-stage-university-entry`, `stage_type: university_entry`, `program_ref: null`): resolves the structural gap that NYU's admission decision happens above the level of any specific program or campus. All four `AdmissionsRequirement` records now carry `admission_stage_ref` pointing here.
2. **Major declaration → `AdmissionStage`** (`ae-nyu-abu-dhabi-stage-major-declaration`, `stage_type: major_declaration`): the disputed timing conflict between two official NYU sources ("end of their second year" vs. "spring break of their second year") is preserved unchanged as a `CONFLICT` / `HUMAN_REVIEW` record — now attached to a structured `AdmissionStage` rather than living only in `Program.extension_metadata` free text.
3. **Early Decision I / II / Regular Decision → three `DecisionPlan` records**: exactly the structure this entity was designed to resolve (gm-05/gm-23). Deadlines, decision-release dates, and binding status are preserved unchanged from the V1.1 extension data.
4. **Test-optional policy → `Program.testing_policy`**: the policy-level fact ("test-optional through the 2027-2028 cycle") is now the canonical `testing_policy` field, while the per-curriculum `AdmissionsRequirement.standardized_tests[]` arrays are left unchanged — the two are designed to coexist (policy-level vs. per-curriculum acceptance), per the schema design doc.
5. **Individualized need-based aid → two `FinancialAidPolicy` records** (gm-17/24): `ae-nyu-abu-dhabi-finaid-need-based` (the general CSS-Profile-based aid available to all non-Emirati applicants) and `ae-nyu-abu-dhabi-finaid-falcon-dirhams` (the UAE-national-specific Personal Support Award). **Neither has a numeric `award_amount` field** — this is a deliberate design constraint, not an oversight, matching the original run's own financial-aid semantic QA rule that explicitly guarded against fabricating or averaging an amount that does not exist as a single public fact. The one genuinely fixed award (Sheikh Mohamed bin Zayed Scholarship, 100% tuition+fees+travel for a defined population) remains a `Scholarship` record, unchanged.
6. **`need_aware_or_blind: "unknown"`** on both `FinancialAidPolicy` records: preserves the original run's independent-verification finding that "need-aware" was the first-pass extraction tool's own characterization, not an exact NYU quote, and was therefore never promoted past `UNKNOWN` — this financial-aid semantic QA discipline is carried forward unchanged, not silently dropped during migration.
7. **`Program.application_platform` / `application_requirements[]`**: populated from the holistic admissions process detail (Common Application, STARS, recommendation, essays, optional Candidate Weekend).
8. **`Program.extension_metadata` trimmed**: `application_structure`, `decision_plans`, `holistic_admissions_process`, `major_declaration_timing`, `major_entry_structure`, and `financial_aid_policy` are removed now that they are represented as first-class entities/fields. `required_secondary_credential` and `transfer_admission_status` are retained since they have no other canonical home.

## The BS/BSc degree_type question: confirmed not adopted

The original run flagged, as a minor observation, that V1.1's `degree_type` enum offers `BSc` but not the literal `BS` abbreviation NYU itself uses. The gap matrix (gm-25) evaluated this and explicitly **rejected** adding a "BS" enum value: `degree_type_local` already preserves NYU's exact wording ("Bachelor of Science (BS)") without enum bloat for what is fundamentally the same degree, differently abbreviated by region. This migration makes no change to `degree_type` — it remains `"BSc"`, as in V1.1.

## Unresolved items carried forward unchanged

- **`ae-nyu-abu-dhabi-stage-major-declaration`**: remains `CONFLICT` / `HUMAN_REVIEW` — the two-source deadline disagreement is not resolved by guessing.
- **`ae-sheikh-mohamed-bin-zayed-nyuad-scholarship`**: remains `SUPPORTED` / `HUMAN_REVIEW` — the eligible-parent wording conflict across NYUAD's own pages ("children of Emirati mothers" vs. "children of an Emirati mother or father") is preserved unchanged.
- **`need_aware_or_blind: "unknown"`** on both `FinancialAidPolicy` records, as above.

## Unmapped facts

None. Every V1.1 field, including every `extension_metadata` entry, is either preserved unchanged, relocated to a canonical field, or promoted to a new structured entity.

## Validation result

`records-v1.2.json` validates cleanly against `evidapath-schema-v1.2.json` (0 errors).

## VerificationRecord formalization

`verification-records-v1.2.json` in this folder carries forward the original V1.1 run's field-level `VerificationRecord`s, reformatted to the V1.2 schema: any record with the informal `absence_claim: true` flag had its `verification_status` promoted to the now-formal `VERIFIED_ABSENT` enum value; `material_extension_fact` is preserved as the now-formal schema field (unchanged in meaning); any NYUAD-run-specific informal semantic-QA flags (`financial_aid_semantic_reviewed`, `holistic_admissions_semantic_reviewed` -- not part of the V1.2 schema) were folded into `conflict_or_limitation_notes` as a bracketed annotation. This is a reformatting pass only -- no field-level claim was added, removed, or re-verified.
