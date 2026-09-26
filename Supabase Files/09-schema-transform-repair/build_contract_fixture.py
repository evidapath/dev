#!/usr/bin/env python3
"""
Build a small, referentially self-contained fixture from EXISTING five-school
V1.2 data (no new research, no synthetic records) that deliberately exercises
every Sanity serialization scenario called for in the V1.2 -> Sanity contract
work: scalars, optional/missing values, arrays of strings, arrays of embedded
objects, arrays of references, nested objects, extension_metadata with and
without content, a VERIFIED record, a HUMAN_REVIEW/CONFLICT record, a
verified-absence record, a range value, and multi-reference chains.

Method: pick a small, deliberate seed set of real record IDs (chosen by hand
below, with the reasoning for each), then compute the REFERENCE CLOSURE of
that seed set against the real five-school data (so the fixture is not just
small, but self-contained -- every reference inside it resolves to another
document also inside it, exactly like the real dataset), then write that
closure out as fixture-scoped records-v1.2.json / verification-records-v1.2.json
files with the exact same shape the real per-institution files have, so the
REAL pipeline scripts (normalized_to_sanity_ndjson_v1_2.py,
resolve_references.py) can run against the fixture completely unmodified.

Usage:
    python3 build_contract_fixture.py --source-dir ../03-migrated-runs --out fixture/source
"""
import argparse
import json
import os
import sys

# Mirrors 04-pipeline/normalized_to_sanity_ndjson_v1_2.py's own tables --
# duplicated here (not imported) so this fixture-builder has zero coupling to
# the pipeline module's internals beyond the two scripts it actually shells
# out to.
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
ENTITY_TYPE_TO_COLLECTION = {v: k for k, v in COLLECTION_TO_ENTITY_TYPE.items()}
ENTITY_TYPE_TO_COLLECTION["VerificationRecord"] = "verification_records"

SIMPLE_REF_FIELDS = {
    "country_ref": "Country", "primary_city_ref": "City", "city_ref": "City",
    "university_ref": "University", "campus_ref": "Campus", "college_ref": "College",
    "program_ref": "Program", "program_pathway_ref": "ProgramPathway",
    "prior_curriculum_category_ref": "ApplicantCategory", "residency_category_ref": "ApplicantCategory",
    "applicant_category_ref": "ApplicantCategory", "admission_stage_ref": "AdmissionStage",
    "cost_profile_ref": "CostProfile",
}
LIST_REF_FIELDS = {"source_refs": "SourceRecord"}
POLYMORPHIC_REF_FIELDS = {"record_ref", "source_ref"}
INSTITUTION_SCOPED_TYPES = {"SourceRecord", "VerificationRecord"}

