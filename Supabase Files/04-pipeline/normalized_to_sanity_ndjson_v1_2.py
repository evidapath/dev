#!/usr/bin/env python3
"""
EvidaPath pipeline -- V1.2 normalized records -> Sanity-import NDJSON (draft docs).

Pure, deterministic, offline transform. No network calls, no Sanity token,
never pushes to a live Sanity project -- this script only writes a local
.ndjson file of `drafts.*`-prefixed documents for later manual import once
Sanity publishing is explicitly authorized (not yet, as of this synthesis).

Covers all 17 V1.2 entity types from records-v1.2.json, plus (optionally)
VerificationRecord documents from a sibling verification-records-v1.2.json,
since "sources, verification metadata" are explicitly in-scope for the
Sanity content model (see 05-sanity/sanity-content-model.md).

REPRODUCIBILITY: _evidapathMeta.generatedAt is derived deterministically
from the run_id's leading ISO date, NEVER from datetime.now(), so running
this script twice against unchanged input produces byte-identical output
(confirmed via SHA-256 comparison in the clean-room test).

Usage:
    python3 normalized_to_sanity_ndjson_v1_2.py <records-v1.2.json> [--verification-records <verification-records-v1.2.json>] --out <drafts.ndjson> [--generated-at <iso8601>]

To build the combined five-school NDJSON, run once per institution with
--out pointing at distinct files, then concatenate (see
05-sanity/import/import-readme.md), or use --combine (below) to do it in
one deterministic pass.
"""
import argparse
import glob
import hashlib
import json
import os
import re
import sys

from empty_optional_objects_v1_2 import check_objects

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

TYPE_TO_SANITY_TYPE = {
    "Country": "country", "City": "city", "University": "university", "Campus": "campus",
    "College": "college", "Program": "program", "ProgramPathway": "programPathway",
    "ApplicantCategory": "applicantCategory", "AdmissionStage": "admissionStage",
    "AdmissionsRequirement": "admissionsRequirement", "DecisionPlan": "decisionPlan",
    "CostProfile": "costProfile", "FinancialRequirement": "financialRequirement",
    "Scholarship": "scholarship", "FinancialAidPolicy": "financialAidPolicy",
    "SourceRecord": "sourceRecord", "DerivedCostEstimate": "derivedCostEstimate",
    "VerificationRecord": "verificationRecord",
}

PIPELINE_VERSION = "1.2"

# Entity types whose `id` field is only LOCALLY unique within one institution's
# own records-v1.2.json / verification-records-v1.2.json (e.g. "src-01",
# "vr-01" are reused, independently, by every institution) -- unlike
# University/Program/etc., whose IDs are country-prefixed and therefore
# already globally unique by construction. Combining multiple institutions'
# drafts into one NDJSON without disambiguating these would silently collide
# Sanity `_id`s across institutions (discovered and fixed via the clean-room
# test's document-count/duplicate-_id check -- see 08-reporting/
# v1.2-freeze-report.md and 05-sanity/README.md).
INSTITUTION_SCOPED_TYPES = {"SourceRecord", "VerificationRecord", "ChangeRecord"}

