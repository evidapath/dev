# TU Munich: V1.1 → V1.2 migration report

## ID stability

No canonical ID changed, with one exception noted below (a `CostProfile` retired in favor of a `FinancialRequirement` of a different ID under a different entity type — not a rename of the same entity). No `v1.1-to-v1.2-id-remap.json` is produced.

## Structural fixes applied

TU Munich's V1.1 run produced the single largest `extension_metadata` block of any of the five institutions (`qualification_recognition_framework`, `aptitude_assessment_eignungsfeststellungsverfahren`, `studienkolleg_pathway`, `application_route`, `curriculum_structure`), explicitly because V1.1 had no entity for a pre-admission qualification-recognition gate, a weighted multi-stage selection procedure, or a preparatory pathway. This migration promotes nearly all of it:

1. **`QualificationRecognitionPathway` → `AdmissionStage`** (`de-tu-munich-stage-qualification-recognition`, `stage_type: qualification_recognition`): the uni-assist VPD gate that determines whether a foreign credential grants direct, subject-restricted, or no admission eligibility.
2. **`SelectionProcedure`/`SelectionCriterion`/`SelectionStage` → `AdmissionStage`** (`de-tu-munich-stage-aptitude-assessment`, `stage_type: selection_stage`): TUM's two-stage, weighted-point Eignungsfeststellungsverfahren is now one `AdmissionStage` with four embedded `SelectionCriterion` entries (HZB average, subject grades, bonus points, Stage-2 test) — resolving the exact "how do we represent a multi-stage, weighted-point selection procedure without flattening it into unstructured text" gap the original run identified (gm-13).
3. **Studienkolleg → `AdmissionStage`** (`de-tu-munich-stage-studienkolleg`, `stage_type: preparatory_pathway`): modeled as an alternative branch (same `sequence_order` as the qualification-recognition stage, not a step after it), consistent with the actual decision logic (Studienkolleg is reached only when qualification recognition fails, not sequentially after the aptitude assessment).
4. **Application route → `Program.application_platform` / `application_requirements[]` / `DecisionPlan`**: TUMonline + uni-assist VPD platform detail is now `Program.application_platform`; document requirements are `Program.application_requirements[]`; the 15 May–15 July 2026 window is a new `DecisionPlan` record (`de-tu-munich-decisionplan-ws2026-27`). The Stage-2 test date (21 Aug 2026) is deliberately modeled inside the `AdmissionStage` record instead, since it is an evaluation step, not an application deadline.
5. **`duration_unit: "semesters"` now native (gm-18)**: V1.1 could only represent TUM's officially published "6 Semester" duration via a lossy conversion to `duration_value: 3.0, duration_unit: "years"`, capped at `SUPPORTED` rather than `VERIFIED` specifically because of that conversion. V1.2's `duration_unit` enum now includes `semesters`; this Program record is updated to `duration_value: 6, duration_unit: "semesters"` — TUM's own stated figure, verbatim, with no arithmetic conversion needed. `Program.extension_metadata.fields.duration_conversion_note` is removed since the underlying friction it documented no longer exists.
6. **Sperrkonto (blocked account) → `FinancialRequirement`** (gm-15/16): the V1.1 `de-tu-munich-cost-non-eu-immigration-liquidity` `CostProfile` record — which its own `extension_metadata` explicitly said existed "only because V1.1 could not represent this fact any other way" — is retired as a `CostProfile` and re-created as `de-tu-munich-finreq-blocked-account` (`requirement_type: blocked_account`). Amount (EUR 11,904), currency, sourcing, and verification status (`SUPPORTED`, `HUMAN_REVIEW`) are all preserved unchanged.
7. **Monthly living-cost range promoted**: both remaining `CostProfile` records (EU/EEA, non-EU) gained `estimated_living_costs_monthly_range: {min: 1300, max: 2000, currency: EUR}`, resolving the same range-vs-point-estimate friction Oxford also exposed.
8. **`Program.extension_metadata` trimmed**: `qualification_recognition_framework`, `aptitude_assessment_eignungsfeststellungsverfahren`, `studienkolleg_pathway`, `application_route`, and `proposed_v1_2_fields` are removed now that they are represented as first-class entities/fields. `curriculum_structure` (phase-1/phase-2 curriculum detail) is retained since it describes program content, not an admission or application concept, and has no other canonical home.

## Unresolved items carried forward unchanged

- **`de-tu-munich-admreq-us`** remains `SUPPORTED` / `HUMAN_REVIEW` — exact AP subject-count/score thresholds for direct entry were a genuine, disclosed gap in the original run, not re-researched here.
- **`de-tu-munich-cost-non-eu`** remains `UNKNOWN` / `HUMAN_REVIEW` for `tuition_annual` — the exact program-specific non-EU tuition tier (EUR 2,000 vs. 3,000/semester) was never confirmed despite five independent fetch attempts in the original run; both unconfirmed candidate figures are retained in `extension_metadata`.
- **`de-tu-munich-finreq-blocked-account`** remains `SUPPORTED` / `HUMAN_REVIEW` for the exact EUR 11,904 figure — the mechanism is officially confirmed but the number itself was only found on secondary/corroborating sources, exactly as in the original V1.1 record.

## Unmapped facts

None. Every V1.1 field, including every `extension_metadata` entry, is either preserved unchanged, relocated to a canonical field, or promoted to a new structured entity.

## Validation result

`records-v1.2.json` validates cleanly against `evidapath-schema-v1.2.json` (0 errors).

## VerificationRecord formalization

`verification-records-v1.2.json` in this folder carries forward the original V1.1 run's field-level `VerificationRecord`s, reformatted to the V1.2 schema: any record with the informal `absence_claim: true` flag had its `verification_status` promoted to the now-formal `VERIFIED_ABSENT` enum value; `material_extension_fact` is preserved as the now-formal schema field (unchanged in meaning); any NYUAD-run-specific informal semantic-QA flags (`financial_aid_semantic_reviewed`, `holistic_admissions_semantic_reviewed` -- not part of the V1.2 schema) were folded into `conflict_or_limitation_notes` as a bracketed annotation. This is a reformatting pass only -- no field-level claim was added, removed, or re-verified.
