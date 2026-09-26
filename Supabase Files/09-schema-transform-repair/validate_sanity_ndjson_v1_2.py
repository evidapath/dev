#!/usr/bin/env python3
"""
EvidaPath pipeline -- Sanity-NDJSON-layer contract validator.

WHY THIS EXISTS: every bug found in the V1.2 -> Sanity contract repair
(missing `id`, extension_metadata.fields type mismatch, un-pruned nulls,
un-annotated embedded objects/array items, un-resolved nested references,
contentless-but-present extension_metadata tripping Rule.required()) lived
in the *transform* layer -- 04-pipeline/normalized_to_sanity_ndjson_v1_2.py,
05-sanity/import/resolve_references.py, 05-sanity/generation/
gen_schema_files.py -- not in the JSON-Schema-validated source data, so none
of the existing validators (which all check records-v1.2.json /
verification-records-v1.2.json against the JSON Schema) could ever have
caught them. This script closes that gap: it checks the *output* of the
transform pipeline -- the resolved Sanity NDJSON that is actually the
import artifact -- against both (a) Sanity's own structural requirements
and (b) the canonical JSON Schema's field/enum vocabulary, independent of
whether the JSON-Schema-level source data was itself valid.

This is the harness required by 09-schema-transform-repair/
sanity-serialization-contract.md Step 6. It fails on every one of:
  - required business `id` missing
  - explicit null in an unsupported field
  - "[object Object]" coercion risk (a raw object/array serialized into a
    plain string/text field, or the literal stringified text itself)
  - reference target absent (unresolved reference)
  - reference target wrong type (the field's declared target type doesn't
    match what the referenced document's `_id` actually is)
  - array-of-object item missing Sanity `_type`
  - array-of-object item missing a (deterministic) `_key`, or a duplicate
    `_key` within one array
  - malformed extension_metadata (raw-dict `fields`, or a present-but-
    contentless block that should have been omitted)
  - empty optional object that would trip a nested Rule.required() for no
    informational reason
  - unexpected field (a top-level key the JSON Schema's own $def for that
    entity type doesn't declare, `id`/`_evidapathMeta` excepted)
  - enum mismatch (an enum-typed field holding a value outside the JSON
    Schema's own enum list for it)

Pure, deterministic, offline. No network calls, no Sanity token. Reads only
the resolved NDJSON file(s) and the JSON Schema given on the command line.

Usage:
    python3 validate_sanity_ndjson_v1_2.py --schema <evidapath-schema-v1.2.json> <resolved.ndjson> [<resolved2.ndjson> ...]

Exit code 0 if every check passes across every file given; 1 otherwise, with
every failure printed (never just the first).
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "04-pipeline"))
from empty_optional_objects_v1_2 import check_objects

ARRAY_OBJECT_FIELDS = {
    "application_requirements", "standardized_tests", "language_requirements",
    "mandatory_fees_breakdown", "other_material_costs", "accepted_assessments",
    "criteria",
}
SINGLE_OBJECT_FIELDS = {
    "testing_policy", "living_cost_source_basis", "progression_requirement",
    "estimated_living_costs_monthly_range", "extension_metadata",
}
# field name -> target Sanity type, for reference-shaped fields (mirrors
# 05-sanity/import/resolve_references.py's own lookup tables exactly).
SIMPLE_REF_FIELDS = {
    "country_ref": "country", "primary_city_ref": "city", "city_ref": "city",
    "university_ref": "university", "campus_ref": "campus", "college_ref": "college",
    "program_ref": "program", "program_pathway_ref": "programPathway",
    "prior_curriculum_category_ref": "applicantCategory", "residency_category_ref": "applicantCategory",
    "applicant_category_ref": "applicantCategory", "admission_stage_ref": "admissionStage",
    "cost_profile_ref": "costProfile",
}
LIST_REF_FIELDS = {"source_refs": "sourceRecord"}
POLYMORPHIC_REF_FIELDS = {"record_ref", "source_ref"}  # can point at any document type

# entity-def-name -> sanity type, mirrors gen_schema_files.py's DOCUMENT_TYPES/OBJECT_TYPES.
DEF_TO_SANITY_DOC_TYPE = {
    "country": "country", "city": "city", "university": "university", "campus": "campus",
    "college": "college", "program": "program", "program_pathway": "programPathway",
    "applicant_category": "applicantCategory", "admission_stage": "admissionStage",
    "admissions_requirement": "admissionsRequirement", "decision_plan": "decisionPlan",
    "cost_profile": "costProfile", "financial_requirement": "financialRequirement",
    "scholarship": "scholarship", "financial_aid_policy": "financialAidPolicy",
    "source_record": "sourceRecord", "derived_cost_estimate": "derivedCostEstimate",
    "verification_record": "verificationRecord", "change_record": "changeRecord",
}
RESERVED_KEYS = {"_id", "_type", "_key", "_evidapathMeta", "id", "value_type", "value", "key"}


def load_schema_field_maps(schema_path):
    """Returns (allowed_fields[sanity_type] -> set, enum_values[sanity_type][field] -> set)
    derived directly from the JSON Schema's own $defs -- this is the
    vocabulary the transform's output is checked against, not a hand
    duplicated copy of it."""
    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)
    defs = schema["$defs"]
    allowed_fields = {}
    enum_values = {}
    for def_name, sanity_type in DEF_TO_SANITY_DOC_TYPE.items():
        node = defs.get(def_name, {})
        props = node.get("properties", {})
        allowed_fields[sanity_type] = set(props.keys())
        enums = {}
        for pname, pdef in props.items():
            if "$ref" in pdef:
                ref_name = pdef["$ref"].split("/")[-1]
                ref_def = defs.get(ref_name, {})
                if "enum" in ref_def:
                    enums[pname] = set(ref_def["enum"])
        enum_values[sanity_type] = enums
    return allowed_fields, enum_values


def find_nulls(node, path=""):
    found = []
    if isinstance(node, dict):
        for k, v in node.items():
            p = f"{path}.{k}"
            if v is None:
                found.append(p)
            else:
                found += find_nulls(v, p)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            p = f"{path}[{i}]"
            if item is None:
                found.append(p)
            else:
                found += find_nulls(item, p)
    return found


def find_missing_type_key(node, path=""):
    found = []
    if isinstance(node, dict):
        for k, v in node.items():
            p = f"{path}.{k}"
            if k in ARRAY_OBJECT_FIELDS and isinstance(v, list):
                for i, item in enumerate(v):
                    if isinstance(item, dict) and ("_type" not in item or "_key" not in item):
                        found.append(f"{p}[{i}] (missing _type and/or _key)")
            elif k in SINGLE_OBJECT_FIELDS and isinstance(v, dict) and "_type" not in v:
                found.append(f"{p} (missing _type)")
            found += find_missing_type_key(v, p)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            found += find_missing_type_key(item, f"{path}[{i}]")
    return found


def find_duplicate_keys(node, path=""):
    found = []
    if isinstance(node, dict):
        for k, v in node.items():
            p = f"{path}.{k}"
            if isinstance(v, list) and v and all(isinstance(i, dict) and "_key" in i for i in v):
                keys = [i["_key"] for i in v]
                if len(keys) != len(set(keys)):
                    found.append(f"{p} (duplicate _key among {keys})")
            found += find_duplicate_keys(v, p)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            found += find_duplicate_keys(item, f"{path}[{i}]")
    return found


def find_unresolved_looking_refs(node, path=""):
    found = []
    if isinstance(node, dict):
        for k, v in node.items():
            p = f"{path}.{k}"
            if k in SIMPLE_REF_FIELDS or k in POLYMORPHIC_REF_FIELDS or k in LIST_REF_FIELDS:
                if isinstance(v, str):
                    found.append(f"{p} (still a bare string: {v!r})")
                elif isinstance(v, list):
                    for i, item in enumerate(v):
                        if isinstance(item, str):
                            found.append(f"{p}[{i}] (still a bare string: {item!r})")
            found += find_unresolved_looking_refs(v, p)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            found += find_unresolved_looking_refs(item, f"{path}[{i}]")
    return found


def find_wrong_type_refs(node, id_to_type, path=""):
    """A resolved reference's _ref, checked against the ACTUAL _type of the
    document it points to (via the full id->type index), must match one of
    the types that field is allowed to target."""
    found = []
    if isinstance(node, dict):
        for k, v in node.items():
            p = f"{path}.{k}"
            expected = None
            if k in SIMPLE_REF_FIELDS:
                expected = {SIMPLE_REF_FIELDS[k]}
            elif k in LIST_REF_FIELDS:
                expected = {LIST_REF_FIELDS[k]}
            if expected and isinstance(v, dict) and v.get("_type") == "reference":
                actual_type = id_to_type.get(v.get("_ref"))
                if actual_type is not None and actual_type not in expected:
                    found.append(f"{p} (_ref {v.get('_ref')!r} is a {actual_type!r}, expected one of {expected})")
            elif expected and isinstance(v, list):
                for i, item in enumerate(v):
                    if isinstance(item, dict) and item.get("_type") == "reference":
                        actual_type = id_to_type.get(item.get("_ref"))
                        if actual_type is not None and actual_type not in expected:
                            found.append(f"{p}[{i}] (_ref {item.get('_ref')!r} is a {actual_type!r}, expected one of {expected})")
            found += find_wrong_type_refs(v, id_to_type, p)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            found += find_wrong_type_refs(item, id_to_type, f"{path}[{i}]")
    return found


def find_object_coercion_risk(node, path=""):
    """Belt-and-suspenders, structural rather than name-list-based (a
    hardcoded field-name allowlist is exactly the kind of thing that missed
    `assumptions`/`proposed_value` in earlier drafts of this check -- this
    version instead uses the repair's own invariant: by the time a document
    reaches this validator, EVERY embedded object must carry `_type`
    (find_missing_type_key already fails independently if not), and every
    array must be either all-strings, all-`_type`-tagged embedded objects,
    or all resolved `{_type: reference, ...}` entries. A dict with no
    `_type`, or a list that is none of those three uniform shapes, is
    exactly the shape that stringifies to "[object Object]" if it ever
    reaches a Sanity string/text field -- regardless of which field name it
    happens to be sitting in.
    """
    found = []
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "_evidapathMeta":
                continue  # pipeline-internal provenance, not a Sanity schema field
            p = f"{path}.{k}"
            if isinstance(v, str) and "[object Object]" in v:
                found.append(f"{p} (contains literal '[object Object]' text: {v!r})")
            elif isinstance(v, dict) and "_type" not in v:
                found.append(f"{p} (untagged embedded object -- missing _type, coercion risk: {v!r})")
            elif isinstance(v, list) and v:
                all_str = all(isinstance(i, str) for i in v)
                all_tagged = all(isinstance(i, dict) and "_type" in i for i in v)
                if not (all_str or all_tagged):
                    found.append(f"{p} (mixed/untagged array item shape, coercion risk: {v!r})")
            found += find_object_coercion_risk(v, p)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            found += find_object_coercion_risk(item, f"{path}[{i}]")
    return found


def find_extension_metadata_issues(node, path=""):
    found = []
    if isinstance(node, dict):
        if "fields" in node and "note" in node and isinstance(node.get("fields"), dict):
            found.append(f"{path} (extension_metadata.fields is still a raw object, not a list)")
        if node.get("_type") == "extensionMetadata":
            note = (node.get("note") or "").strip()
            fields = node.get("fields") or []
            proposed = node.get("proposed_v1_2_fields") or []
            if not note and not fields and not proposed:
                found.append(f"{path} (extension_metadata is present but fully contentless -- should have been omitted)")
        for k, v in node.items():
            found += find_extension_metadata_issues(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, item in enumerate(node):
            found += find_extension_metadata_issues(item, f"{path}[{i}]")
    return found


def find_unexpected_and_enum_errors(doc, sanity_type, allowed_fields, enum_values):
    found = []
    allowed = allowed_fields.get(sanity_type)
    if allowed is not None:
        for k in doc.keys():
            if k in RESERVED_KEYS:
                continue
            if k not in allowed:
                found.append(f"unexpected top-level field '{k}' (not in the {sanity_type} $def)")
    enums = enum_values.get(sanity_type, {})
    for field, allowed_values in enums.items():
        if field in doc and isinstance(doc[field], str) and doc[field] not in allowed_values:
            found.append(f"enum mismatch: {field}={doc[field]!r} not in {sorted(allowed_values)}")
    return found


def validate_files(paths, schema_path):
    allowed_fields, enum_values = ({}, {})
    if schema_path:
        allowed_fields, enum_values = load_schema_field_maps(schema_path)

    object_schema = None
    if schema_path:
        with open(schema_path, encoding="utf-8") as f:
            object_schema = json.load(f)

    all_docs = []
    parse_errors = []
    for path in paths:
        with open(path, encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    all_docs.append(json.loads(line))
                except json.JSONDecodeError as e:
                    parse_errors.append(f"{path}:{lineno}: invalid JSON ({e})")

    if parse_errors:
        return len(all_docs), parse_errors

    id_to_type = {d["_id"]: d["_type"] for d in all_docs if "_id" in d and "_type" in d}
    errors = []

    ids = [d.get("_id") for d in all_docs]
    seen = {}
    for i in ids:
        seen[i] = seen.get(i, 0) + 1
    dupes = [i for i, c in seen.items() if c > 1]
    if dupes:
        errors.append(f"duplicate _id(s) across the given file(s): {dupes}")

    for d in all_docs:
        doc_id = d.get("_id", "?")
        sanity_type = d.get("_type")
        if not d.get("id"):
            errors.append(f"{doc_id}: missing/empty top-level `id` field")
        _, empty_objects = check_objects(d, schema=object_schema)
        for issue in empty_objects:
            requirement = "optional/nullable" if issue["optional"] else "required"
            errors.append(f"{doc_id}: empty {requirement} object at {issue['path']}")
        for n in find_nulls(d):
            errors.append(f"{doc_id}: explicit null at {n}")
        for n in find_missing_type_key(d):
            errors.append(f"{doc_id}: {n}")
        for n in find_duplicate_keys(d):
            errors.append(f"{doc_id}: {n}")
        for n in find_unresolved_looking_refs(d):
            errors.append(f"{doc_id}: unresolved-looking reference at {n}")
        for n in find_wrong_type_refs(d, id_to_type):
            errors.append(f"{doc_id}: wrong-type reference at {n}")
        for n in find_object_coercion_risk(d):
            errors.append(f"{doc_id}: object-coercion risk at {n}")
        for n in find_extension_metadata_issues(d):
            errors.append(f"{doc_id}: {n}")
        if schema_path and sanity_type in DEF_TO_SANITY_DOC_TYPE.values():
            for n in find_unexpected_and_enum_errors(d, sanity_type, allowed_fields, enum_values):
                errors.append(f"{doc_id}: {n}")

    return len(all_docs), errors


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("ndjson_paths", nargs="+")
    parser.add_argument("--schema", default=None,
                         help="Path to evidapath-schema-v1.2.json, enables unexpected-field and enum-mismatch checks.")
    args = parser.parse_args()

    total_docs, errors = validate_files(args.ndjson_paths, args.schema)
    print(f"Checked {len(args.ndjson_paths)} file(s), {total_docs} documents"
          f"{' (schema-vocabulary checks enabled)' if args.schema else ' (--schema not given: unexpected-field/enum checks skipped)'}.")

    if errors:
        print(f"\nFAIL -- {len(errors)} error(s):", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"\nPASS -- {total_docs} documents, 0 errors.")
        sys.exit(0)


if __name__ == "__main__":
    main()
