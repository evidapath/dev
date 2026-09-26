#!/usr/bin/env python3
"""
EvidaPath pipeline -- V1.2 schema + referential-integrity validator.

Validates a migrated run's records-v1.2.json against the executable
contract at ../02-schema-design/evidapath-schema-v1.2.json, then performs
a separate referential-integrity pass covering every *_ref / source_refs
field across all 19 top-level collections, including the six new V1.2
entity types (College, ProgramPathway, AdmissionStage, DecisionPlan,
FinancialRequirement, FinancialAidPolicy).

This script REJECTS undeclared top-level fields on any entity (the JSON
Schema's additionalProperties: false does this), except inside the
explicit `extension_metadata` object.

Usage:
    python3 validate_normalized_records_v1_2.py <records-v1.2.json> [--schema <schema.json>]

Exit code: 0 if everything passes, 1 if any check fails.
"""
import argparse
import json
import os
import sys

try:
    from jsonschema import Draft7Validator
except ImportError:
    print("ERROR: this validator requires the 'jsonschema' package. Install with:\n"
          "  pip install jsonschema --break-system-packages", file=sys.stderr)
    sys.exit(2)


COLLECTION_TO_ENTITY_TYPE = {
    "countries": "Country", "cities": "City", "universities": "University",
    "campuses": "Campus", "colleges": "College", "programs": "Program",
    "program_pathways": "ProgramPathway", "applicant_categories": "ApplicantCategory",
    "admission_stages": "AdmissionStage", "admissions_requirements": "AdmissionsRequirement",
    "decision_plans": "DecisionPlan", "cost_profiles": "CostProfile",
    "financial_requirements": "FinancialRequirement", "scholarships": "Scholarship",
    "financial_aid_policies": "FinancialAidPolicy", "source_records": "SourceRecord",
    "derived_cost_estimates": "DerivedCostEstimate",
}

# ("target_collection", is_list) per reference field, per collection.
REFERENCE_FIELDS = {
    "cities": {"country_ref": ("countries", False)},
    "universities": {
        "country_ref": ("countries", False), "primary_city_ref": ("cities", False),
        "source_refs": ("source_records", True),
    },
    "campuses": {
        "university_ref": ("universities", False), "city_ref": ("cities", False),
        "country_ref": ("countries", False),
    },
    "colleges": {"university_ref": ("universities", False), "source_refs": ("source_records", True)},
    "programs": {
        "university_ref": ("universities", False), "campus_ref": ("campuses", False),
        "college_ref": ("colleges", False), "source_refs": ("source_records", True),
    },
    "program_pathways": {"program_ref": ("programs", False), "source_refs": ("source_records", True)},
    "applicant_categories": {"university_ref": ("universities", False)},
    "admission_stages": {
        "university_ref": ("universities", False), "program_ref": ("programs", False),
        "applicant_category_ref": ("applicant_categories", False),
        "source_refs": ("source_records", True),
    },
    "admissions_requirements": {
        "program_ref": ("programs", False), "prior_curriculum_category_ref": ("applicant_categories", False),
        "admission_stage_ref": ("admission_stages", False), "source_refs": ("source_records", True),
    },
    "decision_plans": {
        "university_ref": ("universities", False), "program_ref": ("programs", False),
        "source_refs": ("source_records", True),
    },
    "cost_profiles": {
        "program_ref": ("programs", False), "residency_category_ref": ("applicant_categories", False),
        "college_ref": ("colleges", False), "program_pathway_ref": ("program_pathways", False),
        "source_refs": ("source_records", True),
    },
    "financial_requirements": {
        "program_ref": ("programs", False), "residency_category_ref": ("applicant_categories", False),
        "source_refs": ("source_records", True),
    },
    "scholarships": {
        "institutions_covered": ("universities", True), "programs_covered": ("programs", True),
        "college_ref": ("colleges", False), "source_refs": ("source_records", True),
    },
    "financial_aid_policies": {
        "university_ref": ("universities", False), "program_ref": ("programs", False),
        "source_refs": ("source_records", True),
    },
    "derived_cost_estimates": {"cost_profile_ref": ("cost_profiles", False)},
}


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_default_schema_path():
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, "..", "02-schema-design", "evidapath-schema-v1.2.json"),
        os.path.join(here, "evidapath-schema-v1.2.json"),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    tried = "\n  ".join(candidates)
    raise FileNotFoundError(f"Could not find the V1.2 schema file automatically. Tried:\n  {tried}\n"
                             f"Pass --schema <path> explicitly.")


