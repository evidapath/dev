# Five-school V1.2 gap matrix

Every V1.2 candidate surfaced across the five completed EvidaPath runs (TU Delft, Oxford, Toronto, TU Munich, NYU Abu Dhabi), classified by disposition. Disposition legend: **A** = promote to V1.2 entity, **B** = add as structured field/enum/embedded object, **C** = keep as extension_metadata / permanent pipeline practice (no schema change), **D** = defer to V1.3+, **E** = reject.

## Disposition summary

| Disposition | Count |
|---|---|
| A | 10 |
| B | 11 |
| C | 4 |
| D | 1 |
| E | 2 |

## Full matrix

### gm-01: prior_curriculum vs residency_citizenship split (ApplicantCategory two dimensions)

- **Institution(s):** TU Delft
- **Problem:** A student's admissions route (curriculum) and their tuition rate (residency/citizenship) are independent axes; one shared applicant_category field conflates them.
- **V1.1 representation:** acceptable
- **Affects:** Discover, Analyze, Plan
- **Nature:** recurring
- **Disposition: C -- KEEP AS-IS (already correct in V1.1)**
- **Rationale:** This is V1.1's own original innovation from the TU Delft pilot and has worked cleanly across all five runs (confirmed again by NYUAD's citizenship-affects-aid-not-cost finding). No V1.2 change needed -- carried forward unchanged.

### gm-02: living_cost_source_basis structured field

- **Institution(s):** TU Delft, TU Munich
- **Problem:** Some 'living cost' figures are refundable visa proof-of-funds deposits, not genuine cost-of-living estimates; collapsing them misrepresents both.
- **V1.1 representation:** awkward
- **Affects:** Discover, Analyze, Plan, Fund, public University page
- **Nature:** recurring
- **Disposition: B -- REFINE STRUCTURED FIELD**
- **Rationale:** The concept was right but the visa_proof_of_funds_deposit case belongs on its own promoted entity (see gm-14, FinancialRequirement) rather than living_cost_source_basis.kind, which forced TU Munich into creating a second whole CostProfile record just to hold one liquidity figure. living_cost_source_basis.kind is narrowed in V1.2 to {genuine_cost_of_living_estimate, government_minimum_income_threshold, not_published}.

### gm-03: Proof-of-funds vs genuine living cost as separate concepts

- **Institution(s):** TU Delft, TU Munich
- **Problem:** A blocked-account/visa-deposit requirement is neither tuition, nor an ordinary fee, nor real spending money -- forcing it into CostProfile misrepresents it as a cost the student pays away.
- **V1.1 representation:** misleading
- **Affects:** Analyze, Plan, Fund
- **Nature:** recurring
- **Disposition: A -- PROMOTE (see FinancialRequirement, gm-14)**
- **Rationale:** Two independent institutions (TU Delft's IND deposit, TU Munich's Sperrkonto) needed the identical workaround. Meets the multi-institution promotion bar cleanly.

### gm-04: College as optional first-class entity

- **Institution(s):** Oxford (evidenced), Toronto (contradicted)
- **Problem:** Oxford shows material, named, college-to-college hardship-fund and fee variance; Toronto explicitly states colleges do NOT affect tuition/admission/scholarship eligibility at all.
- **V1.1 representation:** n/a (no entity exists)
- **Affects:** Discover, Fund, public University page
- **Nature:** institution-specific
- **Disposition: A -- PROMOTE, OPTIONAL**
- **Rationale:** Genuinely conditional: material at Oxford, immaterial at Toronto. Promoted as an optional entity referenced only where evidence shows it matters (via Scholarship.college_ref / CostProfile.college_ref, both nullable) -- never required, never forced onto every university.

### gm-05: Structured application deadline / external application code

- **Institution(s):** Oxford, Toronto, TU Munich, NYU Abu Dhabi
- **Problem:** No canonical home for UCAS codes, ED/RD deadlines, TUMonline/uni-assist stage identifiers -- lived only in free-text extension_metadata across all four institutions that have any application-platform structure at all.
- **V1.1 representation:** awkward
- **Affects:** Discover, Plan, public University page
- **Nature:** recurring
- **Disposition: A -- PROMOTE (DecisionPlan entity)**
- **Rationale:** Four of five institutions independently needed this. Clears the bar decisively.

### gm-06: CostProfile.estimated_living_costs_monthly_range {min, max, currency}