# Schema/transform alignment repair (2026-09-24) -- three bugs found by a
# field-by-field audit of evidapath-schema-v1.2.json ($defs) against the
# generated Sanity schema (05-sanity/{document,object}-types/*.js) against
# this script's actual NDJSON output. See 09-schema-transform-repair/
# schema-transform-alignment.md for the full audit; summary of the fixes
# applied in this module:
#
# 1. `id` was being unconditionally stripped from every document (see the
#    `if k == "id": continue` this replaced) on the theory that it was fully
#    absorbed into `_id`. But every generated Sanity document type ALSO
#    declares its own required top-level `id` string field (mirroring the
#    JSON Schema's own `required: ["id", ...]`) for querying/display
#    independent of Sanity's internal `_id`. Stripping it left that field
#    permanently absent -- the direct cause of the "Untitled" preview bug
#    (every preview.select that read `id` found nothing) and a required-
#    field validation gap on every one of the 399 documents.
# 2. `extension_metadata.fields` is a free-form string-keyed map in the JSON
#    Schema (arbitrary source-backed facts). Sanity has no native arbitrary-
#    map type, and the schema generator previously mapped this to a plain
#    `type: 'string'` field (now fixed to `array of extensionMetadataFieldEntry`
#    -- see gen_schema_files.py) -- but this script still needed to actually
#    perform that shape conversion, since it was copying the raw dict
#    straight through, which is what produced Studio's literal
#    "[object Object]" display.
# 3. Every array-of-embedded-object field (language_requirements,
#    standardized_tests, mandatory_fees_breakdown, other_material_costs,
#    criteria, application_requirements, accepted_assessments) and every
#    embedded single-object field (testing_policy, living_cost_source_basis,
#    progression_requirement, estimated_living_costs_monthly_range,
#    extension_metadata) was emitted as a bare JS object/array with no
#    Sanity `_type`, and array items additionally had no `_key` -- both
#    required by Sanity for embedded objects (`_type` so Studio/GROQ can
#    resolve which object schema applies; `_key` as the array item identity
#    Sanity's editor and diffing rely on). `_key` is derived from a SHA-1 of
#    the item's own canonical-JSON content (never randomly), so re-running
#    this script against unchanged input is still byte-identical.
# 5. `extension_metadata` was always emitted, even when it had literally
#    nothing in it (`note: ""`, `fields: {}`, no `proposed_v1_2_fields`) --
#    7 of the 50 populated `extension_metadata` blocks in the real dataset
#    are exactly this. JSON-Schema's `required: ["note", "fields"]` only
#    means those keys must be present on a fully-populated instance; it does
#    not mean a contentless extension_metadata block is meaningless data
#    that must still be shipped. Combined with removing `Rule.required()`
#    from `note`/`fields` in the generator (see NON_ENFORCED_REQUIRED in
#    gen_schema_files.py), the fix here is symmetric: when the whole block
#    would carry no information, it's omitted like any other absent optional
#    field, exactly per this schema's own "missing = omit" convention.
# 4. Explicit `null` values (this schema's own "missing = value: null,
#    verification_status: unknown" convention -- correct at the JSON-Schema
#    source-of-truth level) were being copied straight through as literal
#    `null`s in the Sanity document. For a plain string/number field this is
#    mostly harmless, but for Sanity's `reference` type a literal `null` is
#    not a valid reference shape (Sanity expects either a `{_type:
#    "reference", _ref: ...}` object or the key to be absent entirely), and
#    for `array`/`object`-typed fields it can produce a broken/blank
#    editor state in Studio. The fix is to omit the key entirely wherever
#    the source value is `null`, recursively, at every nesting level --
#    this preserves the exact same "no value" meaning while being the shape
#    Sanity actually expects. Empty arrays/strings (`[]`, `""`) are left
#    untouched -- those are meaningfully different from `null` in this
#    schema (e.g. `required_subjects: []` means "verified: no subjects
#    required", not "unknown").

# field name -> Sanity object type, for every ARRAY field in the schema
# whose items are embedded objects (mirrors gen_schema_files.py's
# OBJECT_TYPES usage sites -- grep evidapath-schema-v1.2.json's $defs for
# every `"type": "array", "items": {"$ref": "#/$defs/<object-type>"}}`).
ARRAY_OBJECT_FIELDS = {
    "application_requirements": "applicationRequirement",
    "standardized_tests": "testRequirement",
    "language_requirements": "languageRequirement",
    "mandatory_fees_breakdown": "lineItem",
    "other_material_costs": "lineItem",
    "accepted_assessments": "acceptedAssessment",
    "criteria": "selectionCriterion",
}

# field name -> Sanity object type, for every SINGLE-object (non-array)
# embedded-object field in the schema (mirrors the same $defs usage sites).
SINGLE_OBJECT_FIELDS = {
    "testing_policy": "testingPolicy",
    "living_cost_source_basis": "livingCostSourceBasis",
    "progression_requirement": "progressionRequirement",
    "estimated_living_costs_monthly_range": "monthlyRange",
    "extension_metadata": "extensionMetadata",
}


def _stable_key(item: dict) -> str:
    """Deterministic Sanity `_key` derived from an embedded object's own
    content -- never random, so this script stays reproducible."""
    canonical = json.dumps(item, sort_keys=True, ensure_ascii=False)
    return hashlib.sha1(canonical.encode("utf-8")).hexdigest()[:12]


# The exact three fields the JSON Schema declares as bare `{}` ("any
# value") -- see ANY_VALUE_BOX_TYPE in gen_schema_files.py. Confirmed by
# direct query of every $def in the schema: no other property anywhere is
# typeless, so this name-based match is exact, not a heuristic.
ANY_VALUE_FIELDS = {"proposed_value", "previous_value"}


