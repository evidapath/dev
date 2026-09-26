# EvidaPath Data Model V1.2 (conceptual reference)

This document is the conceptual companion to the executable `evidapath-schema-v1.2.json`. It is authoritative over the JSON file: if the two ever disagree, this document reflects intent and the JSON must be corrected to match it.

V1.2 is synthesized entirely from five completed V1.1 stress-test runs (TU Delft, Oxford, Toronto, TU Munich, NYU Abu Dhabi) per the gap matrix in `01-gap-analysis/five-school-gap-matrix.md`. No new institution was researched to produce this schema. Every entity, field, and enum value below traces to a specific gap-matrix row (`gm-XX`), cited inline.

## Design principle carried through every decision below

Promote a concept to a first-class entity or structured field only when (1) multiple institutions independently demonstrated the need, or (2) one institution demonstrated a severe modeling failure that materially affects a student decision and cannot safely remain in `extension_metadata`. Where a simpler shape (a field, an enum value, an embedded object) resolves the same gap as a new top-level entity, the simpler shape was chosen. Six overlapping stage/selection/qualification concepts raised across Toronto, TU Munich, and NYU Abu Dhabi were collapsed into one generalized entity (`AdmissionStage`) rather than becoming six.

## Unchanged from V1.1 (no structural change; referenced, not repeated)

`Country`, `City`, `University`, `Campus`, `ApplicantCategory`, `SourceRecord`, `ChangeRecord`, `DerivedCostEstimate` carry forward with no field or semantic changes. Their full field tables live in V1.1's `evidapath-schema-v1.1.json` and are inherited verbatim into V1.2's `$defs`.

`ApplicantCategory`'s two-dimension design (`prior_curriculum` vs `residency_citizenship`, established by TU Delft) proved sufficient for all five institutions, including Toronto's three-way domestic-Ontario/domestic-other-province/international residency split (gm-19, disposition E — reject, no schema change needed, the existing generic dimension already covers it).

## New top-level entities

### College (gm-04 — disposition A, promote; OPTIONAL entity)

**Purpose.** Represents a collegiate sub-structure within a university, where colleges have their own identity, admissions relevance, or scholarship/cost relevance, but a program is not exclusively owned by one college.

**Evidence.** Oxford's collegiate system materially affects which scholarships a student is eligible for and can carry college-specific cost components. Toronto explicitly contradicted the idea that every university needs this: "Some colleges sponsor academic programs, but you can study any program regardless of your college" — Toronto's colleges are not admissions- or cost-relevant in the same way.

**Design decision.** `College` is a genuinely optional entity. It is never required on `Program` (a program is not owned by a college) and is referenced only where evidence shows it materially affects an outcome: `Scholarship.college_ref` and `CostProfile.college_ref`. Universities without a materially relevant collegiate structure (Toronto, TU Delft, TU Munich, NYU Abu Dhabi) simply have zero `College` records and never populate those optional refs.

**Required fields.** `id`, `university_ref`, `name`, `source_refs`, `record_status`.
**Optional fields.** `description`, `official_url`, `extension_metadata`.

### ProgramPathway (gm-06, gm-20 — disposition A, promote)

**Purpose.** Represents a degree pathway reachable from or through a base `Program` that is not itself a separate admission event: an integrated continuation (Oxford's BA Computer Science → MCompSci, admitted once, degree shape decided later by performance) or an internal specialization/exit point (Toronto's Specialist/Major/Minor structure within one Computer Science admission).

**Evidence.** Oxford's undergraduate CS admits into a single course that can conclude as a BA (3 years) or extend to an integrated MCompSci (4 years) based on second/third-year performance — one admission event, two possible degree outputs, each with its own duration and cost implications. Toronto's Computer Science students are admitted to a Faculty/subject POSt system and later declare a Specialist, Major, or Minor combination — again one admission event, multiple possible final program shapes.

**Design decision.** Generalized as a single entity with a `pathway_type` enum (`primary`, `integrated_continuation`, `alternate_exit`) rather than solving only Oxford's case or only Toronto's. `progression_requirement` is embedded directly on `ProgramPathway` (see below) rather than becoming its own top-level entity, since it never has an independent lifecycle apart from the pathway it describes (gm-07, disposition C reinforced as embedded-not-standalone by minimalism test).