- **Institution(s):** Oxford
- **Problem:** Oxford publishes a monthly living-cost range, not a single annual figure; V1.1 forces silent annualization or loses the range shape.
- **V1.1 representation:** awkward
- **Affects:** Analyze, Plan
- **Nature:** institution-specific-so-far
- **Disposition: B -- ADD STRUCTURED FIELD**
- **Rationale:** A single institution's evidence, but the fix is a cheap, additive, optional field with no architectural cost -- does not require a new entity, so the bar for adding a field (vs. promoting an entity) is lower than for gm-04/gm-14.

### gm-07: Program.campus_ref optional (nullable)

- **Institution(s):** Oxford
- **Problem:** Oxford required inventing a synthetic 'central campus' Campus record whose own extension_metadata admits it isn't a literal bounded campus, just to satisfy a required foreign key.
- **V1.1 representation:** misleading
- **Affects:** Discover, public University page
- **Nature:** institution-specific-so-far
- **Disposition: B -- MAKE FIELD OPTIONAL**
- **Rationale:** A one-line schema relaxation (required -> optional) that removes a documented fabrication (a fake campus record). Low cost, clear benefit, no new entity needed. Toronto (a genuine single/multi-campus institution) is unaffected since it always had a real campus.

### gm-08: ProgramAward / ProgramPathway (multi-award, multi-duration, integrated continuation)

