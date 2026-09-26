# TU Delft: V1.1 → V1.2 migration report

## Special note: this is a pre-V1.1 migration, not a V1.1-to-V1.2 migration

TU Delft's `records.json` predates the V1.1 hardening pass entirely. It has no `schema_version`, no `run_id` object, no `derived_cost_estimates` array, and its `source_records` field is a **string** ("see 01-research/sources.json") rather than an array of `SourceRecord` objects. It also uses several non-canonical field names never present in the V1.1 schema (`Program.total_credits`, `Program.language_notes`, `AdmissionsRequirement.standardized_tests[].required_or_recommended`). Validating this file against `evidapath-schema-v1.1.json` would fail outright. This migration therefore performs a single combined pass: pre-V1.1 ad hoc shape → V1.1-canonical shape → V1.2 additions, all at once, since no intermediate V1.1-conformant artifact for TU Delft has ever existed.

## ID stability

No canonical ID changed. `nl-tu-delft`, `nl-delft`, `nl-tu-delft-main`, `nl-tu-delft-bsc-computer-science-engineering`, all seven `ApplicantCategory` IDs, all four `AdmissionsRequirement` IDs, both `CostProfile` IDs, and both `Scholarship` IDs are identical to the source file. No `v1.1-to-v1.2-id-remap.json` is produced for this institution.

## Structural fixes applied

1. **`source_records`**: the V1.1 file's string placeholder was resolved by loading the actual `01-research/sources.json` (10 sources) and materializing it as a proper `SourceRecord` array. Each source's `retrieved_at` was normalized from date-only (`"2026-09-22"`, the pilot run's own disclosed capture limitation) to a full ISO 8601 timestamp (`"2026-09-22T00:00:00Z"`) to satisfy V1.2's `iso_datetime` format — no new information was added, only a time-of-day placeholder appended to an already-known date, and this normalization is disclosed here rather than silently applied.
1a. **`SourceRecord.fields_supported` convention normalized**: TU Delft's pre-V1.1 sources used record-ID-prefixed entries (e.g. `"ar-nl-tu-delft-cse-dutch-vwo.curriculum_type"`) rather than the `"EntityType.field"` convention V1.1 standardized and V1.2's `check_fields_supported_v1_2.py` enforces. Each entry was normalized to the canonical form (e.g. `"AdmissionsRequirement.curriculum_type (ar-nl-tu-delft-cse-dutch-vwo)"`), preserving the original record ID as a parenthetical annotation so no identifying detail is lost. All 10 `SourceRecord`s now pass `check_fields_supported_v1_2.py` cleanly.
2. **`Program.total_credits`, `Program.language_notes`**: not canonical V1.1 or V1.2 fields. Relocated unchanged into `Program.extension_metadata.fields` with a note explaining the relocation. No data lost.
3. **`AdmissionsRequirement.standardized_tests[].required_or_recommended`**: renamed to the canonical field name `required` (same value, `"required"`) on the one record that used it (`ar-nl-tu-delft-cse-us-ap`).
4. **`University.last_verified: null`**: V1.1's schema technically required a string here; TU Delft's own pre-hardening data already violated this (the record's `record_status` is `STRUCTURED`, meaning it was never independently verified, so no verification date exists). Rather than fabricate a date, V1.2's `University.last_verified` field was corrected to be nullable (`["string", "null"]`) — a small, general schema fix, not a TU-Delft-specific workaround, since "not yet verified" is a legitimate state for any institution's record.
5. **`AdmissionsRequirement.notes: null`** (on `ar-nl-tu-delft-cse-us-ap`): normalized to an empty string `""`. This is a data-cleanup normalization (the field means "no additional notes"), not a schema change, since `notes` is descriptive text elsewhere in the schema and does not carry meaningful-absence semantics the way a numeric/threshold field does.

## V1.2 additions

- **`AdmissionStage`** (1 new record, `nl-tu-delft-stage-matching-selection`): TU Delft's numerus fixus "Matching & Selection procedure" was previously only described in `AdmissionsRequirement.notes` free text across all four curriculum records. It is now a first-class `AdmissionStage` (`stage_type: selection_stage`), and all four `AdmissionsRequirement` records gained an `admission_stage_ref` pointing to it. This is a genuine, real fact being restructured, not new information.
- **`DecisionPlan`** (1 new record, `nl-tu-delft-decisionplan-numerus-fixus`): the January 15 numerus fixus registration deadline, previously buried in `AdmissionsRequirement.notes`, is now a structured `DecisionPlan` (`plan_type: single_stage`).
- **`FinancialRequirement`** (1 new record, `nl-tu-delft-finreq-ind-proof-of-funds`): the Dutch IND proof-of-funds deposit (EUR 14,200/year), previously represented as `CostProfile.estimated_living_costs_annual` with `living_cost_source_basis.kind: visa_proof_of_funds_deposit` (a V1.1 workaround explicitly flagged as misleading in the original run), is now a dedicated `FinancialRequirement` (`requirement_type: visa_proof_of_funds`, `refundable: true`). The corresponding `CostProfile` (`cp-nl-tu-delft-cse-2026-27-non-eu`) had its `estimated_living_costs_annual` and `living_cost_source_basis` fields cleared to `null` / `not_published`, since TU Delft does not publish a separate genuine cost-of-living estimate for non-EU students. **No source fact was deleted** — the EUR 14,200 figure, its currency, and its full sourcing (`src-02`) now live in the `FinancialRequirement` record instead.

## Unmapped facts

None. Every field present in the V1.1-shaped source record has a home in V1.2: either an unchanged canonical field, a relocated `extension_metadata` entry, or a newly promoted structured entity.

## Verification coverage carried forward

No new verification claims were introduced by this migration; the relocated `FinancialRequirement` record's `verification_status: VERIFIED` and `source_refs: ["src-02"]` are inherited directly from the `CostProfile` record it was extracted from. The new `AdmissionStage` and `DecisionPlan` records are conservatively marked `SUPPORTED` / `STRUCTURED`, reflecting that the underlying facts were previously only `SUPPORTED`-level free text, not independently re-verified during this synthesis pass (per the user's instruction that this is a migration job, not a new research job).

## Validation result

`records-v1.2.json` validates cleanly against `evidapath-schema-v1.2.json` (0 errors) — confirmed via `04-pipeline/validate_normalized_records_v1_2.py` (see `04-pipeline/` for the full QA run).

## VerificationRecord formalization

`verification-records-v1.2.json` in this folder carries forward the original V1.1 run's field-level `VerificationRecord`s, reformatted to the V1.2 schema: any record with the informal `absence_claim: true` flag had its `verification_status` promoted to the now-formal `VERIFIED_ABSENT` enum value; `material_extension_fact` is preserved as the now-formal schema field (unchanged in meaning); any NYUAD-run-specific informal semantic-QA flags (`financial_aid_semantic_reviewed`, `holistic_admissions_semantic_reviewed` -- not part of the V1.2 schema) were folded into `conflict_or_limitation_notes` as a bracketed annotation. This is a reformatting pass only -- no field-level claim was added, removed, or re-verified.
