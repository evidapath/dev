# EvidaPath V1.2 Entity-Relationship Overview

## Entity list (19 top-level collections)

Unchanged from V1.1 (8): `Country`, `City`, `University`, `Campus`, `ApplicantCategory`, `SourceRecord`, `ChangeRecord`, `DerivedCostEstimate`.
Modified from V1.1 (5): `Program`, `AdmissionsRequirement`, `CostProfile`, `Scholarship`, `VerificationRecord`.
New in V1.2 (6): `College`, `ProgramPathway`, `AdmissionStage`, `DecisionPlan`, `FinancialRequirement`, `FinancialAidPolicy`.

(19 = 8 + 5 + 6.)

## Reference graph (parent → child, `_ref` fields only; embedded objects not shown)

```
Country
  └─< City
        └─< University  (country_ref, city_ref)
              ├─< Campus                    (university_ref)
              ├─< College                   (university_ref)                         [OPTIONAL, may be empty]
              ├─< ApplicantCategory         (university_ref)
              ├─< AdmissionStage            (university_ref, program_ref?, applicant_category_ref?)
              ├─< DecisionPlan              (university_ref, program_ref?)
              ├─< FinancialAidPolicy        (university_ref, program_ref?)
              └─< Program                   (university_ref, campus_ref?, college_ref?)
                    ├─< ProgramPathway       (program_ref)
                    ├─< AdmissionsRequirement (program_ref, prior_curriculum_category_ref, admission_stage_ref?)
                    ├─< CostProfile          (program_ref, residency_category_ref, college_ref?, program_pathway_ref?)
                    ├─< FinancialRequirement (program_ref, residency_category_ref)
                    └─< Scholarship          (program_ref?, college_ref?)

SourceRecord            <── referenced by source_refs[] from every VERIFIED/SUPPORTED/etc. entity above
VerificationRecord      <── one per field/claim checked, references the entity+field it verifies + source_refs
ChangeRecord            <── produced on reruns only, references the entity+field that changed
DerivedCostEstimate     <── references CostProfile(s) + Program; EvidaPath-calculated, never a source fact
```

`?` marks a nullable/optional reference. `<` marks "referenced by" (child holds the foreign key).

## Why each `?` is nullable, in one line each

- `Program.campus_ref` — null only when campus-level modeling would fabricate a distinction the university doesn't actually make (Oxford).
- `Program.college_ref` — null for every university without a materially admissions/cost-relevant collegiate structure (all but Oxford).
- `AdmissionStage.program_ref` — null when the stage applies university-wide, before any program-specific decision (NYUAD's holistic review).
- `AdmissionStage.applicant_category_ref` — null when the stage applies uniformly across all prior-curriculum categories (most Faculty-entry stages).
- `DecisionPlan.program_ref` — null when the decision plan is university-wide, not program-specific (NYUAD's ED/RD).
- `FinancialAidPolicy.program_ref` — null when the aid policy is university-wide.
- `CostProfile.college_ref` / `.program_pathway_ref` — null unless a genuine college- or pathway-specific cost component exists.
- `Scholarship.college_ref` — null unless the scholarship is college-administered.
- `AdmissionsRequirement.admission_stage_ref` — null for institutions/records that predate stage-level modeling being material (kept nullable rather than required so simple single-stage institutions aren't forced to synthesize a trivial stage).

## Why `College`, `ProgramPathway`, `FinancialRequirement`, and `FinancialAidPolicy` are genuinely optional collections

Unlike `Campus` (every university has at least one) or `AdmissionsRequirement` (every program has admissions criteria), these four collections are expected to be **empty arrays for most institutions** in the current five-school dataset:
- `College`: empty for all five institutions in this migration. Oxford is the entity's structural justification (per-college fee bundling, college-specific hardship-fund variance evidenced in `src-08`/`src-09`), but no individual Oxford college was independently source-verified as a named, first-class record during the original Oxford run -- the only college names that appeared (St Anne's, St Catherine's) came from a `secondary`-type corroboration-only source (`src-09`), which per the source hierarchy is never used to populate a structured field. Populating real, individually-sourced `College` records for Oxford is flagged as a follow-up research item (see Oxford's `migration-report.md`), not fabricated in this synthesis pass, which is migration-only per the user's explicit instruction not to re-research.
- `ProgramPathway`: populated for Oxford (integrated continuation, BA -> MCompSci) and Toronto (Specialist/Major/Minor); empty for TU Delft, TU Munich, NYU Abu Dhabi (each has one program, one degree shape, no internal pathway split).
- `FinancialRequirement`: populated for TU Delft (IND proof-of-funds), TU Munich (Sperrkonto), and Oxford (UK Student visa maintenance-funds threshold); empty for Toronto and NYU Abu Dhabi (no immigration-liquidity requirement was found published for either).
- `FinancialAidPolicy`: populated only for NYU Abu Dhabi (the only institution with individualized, non-fixed need-based aid as opposed to fixed-amount scholarships).

This asymmetry is intentional and expected: V1.2's promotion bar is evidence-driven, not uniform-coverage-driven. An empty array is not a gap — it means no institution in the current evidence base demonstrated that need for that university, and nothing should be invented to fill it.

## Embedded objects (never independently referenced; travel inside their parent record)

- `Program.testing_policy` → `TestingPolicy` → `TestingPolicy.accepted_assessments[]` → `AcceptedAssessment`
- `Program.application_requirements[]` → `ApplicationRequirement` (same shape reused inside `FinancialAidPolicy.application_requirements[]`)
- `AdmissionStage.criteria[]` → `SelectionCriterion`
- `CostProfile.estimated_living_costs_monthly_range` → `MonthlyRange`
- `ProgramPathway.progression_requirement` → `ProgressionRequirement`
- `CostProfile.living_cost_source_basis` → `LivingCostSourceBasis` (inherited from V1.1, kind enum narrowed)

## Lifecycle applies uniformly

Every entity in this graph — old and new — carries `record_status` through the same `RESEARCHED → STRUCTURED → VERIFIED → HUMAN_REVIEW → APPROVED → PUBLISHED` lifecycle. There is no shortcut lifecycle for any V1.2 addition; a `FinancialAidPolicy` or `AdmissionStage` record requires the same human sign-off to reach `APPROVED` as a `Program` record always has.
