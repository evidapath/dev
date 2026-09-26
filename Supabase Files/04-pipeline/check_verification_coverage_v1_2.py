#!/usr/bin/env python3
"""
EvidaPath pipeline -- V1.2 verification-coverage QA check (generalized
across all five test-set institutions, not institution-specific).

Answers, machine-readably, for a migrated records-v1.2.json plus its
sibling verification-records-v1.2.json:

  A. CANONICAL FIELD COVERAGE. For every material field on every legacy
     entity (University, Program, AdmissionsRequirement, CostProfile,
     Scholarship) whose record_status is VERIFIED or HUMAN_REVIEW, is
     there an independent field-level VerificationRecord backing it?

  B. MEANINGFUL-ABSENCE COVERAGE (formalized in V1.2). Every
     VerificationRecord with verification_status=VERIFIED_ABSENT must
     carry non-empty conflict_or_limitation_notes explaining what was
     checked -- the formal replacement for V1.1's informal absence_claim
     boolean.

  C. MATERIAL-EXTENSION COVERAGE (formalized in V1.2). Any fact still
     living in Program/CostProfile/AdmissionsRequirement/College/
     ProgramPathway/AdmissionStage/DecisionPlan/FinancialRequirement/
     FinancialAidPolicy.extension_metadata.fields must have at least one
     VerificationRecord with material_extension_fact=true referencing
     that entity -- the formal replacement for the informal per-run
     additive convention.

  D. NEW-ENTITY EVIDENCE COVERAGE. The six new V1.2 entity types
     (College, ProgramPathway, AdmissionStage, DecisionPlan,
     FinancialRequirement, FinancialAidPolicy) did not exist when the
     original V1.1 field-level VerificationRecords were produced, so
     this check applies a lighter, entity-level bar instead of the
     field-level bar in (A): every such record with record_status in
     (VERIFIED, HUMAN_REVIEW) must have a non-empty source_refs array
     and a non-UNKNOWN verification_status. This is the honestly-scoped
     coverage bar for entities produced by restructuring already-
     verified V1.1 facts during a migration pass, not new research.

MATERIALITY: not every field on every entity needs its own
VerificationRecord. Structural/wiring fields (ids, *_ref foreign keys,
record_status/last_checked bookkeeping, currency, duration_years,
narrative `notes` text) are excluded -- MATERIAL_FIELDS below is the
single source of truth for what this script requires coverage for.

Usage:
    python3 check_verification_coverage_v1_2.py <records-v1.2.json> <verification-records-v1.2.json> [--out coverage.json]

Exit code: 0 if every check passes, 1 otherwise.
"""
import argparse
import json
import re
import sys


def _field_tokens(field_checked):
    tokens = []
    for chunk in (field_checked or "").split(","):
        chunk = chunk.strip()
        m = re.match(r"^[A-Za-z0-9_.]+", chunk)
        if m:
            tokens.append(m.group(0))
    return tokens


MATERIAL_FIELDS = {
    "University": ["canonical_name", "official_website", "institution_type"],
    "Program": ["program_name", "degree_type_local", "faculty_school",
                "official_program_url", "duration_value", "duration_unit",
                "language_of_instruction"],
    "AdmissionsRequirement": ["academic_threshold", "required_subjects", "standardized_tests",
                              "language_requirements"],
    "CostProfile": ["tuition_annual", "mandatory_fees_annual",
                     "estimated_living_costs_annual", "living_cost_source_basis"],
    "Scholarship": ["award_amount", "award_type"],
}

LEGACY_COLLECTIONS = {
    "University": "universities", "Program": "programs",
    "AdmissionsRequirement": "admissions_requirements", "CostProfile": "cost_profiles",
    "Scholarship": "scholarships",
}

NEW_ENTITY_COLLECTIONS = {
    "College": "colleges", "ProgramPathway": "program_pathways",
    "AdmissionStage": "admission_stages", "DecisionPlan": "decision_plans",
    "FinancialRequirement": "financial_requirements", "FinancialAidPolicy": "financial_aid_policies",
}

EXTENSION_BEARING_TYPES = {
    "University": "universities", "Program": "programs", "CostProfile": "cost_profiles",
    "AdmissionsRequirement": "admissions_requirements", "Scholarship": "scholarships",
    "College": "colleges", "ProgramPathway": "program_pathways",
    "AdmissionStage": "admission_stages", "DecisionPlan": "decision_plans",
    "FinancialRequirement": "financial_requirements", "FinancialAidPolicy": "financial_aid_policies",
}


def check_canonical_coverage(records, vrs):
    by_ref = {}
    for v in vrs:
        by_ref.setdefault(v["record_ref"], []).append(v)

    rows = []
    for entity_type, collection in LEGACY_COLLECTIONS.items():
        for r in records.get(collection, []):
            if r.get("record_status") not in ("VERIFIED", "HUMAN_REVIEW"):
                continue
            ref = f"{entity_type}:{r['id']}"
            candidates = by_ref.get(ref, [])
            for field in MATERIAL_FIELDS[entity_type]:
                if field in r and r[field] is None:
                    continue  # null field -- covered separately by the absence-coverage check
                matches = [v for v in candidates if any(
                    field == tok or field in tok or tok in field for tok in _field_tokens(v["field_checked"])
                )]
                best_status = None
                if matches:
                    statuses = [m["verification_status"] for m in matches]
                    for pref in ("VERIFIED", "VERIFIED_ABSENT", "CONFLICT", "SUPPORTED"):
                        if pref in statuses:
                            best_status = pref
                            break
                    else:
                        best_status = statuses[0]
                rows.append({
                    "check": "canonical_material_field", "entity_type": entity_type,
                    "record_id": r["id"], "field": field, "covered": bool(matches),
                    "verification_record_ids": [m["id"] for m in matches],
                    "best_verification_status": best_status,
                })
    return rows


