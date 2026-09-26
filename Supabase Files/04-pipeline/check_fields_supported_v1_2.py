#!/usr/bin/env python3
"""
EvidaPath pipeline -- V1.2 semantic QA check for SourceRecord.fields_supported.

Checks every SourceRecord.fields_supported entry in a migrated run's
records-v1.2.json against the canonical entity/field names in the
executable V1.2 schema, extended to recognize the six new V1.2 entity
types. An entry is accepted if it is one of:

  1. "<EntityType>.<canonical_field_name>[...]"   -- a real V1.2 schema field
  2. "<EntityType>.extension_metadata.fields.<key>[...]" -- a documented
     extension fact (always allowed)
  3. A line starting with "SCHEMA-GAP EVIDENCE ONLY" -- an explicit,
     honest declaration that a source supports a schema-gap observation
     rather than a normalized field (legitimate, not flagged)

Only the FIRST whitespace-delimited token of each fields_supported string
is checked; everything after the first space is a free-text annotation.

Usage:
    python3 check_fields_supported_v1_2.py <records-v1.2.json> [--schema <schema.json>]

Exit code: 0 if every entry is canonical, 1 if any entry is flagged.
"""
import argparse
import json
import os
import sys

KEY_TO_ENTITY = {
    "country": "Country", "city": "City", "university": "University", "campus": "Campus",
    "college": "College", "program": "Program", "program_pathway": "ProgramPathway",
    "applicant_category": "ApplicantCategory", "admission_stage": "AdmissionStage",
    "admissions_requirement": "AdmissionsRequirement", "decision_plan": "DecisionPlan",
    "cost_profile": "CostProfile", "financial_requirement": "FinancialRequirement",
    "scholarship": "Scholarship", "financial_aid_policy": "FinancialAidPolicy",
    "source_record": "SourceRecord", "verification_record": "VerificationRecord",
    "change_record": "ChangeRecord", "derived_cost_estimate": "DerivedCostEstimate",
}


def entity_field_names(schema):
    defs = schema["$defs"]
    result = {}
    for def_key, entity_name in KEY_TO_ENTITY.items():
        props = defs.get(def_key, {}).get("properties", {})
        result[entity_name] = set(props.keys())
    return result


def resolve_default_schema_path():
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, "..", "02-schema-design", "evidapath-schema-v1.2.json"),
        os.path.join(here, "evidapath-schema-v1.2.json"),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    raise FileNotFoundError("Could not find evidapath-schema-v1.2.json automatically; pass --schema.")


def check(records_path, schema_path):
    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)
    entity_fields = entity_field_names(schema)
    entity_names = set(entity_fields.keys())

    with open(records_path, encoding="utf-8") as f:
        data = json.load(f)
    source_records = data.get("source_records", [])

    violations = []
    for rec in source_records:
        src_id = rec.get("id", "(no id)")
        for entry in rec.get("fields_supported", []):
            if entry.startswith("SCHEMA-GAP EVIDENCE ONLY"):
                continue
            token = entry.split(" ", 1)[0]
            if "." not in token:
                violations.append((src_id, entry, "no 'EntityType.field' token found"))
                continue
            entity_part, field_part = token.split(".", 1)
            if entity_part not in entity_names:
                violations.append((src_id, entry, f"'{entity_part}' is not a canonical V1.2 entity type"))
                continue
            top_field = field_part.split(".", 1)[0]
            if top_field == "extension_metadata":
                continue
            if top_field not in entity_fields[entity_part]:
                violations.append((src_id, entry, f"'{entity_part}.{top_field}' is not a canonical field of {entity_part} in V1.2"))
    return violations, len(source_records)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("records_path")
    parser.add_argument("--schema", default=None)
    args = parser.parse_args()

    schema_path = args.schema or resolve_default_schema_path()
    violations, n_sources = check(args.records_path, schema_path)

    if not violations:
        print(f"PASS: every fields_supported entry across {n_sources} SourceRecords is a canonical V1.2 "
              f"field path, a documented extension_metadata path, or an explicit SCHEMA-GAP EVIDENCE ONLY marker.")
        sys.exit(0)
    else:
        print(f"FAIL: {len(violations)} non-canonical fields_supported entr(y/ies) found.\n")
        print(f"{'source ID':<12} {'entry':<90} reason")
        print("-" * 160)
        for src_id, entry, reason in violations:
            print(f"{src_id:<12} {entry[:88]:<90} {reason}")
        sys.exit(1)


if __name__ == "__main__":
    main()
