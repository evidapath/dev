#!/usr/bin/env python3
"""
Resolve canonical-ID string references in the EvidaPath V1.2 Sanity draft
NDJSON into native Sanity `{_type: "reference", _ref: "..."}` objects.

WHY THIS EXISTS: normalized_to_sanity_ndjson_v1_2.py (04-pipeline/) copies
every `*_ref` field straight from records-v1.2.json, where it is a plain
canonical-ID string (e.g. "university_ref": "nl-tu-delft") -- correct and
simple for the JSON-schema-validated source data, but not yet the native
Sanity reference shape a Studio schema of `type: 'reference'` fields
expects on import. This script is the one deterministic, documented
transform between the two, run once, offline, with no network calls and
no live Sanity write.

Two reference shapes appear in the V1.2 schema:
  1. Simple, single-collection refs (e.g. Program.university_ref always
     points at a University) -- resolved via SIMPLE_REF_FIELDS below.
  2. Polymorphic refs formatted "EntityType:canonical-id" (VerificationRecord
     .record_ref, ChangeRecord.record_ref) -- resolved by parsing the
     "EntityType:" prefix.
  3. List-of-refs (source_refs -> SourceRecord; criteria/application_requirements
     are embedded objects, not refs, and are left untouched).

A ref whose target document is not present in this document set (should not
happen -- referential integrity was already checked against records-v1.2.json
by validate_normalized_records_v1_2.py) is left as a plain string and logged,
never silently dropped.

Usage:
    python3 resolve_references.py <in.ndjson> --out <out.ndjson>
"""
import argparse
import json
import sys

TYPE_TO_SANITY_TYPE = {
    "Country": "country", "City": "city", "University": "university", "Campus": "campus",
    "College": "college", "Program": "program", "ProgramPathway": "programPathway",
    "ApplicantCategory": "applicantCategory", "AdmissionStage": "admissionStage",
    "AdmissionsRequirement": "admissionsRequirement", "DecisionPlan": "decisionPlan",
    "CostProfile": "costProfile", "FinancialRequirement": "financialRequirement",
    "Scholarship": "scholarship", "FinancialAidPolicy": "financialAidPolicy",
    "SourceRecord": "sourceRecord", "DerivedCostEstimate": "derivedCostEstimate",
    "VerificationRecord": "verificationRecord", "ChangeRecord": "changeRecord",
}

# field name -> target Sanity type, for simple single-value *_ref fields.
SIMPLE_REF_FIELDS = {
    "country_ref": "country",
    "primary_city_ref": "city",
    "city_ref": "city",
    "university_ref": "university",
    "campus_ref": "campus",
    "college_ref": "college",
    "program_ref": "program",
    "program_pathway_ref": "programPathway",
    "prior_curriculum_category_ref": "applicantCategory",
    "residency_category_ref": "applicantCategory",
    "applicant_category_ref": "applicantCategory",
    "admission_stage_ref": "admissionStage",
    "cost_profile_ref": "costProfile",
}

# list-valued ref fields -> target Sanity type
LIST_REF_FIELDS = {
    "source_refs": "sourceRecord",
}

# polymorphic "EntityType:id" ref fields
POLYMORPHIC_REF_FIELDS = {"record_ref", "source_ref"}

# Entity types whose `id` is only locally unique within one institution's own
# records-v1.2.json / verification-records-v1.2.json (must mirror
# INSTITUTION_SCOPED_TYPES in 04-pipeline/normalized_to_sanity_ndjson_v1_2.py
# exactly, since that is where these documents' own _id was given its
# institution-slug prefix). Found and fixed via the clean-room test's
# duplicate-_id check -- see 08-reporting/v1.2-freeze-report.md point 5 and
# 05-sanity/README.md.
INSTITUTION_SCOPED_SANITY_TYPES = {"sourceRecord", "verificationRecord", "changeRecord"}


def to_ref(sanity_type, canonical_id, institution_slug=None):
    if sanity_type in INSTITUTION_SCOPED_SANITY_TYPES and institution_slug:
        canonical_id = f"{institution_slug}-{canonical_id}"
    return {"_type": "reference", "_ref": f"drafts.{sanity_type}-{canonical_id}"}