**Required fields.** `id`, `program_ref`, `pathway_type`, `degree_type`, `degree_type_local`, `duration_value`, `duration_unit`, `source_refs`, `verification_status`, `record_status`.
**Optional fields.** `progression_requirement` (embedded object: `description`, `gpa_or_class_threshold`, `decision_point_timing`), `notes`, `extension_metadata`.

### AdmissionStage (gm-12, gm-13, gm-14, gm-21, gm-22 — disposition A, promote; the single most consequential V1.2 change)

**Purpose.** A single generalized entity representing any discrete, sequenced step in how a student moves from "applies" to "is fully admitted into their eventual program," at whatever level of the institution that step occurs (university-wide, faculty-wide, category-specific, program-specific, or post-matriculation).

**Evidence this collapses.** Five previously proposed, overlapping entities/fields across three institutions all describe the same underlying shape — a named, ordered step with eligibility/selection criteria and a defined outcome:
- Toronto's `AdmissionStage` (Faculty-level entry before program-specific admission) and `ProgressionRequirement` (the GPA/course threshold gating entry from general first year into the Specialist/Major).
- TU Munich's `ApplicationStage`, `SelectionProcedure`, `SelectionCriterion`, and `SelectionStage` (TUM's multi-step, criteria-weighted selection process for its restricted-admission programs), and `QualificationRecognitionPathway` (how a foreign qualification is recognized as equivalent to the Abitur before substantive review begins).
- NYU Abu Dhabi's `MajorDeclaration` (admitted to the university generally; declares Computer Science as a major later, by a disputed second-year deadline) and its university-wide holistic admission step itself.

**Design decision.** One entity, `stage_type` enum (`university_entry`, `faculty_entry`, `admission_category`, `qualification_recognition`, `preparatory_pathway`, `selection_stage`, `program_entry`, `major_declaration`, `progression`), `sequence_order` integer for ordering multi-stage flows, and an embedded `criteria[]` array of `SelectionCriterion` objects (`criterion_name`, `description`, `threshold_or_formula`, `weight`, `mandatory`) replacing TU Munich's four separate selection entities. `program_ref` and `applicant_category_ref` are both nullable, because a stage may apply at the university level (NYUAD's holistic review, no `program_ref`) or uniformly across categories (Toronto's Faculty entry, no `applicant_category_ref`). This directly satisfies the explicit instruction not to create overlapping entities when one generalized staged model can represent all four institutions.

**Required fields.** `id`, `university_ref`, `program_ref` (nullable), `stage_type`, `sequence_order`, `name`, `description`, `criteria` (array, may be empty), `source_refs`, `verification_status`, `record_status`.
**Optional fields.** `applicant_category_ref`, `decision_outcome_options`, `notes`, `extension_metadata`.

**Relationship to `AdmissionsRequirement`.** `AdmissionStage` does not replace `AdmissionsRequirement`; it sequences and contextualizes it. `AdmissionsRequirement` gained an optional `admission_stage_ref` (gm-14) so an existing per-curriculum requirement record can point at which stage it belongs to, without duplicating the requirement data inside the stage itself.

### DecisionPlan (gm-05, gm-23 — disposition A, promote)

**Purpose.** Represents a structured admission-cycle plan with its own deadline, decision-release timing, and binding status — resolving the recurring gap that Early Decision/Regular Decision-style structures had no canonical field and were being described only in free text.

**Evidence.** Oxford (a single annual UCAS deadline, but an external application code needed representation), Toronto (single deadline per cycle, but early/regular internal distinctions for some programs), TU Munich (a restricted-admission internal deadline distinct from the general enrollment deadline), and NYU Abu Dhabi (explicit ED I / ED II / Regular Decision structure with different binding status per plan) all independently needed a structured way to represent "which admission plan, what deadline, is it binding."

**Design decision.** `plan_type` enum (`early_decision_1`, `early_decision_2`, `regular_decision`, `rolling`, `single_stage`, `program_specific_stage`) covers both NYUAD's multi-plan structure and the single-deadline institutions (which get exactly one `DecisionPlan` record with `plan_type: single_stage`). `program_ref` is nullable for university-wide plans (NYUAD's ED/RD applies across NYU, not per-campus).