def _wrap_any_value(v):
    """verification_record.proposed_value / change_record.{previous,proposed}
    _value -> a deterministic {_type, value, value_type} box. `null` is
    handled here, NOT by the generic null-pruning in `_fix_node`: for every
    other field in this schema, `null` means "missing/unknown data" and
    should be omitted; here it means "the correct/proposed value for this
    field is genuinely absent" -- itself a real verification finding
    (VERIFIED_ABSENT), so it must survive as a populated, schema-valid
    value on a field the JSON Schema marks required."""
    if v is None:
        return {"_type": "anyValueBox", "value": "", "value_type": "null"}
    if isinstance(v, bool):  # must precede the int/float check -- bool is an int subclass in Python
        return {"_type": "anyValueBox", "value": "true" if v else "false", "value_type": "boolean"}
    if isinstance(v, str):
        return {"_type": "anyValueBox", "value": v, "value_type": "string"}
    if isinstance(v, (int, float)):
        return {"_type": "anyValueBox", "value": json.dumps(v), "value_type": "number"}
    return {"_type": "anyValueBox", "value": json.dumps(v, sort_keys=True, ensure_ascii=False), "value_type": "json"}


def _transform_extension_fields(fields_dict: dict) -> list:
    """extension_metadata.fields: free-form {key: value} map -> deterministic
    list of {_type, _key, key, value, value_type} entries. `value` is always
    a string: the original value verbatim when it was already a string, or
    its canonical (sort_keys) JSON serialization otherwise -- `value_type`
    records which case applies so the original shape is always recoverable.
    Never a lossy `str(value)`/"[object Object]"-style stringification."""
    entries = []
    for k in sorted(fields_dict.keys()):
        v = fields_dict[k]
        if isinstance(v, str):
            value_type, value_str = "string", v
        else:
            value_type, value_str = "json", json.dumps(v, sort_keys=True, ensure_ascii=False)
        entries.append({
            "_type": "extensionMetadataFieldEntry",
            "_key": k,
            "key": k,
            "value": value_str,
            "value_type": value_type,
        })
    return entries


def _extension_metadata_is_empty(em: dict) -> bool:
    """True if an (already-transformed) extension_metadata dict carries no
    real information: blank note, no field entries, no proposed fields."""
    note = (em.get("note") or "").strip()
    fields = em.get("fields") or []
    proposed = em.get("proposed_v1_2_fields") or []
    return not note and not fields and not proposed


def _fix_node(node):
    """Single recursive pass applied to every document before it's written:
    prunes explicit nulls, converts extension_metadata.fields, and tags
    embedded objects/array items with Sanity's required _type/_key. See the
    module-level comment above for why each of these is needed."""
    if isinstance(node, dict):
        fixed = {}
        for k, v in node.items():
            if k in ANY_VALUE_FIELDS:
                fixed[k] = _wrap_any_value(v)  # before the null check: null is meaningful here
                continue
            if v is None:
                continue  # (4) omit nulls entirely rather than emit `null`
            if k == "fields" and isinstance(v, dict):
                fixed[k] = _transform_extension_fields(v)  # (2)
                continue
            fixed_v = _fix_node(v)
            if k == "extension_metadata" and isinstance(fixed_v, dict) and _extension_metadata_is_empty(fixed_v):
                continue  # (5) omit the whole block when it carries no information
            if k in SINGLE_OBJECT_FIELDS and isinstance(fixed_v, dict):
                fixed_v = {**fixed_v, "_type": SINGLE_OBJECT_FIELDS[k]}  # (3)
            elif k in ARRAY_OBJECT_FIELDS and isinstance(fixed_v, list):
                sanity_type = ARRAY_OBJECT_FIELDS[k]
                seen = {}
                new_list = []
                for item in fixed_v:
                    if isinstance(item, dict):
                        base_key = _stable_key(item)
                        n = seen.get(base_key, 0)
                        seen[base_key] = n + 1
                        key = base_key if n == 0 else f"{base_key}-{n}"
                        item = {**item, "_type": sanity_type, "_key": key}
                    new_list.append(item)
                fixed_v = new_list
            fixed[k] = fixed_v
        return fixed
    if isinstance(node, list):
        return [_fix_node(x) for x in node if x is not None]
    return node


def derive_generated_at(run_id: str) -> str:
    m = re.match(r"^(\d{4}-\d{2}-\d{2})", run_id or "")
    date = m.group(1) if m else "1970-01-01"
    return f"{date}T00:00:00Z"


