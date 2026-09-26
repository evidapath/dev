# Five-school synthesis: what changed, and because of which university

"Evidence before architecture" means every new V1.2 concept must trace
back to a specific, real modeling failure one or more of the five test-set
institutions actually exposed -- not a speculative future need. This
document is that trace, organized by institution, so the schema's
provenance stays auditable.

## TU Delft (Netherlands)

The pilot run, and the one that established the process discipline every
later run and this synthesis itself inherited (the 2026-09-22 finding that
the seven-phase artifact contract had been designed but not actually
produced -- fixed before any other institution ran). Structurally, TU
Delft's own V1.1 data was the most schema-compliant of the five (a
Bologna-system institution with a single, cleanly bounded admission
route), so it drove fewer *new* V1.2 entities than the other four and
instead exposed two migration-tooling gaps this synthesis had to fix on
its own data:
- `university.last_verified: null` broke V1.1's schema, which required
  `last_verified` as a plain string -- fixed by loosening the V1.2 schema
  field to `["string", "null"]`, a small, general fix (not TU-Delft-
  specific), since "never verified" is a real, meaningful record state.
- TU Delft's own `sources.json` used a record-ID-prefixed
  `fields_supported` convention instead of the canonical `EntityType.field`
  form used elsewhere -- fixed with a `normalize_field_entry()` mapping
  function in the migration script, not by weakening
  `check_fields_supported_v1_2.py`'s bar.
- TU Delft's IND blocked-account-style deposit was the first evidence for
  what became `FinancialRequirement.requirement_type: visa_proof_of_funds`
  -- the same entity Germany's Sperrkonto and the UK's visa maintenance-
  funds threshold would later confirm as a genuine, recurring, cross-
  institution concept (promotion criterion 1: multiple institutions
  independently demonstrate the need).

## Oxford (United Kingdom)

The institution that most directly justified `ProgramPathway` and
`College`, and the first to demonstrate `FinancialRequirement` recurring
outside the Netherlands:
- BA→MCompSci is a genuine `pathway_type: integrated_continuation` --
  V1.1 had no way to represent "the same admission event leads to two
  different, officially distinct degree outcomes depending on later
  progression," and Oxford's own official pages state this explicitly.
- Oxford's collegiate system is the structural justification for the
  `College` entity -- per-college fee bundling is real and officially
  documented -- but no individual college was independently source-
  verified from a primary source in this test set (only a secondary
  source named specific colleges), so **zero `College` records were
  populated**, honoring the source-hierarchy rule rather than fabricating
  a record to match the entity's own justification.