# ---------------------------------------------------------------------------
# Seed set -- every ID below was chosen by hand for a specific reason. This
# IS the scenario-coverage argument; see final-repair-report.md / the
# contract doc for how each maps to a required fixture scenario.
# ---------------------------------------------------------------------------
SEEDS = [
    # institution, collection, id, why
    ("ae-nyu-abu-dhabi", "countries", "ae", "core entity; extension_metadata w/ EMPTY fields+note"),
    ("ae-nyu-abu-dhabi", "cities", "ae-abu-dhabi", "core entity; simple reference (country_ref)"),
    ("ae-nyu-abu-dhabi", "universities", "ae-nyu-abu-dhabi", "core entity; multiple references (country_ref, primary_city_ref)"),
    ("ae-nyu-abu-dhabi", "campuses", "ae-nyu-abu-dhabi-saadiyat", "multiple references (university_ref, city_ref, country_ref)"),
    ("ae-nyu-abu-dhabi", "programs", "ae-nyu-abu-dhabi-computer-science-bs",
     "array of embedded objects (application_requirements), nested single object "
     "containing its own array of embedded objects + array of plain-string refs "
     "(testing_policy.accepted_assessments / .source_refs), extension_metadata WITH content"),
    ("ae-nyu-abu-dhabi", "applicant_categories", "ae-nyu-abu-dhabi-curriculum-a-level",
     "ApplicantCategory, dimension=prior_curriculum"),
    ("ae-nyu-abu-dhabi", "applicant_categories", "ae-nyu-abu-dhabi-residency-uniform",
     "ApplicantCategory, dimension=residency_citizenship (both dimensions covered)"),
    ("ae-nyu-abu-dhabi", "admission_stages", "ae-nyu-abu-dhabi-stage-major-declaration",
     "array of embedded objects (criteria); genuine domain state HUMAN_REVIEW/CONFLICT"),
    ("ae-nyu-abu-dhabi", "admissions_requirements", "admreq-a-level",
     "array of embedded objects (language_requirements), array of strings that is "
     "empty-not-missing (required_subjects: [] = verified absence), extension_metadata "
     "WITH content, optional scalar genuinely null (academic_threshold)"),
    ("gb-university-of-oxford", "program_pathways", "gb-university-of-oxford-pathway-mcompsci",
     "ProgramPathway (NYUAD has none in this dataset)"),
    ("ae-nyu-abu-dhabi", "cost_profiles", "cost-uniform", "CostProfile, single-residency-tier institution"),
    ("gb-university-of-oxford", "cost_profiles", "gb-university-of-oxford-cost-home",
     "CostProfile with a populated range value (estimated_living_costs_monthly_range)"),
    ("gb-university-of-oxford", "financial_requirements", "gb-university-of-oxford-finreq-visa-maintenance",
     "extension_metadata.fields containing a NESTED OBJECT value (visa_maintenance_monthly_range) "
     "as well as a plain string value (oxford_region_classification, itself UNCONFIRMED) -- "
     "exercises the value_type='json' vs 'string' branch of the entry transform in one document"),
    ("ae-nyu-abu-dhabi", "scholarships", "ae-sheikh-mohamed-bin-zayed-nyuad-scholarship",
     "genuine domain state HUMAN_REVIEW/SUPPORTED, and its own VerificationRecord is CONFLICT"),
    ("ae-nyu-abu-dhabi", "financial_aid_policies", "ae-nyu-abu-dhabi-finaid-need-based",
     "FinancialAidPolicy with its own array of embedded objects (application_requirements)"),
    ("ae-nyu-abu-dhabi", "verification_records", "vr-12", "VerificationRecord, CONFLICT, blocking"),
    ("ae-nyu-abu-dhabi", "verification_records", "vr-20", "VerificationRecord, VERIFIED_ABSENT"),
    ("ae-nyu-abu-dhabi", "verification_records", "vr-30", "VerificationRecord, VERIFIED"),
    ("ae-nyu-abu-dhabi", "verification_records", "vr-31", "VerificationRecord, CONFLICT, blocking"),
    ("ae-nyu-abu-dhabi", "verification_records", "vr-34", "VerificationRecord, VERIFIED_ABSENT"),
]


def load_all(source_dir):
    data = {}
    for inst in os.listdir(source_dir):
        rp = os.path.join(source_dir, inst, "records-v1.2.json")
        vp = os.path.join(source_dir, inst, "verification-records-v1.2.json")
        if not os.path.isfile(rp):
            continue
        with open(rp, encoding="utf-8") as f:
            records = json.load(f)
        vrecs = {"verification_records": []}
        if os.path.isfile(vp):
            with open(vp, encoding="utf-8") as f:
                vrecs = json.load(f)
        data[inst] = {"records": records, "verification": vrecs}
    return data


def find_record(data, institution, collection, rec_id):
    if collection == "verification_records":
        for r in data[institution]["verification"].get("verification_records", []):
            if r.get("id") == rec_id:
                return r
    else:
        for r in data[institution]["records"].get(collection, []):
            if r.get("id") == rec_id:
                return r
    return None


def find_record_anywhere(data, collection, rec_id):
    """Non-institution-scoped types have globally unique IDs -- search every
    institution's data for the owner."""
    for inst in data:
        r = find_record(data, inst, collection, rec_id)
        if r is not None:
            return inst, r
    return None, None


def extract_refs(node):
    """Recursively yields (entity_type, id_or_ids) for every ref-shaped field
    found anywhere in the tree, mirroring resolve_references.py's own
    recursive walk and field tables exactly."""
    if isinstance(node, dict):
        for field, entity_type in SIMPLE_REF_FIELDS.items():
            v = node.get(field)
            if isinstance(v, str):
                yield entity_type, v
        for field, entity_type in LIST_REF_FIELDS.items():
            v = node.get(field)
            if isinstance(v, list):
                for item in v:
                    if isinstance(item, str):
                        yield entity_type, item
        for field in POLYMORPHIC_REF_FIELDS:
            v = node.get(field)
            if isinstance(v, str) and ":" in v:
                et, rid = v.split(":", 1)
                yield et, rid
        for v in node.values():
            yield from extract_refs(v)
    elif isinstance(node, list):
        for item in node:
            yield from extract_refs(item)