def run_schema_validation(data, schema):
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(map(str, e.path)))
    violations = []
    for err in errors:
        path = list(err.path)
        entity_type, record_id, field = "(top-level)", "(n/a)", "/".join(str(p) for p in path) if path else "(root)"
        if len(path) >= 2 and path[0] in COLLECTION_TO_ENTITY_TYPE:
            collection = path[0]
            entity_type = COLLECTION_TO_ENTITY_TYPE[collection]
            idx = path[1]
            try:
                record_id = data[collection][idx].get("id", f"(index {idx})")
            except Exception:
                record_id = f"(index {idx})"
            field = "/".join(str(p) for p in path[2:]) if len(path) > 2 else "(entire record)"
        reason = err.message
        if "Additional properties are not allowed" in reason:
            reason = f"UNDECLARED FIELD: {reason}"
        violations.append((entity_type, record_id, field, reason))
    return violations


def run_reference_integrity(data):
    violations = []
    id_index = {c: {r.get("id") for r in data.get(c, []) if isinstance(r, dict)} for c in COLLECTION_TO_ENTITY_TYPE}
    for collection, field_map in REFERENCE_FIELDS.items():
        entity_type = COLLECTION_TO_ENTITY_TYPE[collection]
        for rec in data.get(collection, []):
            rec_id = rec.get("id", "(no id)")
            for field, (target_collection, is_list) in field_map.items():
                if field not in rec or rec[field] is None:
                    continue
                refs = rec[field] if is_list else [rec[field]]
                valid_ids = id_index.get(target_collection, set())
                for ref in refs:
                    if ref not in valid_ids:
                        violations.append((entity_type, rec_id, field,
                                            f"reference '{ref}' does not resolve to any "
                                            f"{COLLECTION_TO_ENTITY_TYPE[target_collection]} in this run"))
    return violations


def check_duplicate_ids(data):
    violations, seen = [], {}
    for collection in COLLECTION_TO_ENTITY_TYPE:
        for rec in data.get(collection, []):
            rid = rec.get("id")
            if rid is None:
                continue
            if rid in seen:
                violations.append((COLLECTION_TO_ENTITY_TYPE[collection], rid, "id",
                                    f"duplicate ID also used by {seen[rid]}"))
            else:
                seen[rid] = f"{COLLECTION_TO_ENTITY_TYPE[collection]}:{rid}"
    return violations


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("records_path")
    parser.add_argument("--schema", default=None)
    args = parser.parse_args()

    schema_path = args.schema or resolve_default_schema_path()
    data = load_json(args.records_path)
    schema = load_json(schema_path)

    all_violations = []
    all_violations.extend(run_schema_validation(data, schema))
    all_violations.extend(check_duplicate_ids(data))
    all_violations.extend(run_reference_integrity(data))

    if not all_violations:
        counts = {COLLECTION_TO_ENTITY_TYPE[c]: len(data.get(c, [])) for c in COLLECTION_TO_ENTITY_TYPE}
        print("PASS: schema validation, duplicate-ID check, and reference-integrity check all clean.")
        print("Entity counts:")
        for entity_type, count in counts.items():
            print(f"  {entity_type}: {count}")
        sys.exit(0)
    else:
        print(f"FAIL: {len(all_violations)} violation(s) found.\n")
        print(f"{'entity':<20} {'record ID':<50} {'field':<35} reason")
        print("-" * 150)
        for entity_type, record_id, field, reason in all_violations:
            print(f"{entity_type:<20} {str(record_id):<50} {field:<35} {reason}")
        sys.exit(1)


if __name__ == "__main__":
    main()