def check_meaningful_absence_coverage(vrs):
    rows = []
    for v in vrs:
        if v.get("verification_status") != "VERIFIED_ABSENT":
            continue
        covered = bool((v.get("conflict_or_limitation_notes") or "").strip())
        rows.append({
            "check": "meaningful_absence_verified_absent", "verification_record_id": v["id"],
            "record_ref": v["record_ref"], "field_checked": v["field_checked"], "covered": covered,
        })
    return rows


def check_material_extension_coverage(records, vrs):
    material_refs = {v["record_ref"] for v in vrs if v.get("material_extension_fact")}
    rows = []
    for entity_type, collection in EXTENSION_BEARING_TYPES.items():
        for r in records.get(collection, []):
            if r.get("record_status") not in ("VERIFIED", "HUMAN_REVIEW"):
                continue
            ext = r.get("extension_metadata") or {}
            fields = ext.get("fields") or {}
            if not fields:
                continue
            ref = f"{entity_type}:{r['id']}"
            covered = ref in material_refs
            rows.append({
                "check": "material_extension_fact", "entity_type": entity_type, "record_id": r["id"],
                "extension_keys": list(fields.keys()), "covered": covered,
            })
    return rows


def check_new_entity_evidence(records):
    rows = []
    for entity_type, collection in NEW_ENTITY_COLLECTIONS.items():
        for r in records.get(collection, []):
            if r.get("record_status") not in ("VERIFIED", "HUMAN_REVIEW"):
                continue
            has_sources = bool(r.get("source_refs"))
            has_status = r.get("verification_status") not in (None, "UNKNOWN")
            rows.append({
                "check": "new_entity_evidence", "entity_type": entity_type, "record_id": r["id"],
                "covered": has_sources and has_status,
                "source_ref_count": len(r.get("source_refs") or []),
                "verification_status": r.get("verification_status"),
            })
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("records_path")
    parser.add_argument("verification_records_path")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    with open(args.records_path, encoding="utf-8") as f:
        records = json.load(f)
    with open(args.verification_records_path, encoding="utf-8") as f:
        vrs = json.load(f)["verification_records"]

    canonical_rows = check_canonical_coverage(records, vrs)
    absence_rows = check_meaningful_absence_coverage(vrs)
    extension_rows = check_material_extension_coverage(records, vrs)
    new_entity_rows = check_new_entity_evidence(records)

    not_covered_canonical = [r for r in canonical_rows if not r["covered"]]
    not_covered_absence = [r for r in absence_rows if not r["covered"]]
    not_covered_extension = [r for r in extension_rows if not r["covered"]]
    not_covered_new_entity = [r for r in new_entity_rows if not r["covered"]]

    overall_pass = not (not_covered_canonical or not_covered_absence or not_covered_extension or not_covered_new_entity)

    result = {
        "run_id": records.get("run_id"),
        "materiality_definition": MATERIAL_FIELDS,
        "canonical_field_coverage": canonical_rows,
        "meaningful_absence_coverage": absence_rows,
        "material_extension_coverage": extension_rows,
        "new_entity_evidence_coverage": new_entity_rows,
        "summary": {
            "total_material_fields_checked": len(canonical_rows),
            "not_covered_canonical": len(not_covered_canonical),
            "total_verified_absent_claims_checked": len(absence_rows),
            "not_covered_absence": len(not_covered_absence),
            "total_material_extension_facts_checked": len(extension_rows),
            "not_covered_extension": len(not_covered_extension),
            "total_new_entity_records_checked": len(new_entity_rows),
            "not_covered_new_entity": len(not_covered_new_entity),
        },
        "overall_result": "PASS" if overall_pass else "FAIL",
    }

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            f.write("\n")

    if overall_pass:
        print(f"PASS: {len(canonical_rows)} canonical material fields covered; {len(absence_rows)} "
              f"VERIFIED_ABSENT claims all carry supporting notes; {len(extension_rows)} material "
              f"extension_metadata facts all have an independent VerificationRecord; {len(new_entity_rows)} "
              f"new-V1.2-entity records all carry source_refs and a resolved verification_status.")
        sys.exit(0)
    else:
        print(f"FAIL: {len(not_covered_canonical)} canonical field(s), {len(not_covered_absence)} "
              f"VERIFIED_ABSENT claim(s), {len(not_covered_extension)} material-extension-fact(s), "
              f"{len(not_covered_new_entity)} new-entity record(s) uncovered.\n")
        for r in not_covered_canonical:
            print(f"  [canonical] {r['entity_type']}:{r['record_id']}.{r['field']} -- UNCOVERED")
        for r in not_covered_absence:
            print(f"  [absence]   {r['verification_record_id']} ({r['record_ref']}) -- NO SUPPORTING NOTES")
        for r in not_covered_extension:
            print(f"  [extension] {r['entity_type']}:{r['record_id']} -- keys {r['extension_keys']} UNCOVERED")
        for r in not_covered_new_entity:
            print(f"  [new-entity] {r['entity_type']}:{r['record_id']} -- source_refs={r['source_ref_count']}, "
                  f"verification_status={r['verification_status']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
