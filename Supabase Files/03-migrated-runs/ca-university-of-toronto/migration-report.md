# Toronto: V1.1 → V1.2 migration report

## ID stability

No canonical ID changed. All V1.1 IDs are preserved unchanged. No `v1.1-to-v1.2-id-remap.json` is produced.

## Structural fixes applied (this is the most consequential migration of the five)

Toronto's V1.1 run was explicitly built around the finding that "V1.1's single-Program model cannot cleanly represent University of Toronto's actual admission structure" — captured entirely in `Program.extension_metadata` because no canonical entity existed. This migration promotes that entire finding into first-class V1.2 entities:

1. **CMP1 admission category → `AdmissionStage`** (`ca-university-of-toronto-stage-cmp1-entry`, `stage_type: admission_category`): Toronto's Year 1 Computer Science (CMP1) admission category — the actual entry point a Fall 2027 applicant applies to, structurally distinct from the `Program` record itself — is now a first-class stage. `program_ref` is `null` on this stage because CMP1 precedes any program-specific admission. All four `AdmissionsRequirement` records gained `admission_stage_ref` pointing here.
2. **Admission Guarantee → `AdmissionStage`** (`ca-university-of-toronto-stage-progression-guarantee`, `stage_type: progression`): the first-year continuation/guarantee criteria (course grades, credit totals, timing) are now structured `criteria[]` entries rather than a single free-text block.
3. **Out-of-stream competitive pathway → `AdmissionStage`** (`ca-university-of-toronto-stage-out-of-stream-competitive`, `stage_type: progression`): the competitive (non-guaranteed) route for non-CMP1 students into CS Major/Minor, previously only in `SourceRecord.excerpt` text (`src-02`), is now its own stage with structured criteria.
4. **Specialist/Major/Minor → `ProgramPathway`**: the base `Program` record (`ca-university-of-toronto-computer-science`) continues to represent the CS Specialist (ASSPE1689). Two new `ProgramPathway` records (`ca-university-of-toronto-pathway-major`, `-pathway-minor`, both `pathway_type: alternate_exit`) represent the Major and Minor exits reachable from the same CMP1 admission event, each with its own `progression_requirement` reflecting its distinct grade threshold (77% vs. 70% in CSC111H1).
5. **`Program.extension_metadata` trimmed**: `admission_category`, `admission_guarantee_continuation_requirement`, and `alternate_related_programs` are removed from `extension_metadata.fields` now that they are represented as first-class `AdmissionStage`/`ProgramPathway` records. `total_credit_requirement` and `duration_derivation_note` remain in `extension_metadata` since they describe the Specialist Program's own credit load, not a staged-admission concept.
6. **`Program.application_platform` / `application_requirements`**: added (`OUAC`, code `TAD`; Supplemental Application), resolving what was previously only implicit in source excerpts.

## College entity: explicitly and deliberately empty

Toronto's own official page (`src-15`) is the decisive contradiction of Oxford's College hypothesis: "Some colleges sponsor academic programs, but you can study any program regardless of your college," and no statement anywhere ties college assignment to tuition, fees, admission requirements, or scholarship eligibility at Toronto. Zero `College` records for Toronto is not a gap — it is the correct representation of a genuinely different institutional structure, exactly as gm-04's disposition rationale states.

## Unresolved items carried forward unchanged

- **`ca-university-of-toronto-admreq-a-level`** and **`-admreq-us`** remain `UNKNOWN` / `HUMAN_REVIEW` — the primary Faculty of Arts & Science pages were blocked by bot-detection during the original run and were not re-fetched during this migration (migration-only scope, per instruction).
- **`ca-university-of-toronto-cost-domestic-other-province`** remains `UNKNOWN` / `HUMAN_REVIEW` — three inconsistent PDF-table-extraction reads of the same source document, not resolved by guessing.
- A new **`DecisionPlan`** record (`ca-university-of-toronto-decisionplan-2027`) was added with `application_deadline: null` and `verification_status: UNKNOWN`, explicitly modeling Toronto's own disclosed absence of a stated deadline on the CS program page — the application *structure* (single OUAC cycle, non-binding) is confirmed; only the exact date is not.

## Unmapped facts

None. Every fact in the V1.1 record — including every `extension_metadata` entry — is either preserved unchanged or promoted to a new structured entity.

## Validation result

`records-v1.2.json` validates cleanly against `evidapath-schema-v1.2.json` (0 errors).

## VerificationRecord formalization

`verification-records-v1.2.json` in this folder carries forward the original V1.1 run's field-level `VerificationRecord`s, reformatted to the V1.2 schema: any record with the informal `absence_claim: true` flag had its `verification_status` promoted to the now-formal `VERIFIED_ABSENT` enum value; `material_extension_fact` is preserved as the now-formal schema field (unchanged in meaning); any NYUAD-run-specific informal semantic-QA flags (`financial_aid_semantic_reviewed`, `holistic_admissions_semantic_reviewed` -- not part of the V1.2 schema) were folded into `conflict_or_limitation_notes` as a bracketed annotation. This is a reformatting pass only -- no field-level claim was added, removed, or re-verified.