- **Institution(s):** Oxford (BA -> MCompSci), Toronto (Specialist/Major/Minor)
- **Problem:** A single admission event can lead to more than one degree shape (different duration, different degree_type, different total cost) -- Program's one degree_type/one duration_value cannot represent this, and any total-cost calculation silently scopes to only one shape.
- **V1.1 representation:** impossible (materially: cost range is silently understated)
- **Affects:** Discover, Analyze, Plan, public University page
- **Nature:** recurring
- **Disposition: A -- PROMOTE (ProgramPathway entity)**
- **Rationale:** Two structurally different but conceptually identical failures (integrated master's extension vs. multiple formally-coded majors sharing one admission gate) -- exactly the 'different concrete shapes, same underlying gap' pattern the design guidance asks to validate against multiple institutions before promoting. Both are now validated.

### gm-09: AdmissionStage (generalized staged admission: university/faculty/admission-category/program-of-study/major-declaration/progression/preparatory-pathway/selection)

- **Institution(s):** Toronto (admission-category -> progression), TU Munich (qualification recognition -> aptitude selection -> Studienkolleg), NYU Abu Dhabi (university entry -> later major declaration)
- **Problem:** 'One AdmissionsRequirement per program' is too flat to represent a genuinely multi-step admission/entry process with different timing, evidence, and populations at each step.
- **V1.1 representation:** impossible
- **Affects:** Discover, Analyze, Plan, public University page, verification/audit only
- **Nature:** recurring
- **Disposition: A -- PROMOTE, GENERALIZED**
- **Rationale:** Three structurally different institutions each independently needed a staged model, each proposing overlapping but non-identical entity names (AdmissionStage+ProgressionRequirement at Toronto; ApplicationStage+SelectionProcedure+SelectionCriterion+SelectionStage+QualificationRecognitionPathway at TUM; MajorDeclaration at NYUAD). One generalized AdmissionStage entity with a stage_type enum and an embedded structured criteria[] array represents all three cleanly without creating 6+ overlapping entities -- see gm-10 through gm-13, gm-16 for the specific sub-candidates folded in here.

### gm-10: ProgressionRequirement as its own entity

- **Institution(s):** Toronto
- **Problem:** Continuation-from-first-year-into-program-of-study criteria have different timing/population than initial admission.
- **V1.1 representation:** impossible
- **Affects:** Discover, Plan
- **Nature:** recurring (folded into gm-09)
- **Disposition: B -- FOLD INTO AdmissionStage (stage_type=progression)**
- **Rationale:** Per the design guidance's own instruction to prefer the simpler coherent model: a progression gate is just another stage in the same sequence as university entry and program entry, not a structurally different kind of fact. Modeling it as a stage_type value avoids a second near-duplicate entity.

### gm-11: QualificationRecognitionPathway

- **Institution(s):** TU Munich
- **Problem:** Direct/subject-restricted/Studienkolleg recognition routing is a genuine decision gate that determines whether a student can even reach the aptitude-assessment stage.
- **V1.1 representation:** impossible (lived in extension_metadata)
- **Affects:** Discover, Plan
- **Nature:** institution-specific-so-far (folded into gm-09)
- **Disposition: B -- FOLD INTO AdmissionStage (stage_type=qualification_recognition)**
- **Rationale:** This is structurally just an early-sequence AdmissionStage whose criteria happen to be about curriculum-equivalency rather than grades. No separate entity needed; the generalized stage model already carries applicant_category_ref, so recognition rules that differ by prior curriculum are representable without a bespoke entity.

### gm-12: SelectionProcedure / SelectionCriterion / SelectionStage (points-based aptitude formula)

- **Institution(s):** TU Munich
- **Problem:** TU Munich's Eignungsfeststellungsverfahren is a weighted, multi-stage points formula that a flat academic_threshold string cannot represent.
- **V1.1 representation:** impossible
- **Affects:** Discover, Plan
- **Nature:** institution-specific-so-far (folded into gm-09)
- **Disposition: B -- FOLD INTO AdmissionStage.criteria[] (embedded structured array)**
- **Rationale:** Per the design guidance's explicit instruction: 'avoid three entities if one structured procedure object is sufficient.' AdmissionStage's embedded criteria[] array ({criterion_name, description, threshold_or_formula, weight, mandatory}) represents a weighted points formula without three new top-level entities.

### gm-13: MajorDeclaration

- **Institution(s):** NYU Abu Dhabi
- **Problem:** Students admitted to the university generally, not the program directly; major declared later, with a materially decision-relevant timing dispute between two official sources.
- **V1.1 representation:** impossible (lived in extension_metadata, including an unresolved conflict)
- **Affects:** Discover, Plan
- **Nature:** recurring (folded into gm-09)
- **Disposition: B -- FOLD INTO AdmissionStage (stage_type=major_declaration)**
- **Rationale:** Structurally identical in shape to Toronto's progression stage (a later, timing-bound gate after initial university admission) -- confirms AdmissionStage's generality rather than requiring its own entity.

### gm-14: FinancialRequirement / ImmigrationFinancialRequirement (blocked account, proof of funds)

- **Institution(s):** TU Delft (IND deposit), TU Munich (Sperrkonto)
- **Problem:** A visa-related liquidity requirement is neither tuition, nor a fee, nor genuine living-cost guidance -- forcing it into CostProfile required TU Munich to create an entire second CostProfile record as a workaround.
- **V1.1 representation:** misleading (workaround required a duplicate record)
- **Affects:** Analyze, Plan, Fund
- **Nature:** recurring
- **Disposition: A -- PROMOTE**
- **Rationale:** Two institutions independently needed this and both used the same workaround (living_cost_source_basis.kind=visa_proof_of_funds_deposit, one via a bolt-on kind value, one via a whole duplicate CostProfile). A dedicated FinancialRequirement entity (types: visa_proof_of_funds, blocked_account, government_minimum_resources, enrollment_deposit, other_liquidity_requirement) removes the duplicate-record workaround entirely.

### gm-15: duration_unit: semester

- **Institution(s):** TU Munich
- **Problem:** TU Munich states duration in semesters (6 Semester); V1.1 forced a manual, disclosed-but-lossy semester-to-years conversion (capped SUPPORTED rather than VERIFIED).
- **V1.1 representation:** awkward
- **Affects:** Discover, public University page
- **Nature:** institution-specific-so-far
- **Disposition: B -- ADD ENUM VALUE**
- **Rationale:** Trivial, low-risk addition (duration_unit enum gains 'semesters' alongside 'years'/'months') that removes a disclosed-but-unnecessary conversion step. No architectural cost.

### gm-16: DecisionPlan (ED I / ED II / Regular Decision, binding status, deadlines)

- **Institution(s):** NYU Abu Dhabi, TU Munich (application route), Oxford (UCAS deadline), Toronto (single deadline)
- **Problem:** No canonical way to represent multiple, differently-binding decision plans per program/university with their own deadlines and decision-release dates.
- **V1.1 representation:** impossible
- **Affects:** Discover, Plan, public University page
- **Nature:** recurring (same underlying gap as gm-05)
- **Disposition: A -- PROMOTE**
- **Rationale:** Same evidence base as gm-05; DecisionPlan is the concrete entity design that resolves it. NYUAD gives the richest single case (three named, differently-binding plans).

### gm-17: TestingPolicy / AcceptedAssessment

- **Institution(s):** NYU Abu Dhabi
- **Problem:** 'Test-optional through a named cycle, no minimum score' is a university-wide policy statement, not a per-curriculum admissions requirement -- AdmissionsRequirement.standardized_tests[].required (required/recommended) cannot express a cycle-scoped policy or the difference between 'no minimum' and 'not required at all'.
- **V1.1 representation:** misleading
- **Affects:** Discover, Plan
- **Nature:** institution-specific-so-far
- **Disposition: B -- ADD STRUCTURED FIELD (Program.testing_policy, embedded)**
- **Rationale:** A single institution's evidence, but the underlying shape (a university-wide, cycle-scoped meta-policy layered above per-curriculum test requirements) is plausible at other US-pattern institutions in a future batch. Kept as an embedded object on Program rather than a new top-level entity -- it is never independently referenced or queried outside its one parent Program, satisfying the embedded-object criteria exactly.

### gm-18: FinancialAidPolicy / NeedBasedAid

- **Institution(s):** NYU Abu Dhabi
- **Problem:** Individualized, need-based institutional aid (CSS-Profile-driven, amount varies by demonstrated need) cannot be represented by Scholarship without either fabricating an amount or omitting a real, decision-relevant policy entirely.
- **V1.1 representation:** impossible
- **Affects:** Discover, Analyze, Plan, Fund, public University page, Scholarship page
- **Nature:** institution-specific-so-far, but structurally certain to recur at any US-pattern institution
- **Disposition: A -- PROMOTE**
- **Rationale:** Single institution, but a severe modeling failure that materially affects a student's funding decision and cannot safely stay in extension_metadata -- meets the second promotion criterion explicitly. Every US-pattern private university in a future batch will need this exact concept.

### gm-19: AidApplicationRequirement

- **Institution(s):** NYU Abu Dhabi
- **Problem:** CSS Profile submission, deadlines, and required tax-verification documents for need-based aid.
- **V1.1 representation:** impossible (lived in extension_metadata)
- **Affects:** Plan, Fund
- **Nature:** recurring (folded into gm-18)
- **Disposition: B -- FOLD INTO FinancialAidPolicy.application_requirements[] (embedded, reuses ApplicationRequirement shape)**
- **Rationale:** Same embedded shape as Program.application_requirements[] (gm-05's application-materials side) -- reused rather than duplicated.

### gm-20: Individualized AidPackage (a specific student's award)

- **Institution(s):** NYU Abu Dhabi (explicitly warned against)
- **Problem:** N/A -- this is a deliberate non-candidate.
- **V1.1 representation:** n/a
- **Affects:** verification/audit only
- **Nature:** pipeline-only
- **Disposition: E -- REJECT (belongs in Supabase, not Sanity)**
- **Rationale:** Explicit instruction: Sanity stores public market knowledge; a specific student's personalized aid outcome belongs in Supabase later. Modeling hypothetical individual aid-package records in the public schema would misrepresent unverifiable, non-public, per-student data as market intelligence.

### gm-21: VERIFIED ABSENCE vs UNKNOWN

- **Institution(s):** TU Munich (introduced), NYU Abu Dhabi (heaviest use, 11 absence claims)
- **Problem:** A confirmed 'this does not exist / is not required / is not published' fact was indistinguishable from an unresearched null, both stored as verification_status=UNKNOWN with an ad hoc, schema-informal absence_claim boolean bolted onto VerificationRecord.
- **V1.1 representation:** misleading (an ad hoc field outside the formal schema was required to express it at all)
- **Affects:** Analyze, Plan, verification/audit only
- **Nature:** recurring
- **Disposition: A -- PROMOTE (new verification_status enum value: VERIFIED_ABSENT)**
- **Rationale:** Confirmed across two institutions with the heaviest recurrence of any candidate in this synthesis (15 combined absence claims across TUM+NYUAD). The minimum clean mechanism is one new enum value on the existing verification_status field, not a new entity or a duplicated fact -- satisfies the minimalism test directly ('prefer not to duplicate factual values unnecessarily').

### gm-22: Verification of material extension_metadata

- **Institution(s):** TU Munich (introduced), NYU Abu Dhabi (reinforced)
- **Problem:** Decision-relevant facts temporarily parked in extension_metadata were exempt from the verification-coverage checker's definition of 'material field', letting real facts escape independent verification.
- **V1.1 representation:** acceptable in principle, awkward in enforcement (an ad hoc material_extension_fact boolean was required)
- **Affects:** verification/audit only
- **Nature:** pipeline-only
- **Disposition: A -- PROMOTE (formalize material_extension_fact as a real VerificationRecord field)**
- **Rationale:** Same treatment as gm-21: promote the informal boolean flag used in the TUM/NYUAD runs to an actual, documented, optional field on the VerificationRecord entity, rather than leaving it as an off-schema convention.

### gm-23: Reproducible Sanity generation (no datetime.now())

- **Institution(s):** Oxford (bug found), Toronto/TUM/NYUAD (fix carried forward)
- **Problem:** An earlier transform used wall-clock time in generatedAt, producing a different hash on every run and defeating byte-reproducibility testing.
- **V1.1 representation:** n/a (pipeline code issue, not a schema issue)
- **Affects:** verification/audit only
- **Nature:** pipeline-only
- **Disposition: C -- KEEP AS PERMANENT PIPELINE PRACTICE (not a schema change)**
- **Rationale:** Already fixed and carried forward correctly in every run since Oxford. Documented in 04-pipeline's V1.2 transform script and the QA gate list, not a schema-design matter.

### gm-24: Exact canonical field-path checking (fields_supported)

- **Institution(s):** Oxford (bug found), all subsequent runs
- **Problem:** SourceRecord.fields_supported drifted into noncanonical, made-up dotted paths that didn't correspond to any real schema field.
- **V1.1 representation:** n/a (pipeline QA issue)
- **Affects:** verification/audit only
- **Nature:** pipeline-only
- **Disposition: C -- KEEP AS PERMANENT PIPELINE PRACTICE**
- **Rationale:** check_fields_supported.py already enforces this; V1.2's version (check_fields_supported_v1_2.py) is updated for the new entity/field names but the practice itself is unchanged.

### gm-25: Field-level verification coverage checking

- **Institution(s):** Oxford (introduced), all subsequent runs
- **Problem:** record_status=VERIFIED entities could exist with zero backing field-level VerificationRecords.
- **V1.1 representation:** n/a (pipeline QA issue)
- **Affects:** verification/audit only
- **Nature:** pipeline-only
- **Disposition: C -- KEEP AS PERMANENT PIPELINE PRACTICE**
- **Rationale:** check_verification_coverage.py already enforces this; V1.2's version adds the new entities (AdmissionStage, FinancialRequirement, FinancialAidPolicy, ProgramPathway, College) to its materiality definitions.

### gm-26: BS vs BSc degree_type enum literal

- **Institution(s):** NYU Abu Dhabi
- **Problem:** NYU's own abbreviation is 'BS', not in the V1.1 degree_type enum (which only has 'BSc').
- **V1.1 representation:** acceptable (degree_type_local absorbs the exact wording)
- **Affects:** public University page
- **Nature:** institution-specific
- **Disposition: E -- REJECT (no schema change)**
- **Rationale:** BS and BSc are the same degree, spelled differently by region; degree_type_local already preserves NYU's exact wording verbatim. Adding a second enum literal for the same underlying concept would be enum bloat with no query benefit, failing the minimalism test's 'could this be a structured field instead' question -- it already is one (degree_type_local).

### gm-27: Toronto's 'confirmed-category, unconfirmed-figure' status

- **Institution(s):** Toronto
- **Problem:** A cost category is known to exist and known to differ from a sibling category, but the exact figure could not be read reliably -- currently only expressible as free-text extension_metadata.
- **V1.1 representation:** acceptable (VERIFIED ABSENCE/UNKNOWN distinction from gm-21 now covers this)
- **Affects:** Analyze, verification/audit only
- **Nature:** pipeline-only, minor
- **Disposition: D -- DEFER TO V1.3+**
- **Rationale:** Toronto's own run-summary called this 'logged, minor.' The gm-21 VERIFIED_ABSENT status covers the common case (confirmed absence); a distinct 'confirmed-exists-but-unreadable' status would be a fourth verification_status refinement with only one data point behind it -- defer until a second institution demonstrates the same need.

### gm-28: ApplicationStage / ApplicationRequirement / ApplicationArtifact as three separate top-level entities

- **Institution(s):** TU Munich (proposed), NYU Abu Dhabi (proposed)
- **Problem:** Both runs proposed a 3-4 entity cluster for 'what you submit and when.'
- **V1.1 representation:** impossible
- **Affects:** Discover, Plan
- **Nature:** recurring (resolved via gm-05/gm-16 + structured fields)
- **Disposition: B -- RESOLVED AS: DecisionPlan (entity, gm-16) + Program.application_platform (field) + Program.application_requirements[] (embedded array)**
- **Rationale:** Minimalism pass: three-to-four proposed entities collapse into one promoted entity (DecisionPlan, already justified by gm-05/gm-16) plus two lightweight Program fields. ApplicationArtifact specifically is REJECTED as a fourth entity -- an artifact (STARS record, transcript, essay) is just one row in application_requirements[] with an artifact_type sub-field, not an independently queryable concept.