def compute_closure(data, seeds):
    closure = set()  # (institution, collection, id)
    queue = list(seeds)
    while queue:
        institution, collection, rec_id = queue.pop()
        key = (institution, collection, rec_id)
        if key in closure:
            continue
        rec = find_record(data, institution, collection, rec_id)
        if rec is None:
            print(f"WARNING: seed/dependency not found: {key}", file=sys.stderr)
            continue
        closure.add(key)
        for entity_type, target_id in extract_refs(rec):
            target_collection = ENTITY_TYPE_TO_COLLECTION[entity_type]
            if entity_type in INSTITUTION_SCOPED_TYPES:
                # Locally-scoped ID (e.g. "src-01") -- always resolved against
                # THIS record's own institution, same rule resolve_references.py uses.
                queue.append((institution, target_collection, target_id))
            else:
                owner_inst, target_rec = find_record_anywhere(data, target_collection, target_id)
                if owner_inst is None:
                    print(f"WARNING: dangling reference from {key} to "
                          f"{entity_type}:{target_id} -- not found in any institution", file=sys.stderr)
                    continue
                queue.append((owner_inst, target_collection, target_id))
    return closure


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", default="../03-migrated-runs")
    parser.add_argument("--out", default="fixture/source")
    args = parser.parse_args()

    data = load_all(args.source_dir)
    seeds = [(inst, coll, rid) for inst, coll, rid, _why in SEEDS]
    closure = compute_closure(data, seeds)

    by_institution = {}
    for inst, coll, rid in closure:
        by_institution.setdefault(inst, {}).setdefault(coll, []).append(rid)

    os.makedirs(args.out, exist_ok=True)
    total = 0
    per_type_counts = {}
    for inst, colls in sorted(by_institution.items()):
        inst_dir = os.path.join(args.out, inst)
        os.makedirs(inst_dir, exist_ok=True)

        src_records = data[inst]["records"]
        out_records = {"run_id": src_records.get("run_id", inst), "schema_version": src_records.get("schema_version", "1.2")}
        for coll in COLLECTION_TO_ENTITY_TYPE:
            # Every collection key is required at the top level of
            # records-v1.2.json (confirmed against the JSON Schema's own
            # root `required` list) even when empty -- so every collection
            # is always written, `[]` when this fixture selected nothing
            # from it, exactly matching the real per-institution files'
            # shape rather than a bespoke fixture-only shape.
            ids_wanted = set(colls.get(coll, []))
            items = [r for r in src_records.get(coll, []) if r.get("id") in ids_wanted]
            out_records[coll] = items
            total += len(items)
            et = COLLECTION_TO_ENTITY_TYPE[coll]
            per_type_counts[et] = per_type_counts.get(et, 0) + len(items)
        with open(os.path.join(inst_dir, "records-v1.2.json"), "w", encoding="utf-8") as f:
            json.dump(out_records, f, indent=2, sort_keys=True)

        # Always written, even empty, matching every real per-institution
        # verification-records-v1.2.json file's shape.
        vr_ids_wanted = set(colls.get("verification_records", []))
        src_vr = data[inst]["verification"]
        vr_items = [r for r in src_vr.get("verification_records", []) if r.get("id") in vr_ids_wanted]
        with open(os.path.join(inst_dir, "verification-records-v1.2.json"), "w", encoding="utf-8") as f:
            json.dump({"verification_records": vr_items}, f, indent=2, sort_keys=True)
        total += len(vr_items)
        per_type_counts["VerificationRecord"] = per_type_counts.get("VerificationRecord", 0) + len(vr_items)

    print(f"Fixture closure: {total} source records across {len(by_institution)} institution(s).")
    for et, c in sorted(per_type_counts.items()):
        print(f"  {et}: {c}")
    print(f"Written to {args.out}/")


if __name__ == "__main__":
    main()