- UK visa maintenance-funds thresholds became the second confirming case
  for `FinancialRequirement` (after TU Delft's IND deposit), and the one
  that required correcting the entity's `requirement_type` from an
  initial `other_liquidity_requirement` guess to the more precise
  `government_minimum_resources`.
- Oxford's monthly living-cost range (GBP 1,475-2,175) was the first
  evidence for `CostProfile.estimated_living_costs_monthly_range`, later
  confirmed as a recurring need by TU Munich's own monthly Sperrkonto-
  adjacent range.
- Two `DerivedCostEstimate` records referencing the now-retired visa-
  maintenance-funds `CostProfile` were retired (not deleted -- the
  underlying facts remain fully present on the `FinancialRequirement`
  record) once that `CostProfile` was superseded, documented in Oxford's
  own migration report.

## Toronto (Canada)

The single most consequential migration of the five, and the primary
evidence for `AdmissionStage`, one of the two new entities meeting
promotion criterion 2 (a severe single-institution modeling failure
materially affecting a student decision) even before other institutions
confirmed the pattern:
- V1.1 had no way to represent that a Toronto applicant applies to a
  university-wide "CMP1" admission category, not directly to the CS
  Specialist program -- a structural fact the original V1.1 run could
  only capture as unstructured `Program.extension_metadata` text. This
  became `AdmissionStage.stage_type: admission_category`.
- The Admission Guarantee (continuation into CS Major/Minor) and the
  out-of-stream competitive pathway for non-CMP1 students became two more
  `AdmissionStage` records (`stage_type: progression`), each with
  structured `criteria[]` instead of free text.
- Specialist/Major/Minor -- three genuinely different degree exits
  reachable from the same admission event -- became the second confirming
  case for `ProgramPathway` (`pathway_type: alternate_exit`), each with
  its own distinct grade threshold (77% vs. 70% in CSC111H1).
- Toronto's own official page was the decisive **counter-evidence**
  against forcing `College` records everywhere: it explicitly states
  college assignment has no bearing on tuition, fees, admission, or
  scholarship eligibility at Toronto, confirming that a genuinely empty
  `College` collection for Toronto is correct modeling, not a gap.
- A new `DecisionPlan` record was added with `application_deadline: null`
  and `verification_status: UNKNOWN`, correctly modeling Toronto's own
  disclosed absence of a stated deadline rather than inventing one.

## TU Munich (Germany)

The largest single `extension_metadata` block of any institution, and the
primary evidence for the qualification-recognition and multi-stage-
selection variants of `AdmissionStage`, plus the `semesters` duration unit:
- A uni-assist VPD qualification-recognition gate (does a foreign
  credential grant direct, restricted, or no eligibility?) became
  `AdmissionStage.stage_type: qualification_recognition` -- a concept no
  other institution in the test set needed in this exact form, but one
  severe enough on its own (a gate that can eliminate an applicant before
  any program-level review) to meet promotion criterion 2.
- TUM's two-stage, weighted-point Eignungsfeststellungsverfahren became
  `AdmissionStage.stage_type: selection_stage` with four embedded
  `SelectionCriterion` entries -- resolving the specific "how do we model
  a multi-stage, weighted-point selection procedure without flattening it
  into text" gap the original TU Munich run itself identified.
- Studienkolleg (the preparatory-year alternative branch, reached only
  when qualification recognition fails) became
  `AdmissionStage.stage_type: preparatory_pathway`, modeled at the same
  `sequence_order` as the qualification-recognition stage rather than
  sequentially after it, matching the real decision logic.
- TUM's officially published "6 Semester" duration could previously only
  be represented via a lossy conversion to `duration_value: 3.0 years`,
  capped at `SUPPORTED` confidence specifically because of that
  conversion. V1.2's `duration_unit` enum gaining `"semesters"` lets this
  Program record state TUM's own figure verbatim at higher confidence.
- The Sperrkonto (blocked account) requirement -- previously a
  `CostProfile` record that its own `extension_metadata` said existed
  "only because V1.1 could not represent this fact any other way" --
  became the second confirming case for `FinancialRequirement`
  (`requirement_type: blocked_account`), retiring that `CostProfile` in
  the process.
- TUM's monthly living-cost range (EUR 1,300-2,000) was the second
  confirming case for `CostProfile.estimated_living_costs_monthly_range`.

## NYU Abu Dhabi (UAE)

The institution with the richest holistic-admissions and financial-aid
detail, and the sole evidence for `FinancialAidPolicy`, `DecisionPlan`'s
three-plan-type structure, and `Program.testing_policy`:
- University-wide holistic admission (decided above the level of any
  specific program) became `AdmissionStage.stage_type: university_entry`.
- Major declaration -- including a genuine, disclosed two-source deadline
  conflict ("end of second year" vs. "spring break of second year") --
  became `AdmissionStage.stage_type: major_declaration`, preserved as
  `CONFLICT`/`HUMAN_REVIEW`, not resolved by guessing.
- Early Decision I / II / Regular Decision became three separate
  `DecisionPlan` records -- exactly the structure this entity exists to
  resolve, and the confirming case that made `DecisionPlan` a genuinely
  cross-institution concept once Toronto's, Oxford's, TU Munich's, and TU
  Delft's own application timelines were retrofitted into the same entity.
- NYU's test-optional policy through the 2027-2028 cycle became
  `Program.testing_policy` -- the sole population of this new embedded
  object in the test set, deliberately left `null` everywhere else since
  no other institution published an equivalent policy-level statement.
- Individualized need-based aid (general + Falcon Dirhams for UAE
  nationals) became two `FinancialAidPolicy` records -- deliberately
  carrying **no numeric `award_amount` field**, matching the original
  run's own semantic-QA finding that no single public award figure exists
  to state. `need_aware_or_blind: "unknown"` on both records preserves
  the original run's finding that "need-aware" was the extraction tool's
  own characterization, never an exact NYU quote.
- The gap matrix's rejection of adding a literal "BS" `degree_type` enum
  value (gm-25) was tested directly against NYUAD's own wording ("Bachelor
  of Science (BS)") and confirmed: `degree_type_local` already preserves
  the exact regional abbreviation without enum bloat for what is
  fundamentally the same degree.

## What this trace confirms

Every one of the six new top-level V1.2 entities
(`AdmissionStage`, `ProgramPathway`, `DecisionPlan`, `FinancialRequirement`,
`FinancialAidPolicy`, `College`) and every embedded-object addition
(`TestingPolicy`/`AcceptedAssessment`, `MonthlyRange`, the `semesters`
duration unit, `VERIFIED_ABSENT`) traces to a specific, named, source-
documented institutional fact -- never to a speculative "this seems like
it would be useful" addition. Where an institution's evidence was
insufficient to populate an entity its own structure justified (Oxford's
`College`), that is disclosed as an honest gap, not silently worked
around.
