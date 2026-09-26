# EvidaPath V1.2 Sanity content model

## Classification test

Per the EvidaPath pipeline skill's own standing rule: a concept becomes a
Sanity **document type** when it has its own stable ID, is referenced by
multiple records, changes independently of its parent, benefits from
being queried directly, needs its own evidence/verification lifecycle, or
may power its own public page or discovery surface. Everything else is an
**embedded object type** -- data that only ever makes sense nested inside
the document that owns it.

## Document types (19)

| Sanity type | Source `$def` | Why it is a document |
|---|---|---|
| `country` | `country` | Referenced by City, University, Campus, DecisionPlan sourcing; stable across all institutions. |
| `city` | `city` | Referenced by University, Campus; independently useful for city-level filtering/discovery. |
| `university` | `university` | The core institutional entity; referenced by nearly everything; has its own verification lifecycle (`last_researched`, `last_verified`, `record_status`). |
| `campus` | `campus` | Referenced by Program (optionally, since V1.2 -- see below); a university may have several. |
| `college` | `college` | Referenced by CostProfile/Scholarship where populated; genuinely optional (0 records in this test set -- see "College stays empty" below) but a real, independent Oxford-style sub-institutional entity when it exists. |
| `program` | `program` | The central decision-relevant entity every student-facing query ultimately resolves to. |
| `programPathway` | `program_pathway` | Referenced by CostProfile; has its own `progression_requirement`, `verification_status`, and `record_status` independent of the base Program (e.g. Toronto's Major/Minor exits). |
| `applicantCategory` | `applicant_category` | Referenced by AdmissionsRequirement (curriculum dimension) and CostProfile (residency dimension) -- two independent axes, each needing its own queryable record. |
| `admissionStage` | `admission_stage` | Has its own `sequence_order`, `verification_status`, `record_status`, and embedded `criteria[]`; referenced by AdmissionsRequirement. |
| `admissionsRequirement` | `admissions_requirement` | Field-level verified facts with their own `academic_year`, `last_checked`, `verification_status`. |
| `decisionPlan` | `decision_plan` | Independent deadline/binding-status lifecycle per plan type (ED1/ED2/RD/rolling/etc.), referenced nowhere else but queried directly by students. |
| `costProfile` | `cost_profile` | Own `academic_year`, `verification_status`; referenced by DerivedCostEstimate. |
| `financialRequirement` | `financial_requirement` | Independent verification lifecycle (e.g. TU Delft's IND deposit, TU Munich's Sperrkonto, Oxford's visa maintenance-funds threshold); explicitly distinct from CostProfile's genuine cost-of-living estimates. |
| `scholarship` | `scholarship` | Its own eligibility, amount, and deadline lifecycle; often spans multiple programs/institutions. |
| `financialAidPolicy` | `financial_aid_policy` | Deliberately has no numeric `award_amount` (policy-level, not award-level); own verification lifecycle. |
| `sourceRecord` | `source_record` | The evidentiary backbone -- every other document's `source_refs` points here; must be independently queryable to audit any claim. |
| `derivedCostEstimate` | `derived_cost_estimate` | EvidaPath's own calculation, explicitly never conflated with a CostProfile's sourced fact; needs its own `calculation_version`/`calculated_at` lifecycle. |
| `verificationRecord` | `verification_record` | The QA backbone -- one per field/claim checked, independently queryable for audit and for the coverage-gap reporting in `08-reporting/`. |
| `changeRecord` | `change_record` | Populated only on reruns (0 records in this first-run test set); still a first-class document type since a rerun must diff against and reference the exact prior ChangeRecord history. |

### College stays empty -- by design, not by omission

Zero `College` records are populated across all five institutions in this
migration (see `entity-relationship-overview.md`). Oxford is the
structural justification for the entity (official per-college fee
bundling), but no individual Oxford college was independently
source-verified in this test set -- only a secondary-type source named
specific colleges, which this pipeline's source-hierarchy rule (primary
sources only for material facts) correctly refused to promote into a
fabricated record. `college` remains a real document type in the schema,
ready to receive verified records the next time Oxford (or another
collegiate university) is researched in depth; it is not a placeholder
invented for architectural symmetry.

## Object types (11)

| Sanity type | Source `$def` | Nests inside | Why it is NOT a document |
|---|---|---|---|
| `selectionCriterion` | `selection_criterion` | `admissionStage.criteria[]` | Has no ID or lifecycle of its own; only ever meaningful as one line of a specific stage's rubric (e.g. TU Munich's four weighted Eignungsfeststellungsverfahren criteria). |
| `applicationRequirement` | `application_requirement` | `program.application_requirements[]`, `financialAidPolicy.application_requirements[]` | A checklist line item, reused verbatim across two document types; never independently queried or referenced. |
| `testingPolicy` | `testing_policy` | `program.testing_policy` | One-to-one with its owning Program; never shared or referenced elsewhere. |
| `acceptedAssessment` | `accepted_assessment` | `testingPolicy.accepted_assessments[]` | A line inside a policy, not a standalone fact. |
| `monthlyRange` | `monthly_range` | `costProfile.estimated_living_costs_monthly_range` | A `{min, max, currency}` triple with no independent existence. |
| `progressionRequirement` | `progression_requirement` | `programPathway.progression_requirement` | Describes one pathway's own continuation rule; never reused. |
| `livingCostSourceBasis` | `living_cost_source_basis` | `costProfile.living_cost_source_basis` | A required structured annotation of a single CostProfile's basis; carried over unchanged from V1.1's own object-type precedent. |
| `extensionMetadata` | `extension_metadata` | any document with unresolved-but-preserved V1.1/pre-V1 facts | Deliberately generic overflow container -- promoting it to a document would defeat its purpose (flagged-for-later-promotion facts, not a queryable entity). |
| `lineItem` | `line_item` | `costProfile.mandatory_fees_breakdown[]` / `other_material_costs[]` | A `{label, amount, frequency}` triple, never referenced independently. |
| `testRequirement` | `test_requirement` | `admissionsRequirement.standardized_tests[]` | Per-curriculum test detail nested under one AdmissionsRequirement; the *policy-level* test story now lives in `testingPolicy` instead (the two are designed to coexist per `evidapath-schema-v1.2.md`). |
| `languageRequirement` | `language_requirement` | `admissionsRequirement.language_requirements[]` | Same reasoning as `testRequirement`. |

## Minimalism check (explicitly re-confirmed, not just asserted)

Every embedded object above was checked against the promotion criteria
(gap-matrix disposition, `02-schema-design/evidapath-schema-v1.2.md`)
before this package was built: none of them is independently referenced
by more than the one or two document types listed, none carries its own
`verification_status`/`record_status` lifecycle distinct from its parent,
and none has a plausible standalone public page. Nothing in this list was
promoted to a document type "for consistency" -- each stayed embedded
because it failed the promotion test, the same discipline applied when
the six new document types (College, ProgramPathway, AdmissionStage,
DecisionPlan, FinancialRequirement, FinancialAidPolicy) were promoted in
the schema-design phase.