def resolve_node(node, known_ids, unresolved_log, doc_id, institution_slug):
    """Recursively resolves ref-shaped fields wherever they occur in the
    document tree, not just at the top level.

    Bug fix (schema/transform alignment repair, 2026-09-24): this used to
    only look at `doc`'s own top-level keys, so a ref field nested inside an
    embedded object -- e.g. Program.testing_policy.source_refs, which the
    Sanity schema types as `array of reference` exactly like every other
    `source_refs` field -- was never resolved and stayed a bare canonical-ID
    string, a schema/data shape mismatch on import. Recursing into every
    dict/list catches every such field regardless of nesting depth, using
    the exact same three lookup tables as before.
    """
    if isinstance(node, dict):
        for field, target_type in SIMPLE_REF_FIELDS.items():
            if field in node and node[field] is not None and isinstance(node[field], str):
                ref = to_ref(target_type, node[field], institution_slug)
                if ref["_ref"] not in known_ids:
                    unresolved_log.append((doc_id, field, ref["_ref"]))
                else:
                    node[field] = ref

        for field, target_type in LIST_REF_FIELDS.items():
            if field in node and isinstance(node[field], list):
                new_list = []
                for item in node[field]:
                    if isinstance(item, str):
                        ref = to_ref(target_type, item, institution_slug)
                        if ref["_ref"] not in known_ids:
                            unresolved_log.append((doc_id, field, ref["_ref"]))
                            new_list.append(item)
                        else:
                            new_list.append(ref)
                    else:
                        new_list.append(item)
                node[field] = new_list

        for field in POLYMORPHIC_REF_FIELDS:
            if field in node and isinstance(node[field], str) and ":" in node[field]:
                entity_type, canonical_id = node[field].split(":", 1)
                target_type = TYPE_TO_SANITY_TYPE.get(entity_type)
                if not target_type:
                    unresolved_log.append((doc_id, field, node[field]))
                else:
                    ref = to_ref(target_type, canonical_id, institution_slug)
                    if ref["_ref"] not in known_ids:
                        unresolved_log.append((doc_id, field, ref["_ref"]))
                    else:
                        node[field] = ref

        for v in node.values():
            resolve_node(v, known_ids, unresolved_log, doc_id, institution_slug)
    elif isinstance(node, list):
        for item in node:
            resolve_node(item, known_ids, unresolved_log, doc_id, institution_slug)


def resolve_doc(doc, known_ids, unresolved_log):
    # Every doc carries its own institution slug in _evidapathMeta (set by
    # normalized_to_sanity_ndjson_v1_2.py) -- this disambiguates a bare
    # "src-01" in THIS doc's own source_refs to the SourceRecord from the
    # SAME institution, never another institution's identically-numbered one.
    institution_slug = (doc.get("_evidapathMeta") or {}).get("institutionSlug")
    resolve_node(doc, known_ids, unresolved_log, doc["_id"], institution_slug)
    return doc


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("in_path")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    docs = []
    with open(args.in_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                docs.append(json.loads(line))

    known_ids = {d["_id"] for d in docs}
    unresolved_log = []
    resolved = [resolve_doc(d, known_ids, unresolved_log) for d in docs]
    resolved.sort(key=lambda d: d["_id"])

    with open(args.out, "w", encoding="utf-8") as f:
        for doc in resolved:
            f.write(json.dumps(doc, ensure_ascii=False, sort_keys=True))
            f.write("\n")

    print(f"Resolved {len(resolved)} documents -> {args.out}")
    if unresolved_log:
        print(f"WARNING: {len(unresolved_log)} reference(s) could not be resolved (left as plain string):",
              file=sys.stderr)
        for doc_id, field, target in unresolved_log:
            print(f"  {doc_id}.{field} -> {target}", file=sys.stderr)
        sys.exit(1)
    else:
        print("All references resolved cleanly -- 0 unresolved.")


if __name__ == "__main__":
    main()