def derive_institution_slug(records_path: str) -> str:
    """The institution folder name (e.g. 'nl-tu-delft'), i.e. the parent
    directory of records-v1.2.json -- the same canonical-ID prefix already
    used for every globally-unique entity ID in this dataset."""
    return os.path.basename(os.path.dirname(os.path.abspath(records_path)))


def to_sanity_doc(entity_type, record, generated_at, institution_slug):
    sanity_type = TYPE_TO_SANITY_TYPE.get(entity_type, entity_type[0].lower() + entity_type[1:])
    rec_id = record.get("id") or record.get("id".upper())
    id_prefix = f"{institution_slug}-" if entity_type in INSTITUTION_SCOPED_TYPES else ""
    doc_id = f"drafts.{sanity_type}-{id_prefix}{rec_id}"
    doc = {"_id": doc_id, "_type": sanity_type}
    for k, v in record.items():
        # `id` is kept (not stripped): every Sanity document type also
        # declares its own required top-level `id` field, independent of
        # `_id` -- see the module-level comment above (fix 1).
        doc[k] = v
    doc["_evidapathMeta"] = {
        "sourceEntityType": entity_type, "sourceRecordId": rec_id,
        "institutionSlug": institution_slug,
        "generatedAt": generated_at, "pipelineVersion": PIPELINE_VERSION,
    }
    fixed, empty_objects = check_objects(_fix_node(doc), omit_empty=True)
    if empty_objects:
        raise ValueError(f"{doc_id}: empty required objects: {empty_objects}")
    return fixed


def build_docs_for_institution(records_path, verification_records_path=None, generated_at_override=None):
    with open(records_path, encoding="utf-8") as f:
        data = json.load(f)
    run_id = data.get("run_id", "")
    generated_at = generated_at_override or derive_generated_at(run_id)
    institution_slug = derive_institution_slug(records_path)

    docs = []
    for collection, entity_type in COLLECTION_TO_ENTITY_TYPE.items():
        for record in data.get(collection, []):
            docs.append(to_sanity_doc(entity_type, record, generated_at, institution_slug))

    if verification_records_path and os.path.isfile(verification_records_path):
        with open(verification_records_path, encoding="utf-8") as f:
            vr_data = json.load(f)
        for vr in vr_data.get("verification_records", []):
            docs.append(to_sanity_doc("VerificationRecord", vr, generated_at, institution_slug))

    return docs, run_id


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("records_path", nargs="?", help="Single institution's records-v1.2.json")
    parser.add_argument("--verification-records", default=None)
    parser.add_argument("--out", required=True)
    parser.add_argument("--generated-at", default=None)
    parser.add_argument("--combine-dir", default=None,
                         help="Instead of a single records_path, glob "
                              "<combine-dir>/*/records-v1.2.json (and matching "
                              "verification-records-v1.2.json) and write ONE combined, "
                              "deterministically-ordered NDJSON.")
    args = parser.parse_args()

    all_docs = []
    if args.combine_dir:
        inst_dirs = sorted(glob.glob(os.path.join(args.combine_dir, "*")))
        for inst_dir in inst_dirs:
            rp = os.path.join(inst_dir, "records-v1.2.json")
            vp = os.path.join(inst_dir, "verification-records-v1.2.json")
            if not os.path.isfile(rp):
                continue
            docs, run_id = build_docs_for_institution(rp, vp, args.generated_at)
            all_docs.extend(docs)
    else:
        if not args.records_path:
            print("ERROR: records_path is required unless --combine-dir is given.", file=sys.stderr)
            sys.exit(2)
        docs, run_id = build_docs_for_institution(args.records_path, args.verification_records, args.generated_at)
        all_docs.extend(docs)

    # Deterministic ordering: sort by _id so output never depends on dict/glob iteration order.
    all_docs.sort(key=lambda d: d["_id"])

    with open(args.out, "w", encoding="utf-8") as f:
        for doc in all_docs:
            f.write(json.dumps(doc, ensure_ascii=False, sort_keys=True))
            f.write("\n")

    by_type = {}
    for d in all_docs:
        by_type[d["_type"]] = by_type.get(d["_type"], 0) + 1
    print(f"Wrote {len(all_docs)} Sanity draft documents to {args.out} (no live write).")
    for t, c in sorted(by_type.items()):
        print(f"  {t}: {c}")


if __name__ == "__main__":
    main()