**Required fields.** `id`, `university_ref`, `program_ref` (nullable), `plan_type`, `academic_year`, `source_refs`, `verification_status`, `record_status`.
**Optional fields.** `application_platform`, `binding`, `application_deadline`, `decision_release_date`, `notes`, `extension_metadata`.

### FinancialRequirement (gm-15, gm-16 — disposition A, promote)

**Purpose.** Represents a liquidity/proof-of-funds requirement imposed by an immigration authority or the university itself as a condition of visa issuance or enrollment — structurally distinct from a genuine cost-of-living estimate, and distinct from tuition.

**Evidence.** TU Delft's Dutch IND proof-of-funds figure and TU Munich's Sperrkonto (blocked account) requirement are both refundable-or-lockable liquidity thresholds a student must demonstrate, not money they spend on living costs. Under V1.1 these had to be squeezed into `CostProfile.living_cost_source_basis.kind: visa_proof_of_funds_deposit`, conflating "how much will you spend to live" with "how much must you prove you have," which materially misleads a student budgeting for the degree.

**Design decision.** New entity with `requirement_type` enum (`visa_proof_of_funds`, `blocked_account`, `government_minimum_resources`, `enrollment_deposit`, `other_liquidity_requirement`), `refundable` boolean, and `administering_body` (so a student can tell "this is the Dutch immigration service's number," not the university's). `living_cost_source_basis_kind` in V1.2 drops `visa_proof_of_funds_deposit` entirely (gm-16) — that concept now lives only here, never duplicated as a cost-profile kind.

**Required fields.** `id`, `program_ref`, `residency_category_ref`, `requirement_type`, `amount`, `currency`, `refundable`, `administering_body`, `academic_year`, `source_refs`, `verification_status`, `record_status`.
**Optional fields.** `frequency`, `notes`, `extension_metadata`.

### FinancialAidPolicy (gm-17, gm-24 — disposition A, promote)

**Purpose.** Represents an institution's *policy* for awarding individualized, non-fixed financial aid — what mechanism exists, whether it's need-aware or need-blind, what's required to apply — without ever stating a numeric award amount for an individual.

**Evidence.** NYU Abu Dhabi offers need-based aid via CSS Profile to all non-Emirati applicants with amounts that are explicitly individualized and non-fixed. `Scholarship` (V1.1) is structurally a fixed-or-formula award record; representing NYUAD's aid there would force fabricating or averaging an amount that doesn't exist as a single public fact.

**Design decision.** `FinancialAidPolicy` deliberately has **no numeric `award_amount` field of any kind** — this is a design constraint, not an oversight, and is stated explicitly in the field's own JSON Schema `description` so a future engineer does not "fix" it by adding one. It captures only public, policy-level facts: mechanism (`policy_type`: `need_based` / `merit_based` / `mixed`), `need_aware_or_blind`, application requirements, and free-text `award_basis_description`. Individualized per-student `AidPackage` records (what a specific admitted student is actually offered) were explicitly evaluated and **rejected** from Sanity (gm-24, disposition E) — that is personalized student-outcome data, and per the user's own system separation belongs in Supabase once a student has an actual offer, never fabricated or represented as public market knowledge in Sanity.

**Required fields.** `id`, `university_ref`, `program_ref` (nullable), `policy_type`, `need_aware_or_blind`, `award_basis_description`, `application_requirements` (array, may be empty), `source_refs`, `verification_status`, `record_status`.
**Optional fields.** `need_assessment_mechanism`, `eligible_population_notes`, `max_award_cap_description`, `renewable`, `renewal_conditions`, `application_deadline`, `academic_year`, `extension_metadata`.

## New embedded object types (not top-level entities — deliberately)

These resolve real gaps without becoming independently-lifecycled documents, per the minimalism test (a field/embedded object beats a new entity when nothing needs to reference or version it independently).

- **`SelectionCriterion`** — embedded in `AdmissionStage.criteria[]`. Fields: `criterion_name`, `description`, `threshold_or_formula`, `weight`, `mandatory`. Replaces TU Munich's standalone `SelectionCriterion` entity proposal (gm-13, disposition B not A — structured field, not new document type).
- **`ApplicationRequirement`** — embedded in `Program.application_requirements[]` and reused inside `FinancialAidPolicy.application_requirements[]`. Fields: `requirement_type` (enum: form, transcript_or_school_report, recommendation, essay, standardized_test_score, self_reported_record, interview_or_evaluation_event, financial_document, other), `name`, `necessity`, `description`, `notes`. Resolves the recurring "what does the application actually consist of" gap (Oxford's personal statement + reference + written work; TU Munich's transcript + language certificate + motivation letter; NYUAD's Common App + supplements) without adding a separate `ApplicationArtifact` entity, which was explicitly considered and rejected (gm-09, disposition E — one embedded array is sufficient; nothing about an individual requirement needs independent identity, verification lifecycle, or cross-record reference).
- **`TestingPolicy`** — embedded, nullable object on `Program.testing_policy`. Fields: `policy_type` (enum: required, optional, test_flexible, test_blind, not_applicable), `accepted_assessments[]` (array of `AcceptedAssessment`), `scope_note` (free text stating which cycle(s) the policy covers), `source_refs`. Resolves NYUAD's test-optional-through-a-specific-cycle policy, which is a policy-level fact distinct from the per-curriculum `AdmissionsRequirement.standardized_tests[]` array (which states what a given curriculum's applicants may submit). The two coexist deliberately: `testing_policy` says "is testing required at all, and through when," `AdmissionsRequirement.standardized_tests` says "for this curriculum, which specific tests are accepted."
- **`AcceptedAssessment`** — embedded in `TestingPolicy.accepted_assessments[]`. Fields: `test_name`, `necessity`, `competitive_benchmark` (explicitly documented as a non-binding "competitive applicants typically score" figure — never represented as a formal minimum unless the source states a real minimum, directly enforcing the holistic-admissions semantic QA rule from the NYUAD run), `notes`.
- **`MonthlyRange`** — embedded, nullable object on `CostProfile.estimated_living_costs_monthly_range`. Fields: `min`, `max`, `currency`. Resolves Oxford's publication shape (a monthly range, e.g. £1,300–£1,900/month) which V1.1 could only awkwardly force into an annual point estimate (gm-10, disposition B).
- **`ProgressionRequirement`** — embedded, nullable object on `ProgramPathway.progression_requirement`. Fields: `description`, `gpa_or_class_threshold`, `decision_point_timing`.

## Modified existing entities

### Program

- `campus_ref` is now **optional/nullable** (was required in V1.1). Resolves Oxford's forced fabrication of a synthetic "central campus" record where no such administrative unit exists in reality (gm-11, disposition B). A university with a genuine single campus still populates it normally; `null` is reserved for cases where campus-level modeling would misrepresent the institution.
- New optional field `college_ref` — nullable reference, populated only for institutions where a program is meaningfully associated with one or more colleges at the point of admission (in practice, currently unused directly on `Program` since Oxford's college relevance surfaces through `Scholarship`/`CostProfile` instead; the field exists for completeness and future evidence, per gm-04's rationale that College must never be forced onto every program).
- New optional field `application_platform` (string) — e.g. "UCAS", "Common Application", "TUMonline".
- New optional field `application_requirements` (array of embedded `ApplicationRequirement`) — see above.
- New optional field `testing_policy` (nullable embedded `TestingPolicy`) — see above.

### AdmissionsRequirement

- New optional field `admission_stage_ref` (nullable) — links a per-curriculum requirement to the generalized `AdmissionStage` it belongs to, without duplicating stage data.

### CostProfile

- `living_cost_source_basis.kind` enum **narrowed**: `visa_proof_of_funds_deposit` removed (that concept now belongs exclusively to `FinancialRequirement`). Remaining values: `genuine_cost_of_living_estimate`, `government_minimum_income_threshold`, `not_published`.
- New optional field `estimated_living_costs_monthly_range` (nullable embedded `MonthlyRange`).
- New optional field `college_ref` (nullable) — for college-specific cost components (Oxford college fees).
- New optional field `program_pathway_ref` (nullable) — for cost differences tied to a specific pathway (e.g. Oxford's 4th integrated MCompSci year has its own cost line distinct from the 3-year BA).

### Scholarship

- New optional field `college_ref` (nullable) — for college-administered scholarships (Oxford).

### VerificationRecord

- `material_extension_fact` **formalized** as a real, documented, optional boolean field (was an informal additive convention in the TU Munich and NYU Abu Dhabi runs). True when a `VerificationRecord` independently verifies a decision-relevant fact that lives in an entity's `extension_metadata.fields` rather than in a canonical schema field — this is how V1.2's QA tooling checks "material extension_metadata coverage" (gm-27, disposition B).

## Enum changes

- **`verification_status`** gains `VERIFIED_ABSENT` (gm-26 / carried QA rule, disposition A). Formalizes the distinction, used informally as an `absence_claim` boolean in the TU Munich and NYU Abu Dhabi runs, between "we affirmatively confirmed this fact does not exist / does not apply" (e.g. "no minimum IB point total is published — only a subject requirement") and plain `UNKNOWN` ("we could not find evidence either way"). A record with `VERIFIED_ABSENT` still cites `source_refs` — the sources that support the absence claim itself.
- **`duration_unit`** gains `semesters` (gm-18, disposition B). Resolves TU Munich's semester-denominated program duration, which V1.1 could only represent by a lossy conversion to years.
- **`living_cost_source_basis_kind`** narrowed (see CostProfile above).
- **`degree_type`** is explicitly **unchanged** — no "BS" value was added (gm-25, disposition E, reject). NYU Abu Dhabi's Bulletin-canonical "BS" vs. its own marketing page's ambiguity is already fully resolved by the existing `degree_type_local` field, which preserves the exact regional/institutional wording without enum bloat for what is fundamentally the same degree as "BSc" elsewhere.

## New enums

`admission_stage_type`, `financial_requirement_type`, `financial_aid_policy_type`, `need_aware_or_blind`, `pathway_type`, `application_requirement_type`, `decision_plan_type`, `requirement_necessity` — full value lists are in the executable JSON schema's `$defs`.

## Meaningful-null / absence semantics (formalized QA rule, carried from TU Munich/NYU Abu Dhabi)

A `null` value with `verification_status: UNKNOWN` means "not researched or not found — absence of evidence." A `null` value with `verification_status: VERIFIED_ABSENT` means "affirmatively confirmed not to exist or not to apply, backed by `source_refs` that support the absence claim." These are never interchangeable, and QA tooling (`check_verification_coverage_v1_2.py`) checks that every `VERIFIED_ABSENT` claim carries at least one source reference, exactly as every other verified fact does.

## extension_metadata rules (unchanged from V1.1, restated)

Every entity retains an `extension_metadata` object (`{fields: {...}, notes}`) as the sole escape hatch for a real, sourced fact that has no canonical field yet. A fact in `extension_metadata` is never fabricated data and is never a substitute for promoting a field that meets the promotion bar above; it is reserved for genuinely institution-specific or not-yet-recurring facts (disposition C in the gap matrix). When a fact in `extension_metadata` is independently verified and materially affects a student decision, its `VerificationRecord` sets `material_extension_fact: true` so QA tooling can surface it for future schema review, without forcing an immediate schema change.

## Record lifecycle (unchanged from V1.1, restated for completeness)

`RESEARCHED → STRUCTURED → VERIFIED → HUMAN_REVIEW → APPROVED → PUBLISHED`. Nothing skips `VERIFIED`. `HUMAN_REVIEW → APPROVED` requires explicit human sign-off, every time. Sanity publishing is a separate, still-unauthorized gate independent of `record_status` — even an `APPROVED` record's Sanity draft is not pushed live without explicit authorization. This applies identically to every new V1.2 entity; none of them get a shortcut lifecycle.

## Source and verification requirements (unchanged from V1.1, restated)

Every new entity requires `source_refs` (minItems: 1) and a `verification_status`. No new entity may exist as speculative or inferred data — the same "evidence before schema" discipline governing V1.1 governs every V1.2 addition. This is enforced structurally: `source_refs` and `verification_status` are `required` fields on every new `$def`, not optional conveniences.
