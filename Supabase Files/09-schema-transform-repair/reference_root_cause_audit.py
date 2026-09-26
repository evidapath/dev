#!/usr/bin/env python3
"""
Reference root-cause audit -- Step 4 of the V1.2 -> Sanity contract repair.

For every reference in a resolved Sanity NDJSON, determines which of six
categories explains it (or confirms it's clean):

  A. target genuinely missing (the referenced _id is not in this document set)
  B. wrong allowed reference type (the field's schema only allows certain
     target types, and the actual target is a different type)
  C. malformed _ref (doesn't match the expected drafts.<sanityType>-<id> shape)
  D. draft/published ID mismatch -- NOT DIRECTLY TESTABLE from a static file:
     this dataset is entirely `drafts.*`-prefixed by construction (nothing in
     it is published), so a genuine draft/published split can only exist if
     the LIVE Sanity dataset also contains an independently-published (non-
     drafts-prefixed) copy of the same record from some other import. This
     script says so explicitly rather than asserting an unfalsifiable "0".
  E. target exists in this set, but the target DOCUMENT ITSELF fails the
     contract validator (missing id, null, un-annotated embedded object,
     etc.) -- this is the "reference inherits its target's redness" theory,
     and this script tests it directly by cross-referencing every reference
     against the SAME contract validator's per-document error list.
  F. other / unexplained.

Usage:
    python3 reference_root_cause_audit.py --schema <schema.json> <resolved.ndjson>
"""
import argparse
import json
import re
import sys

sys.path.insert(0, ".")
from validate_sanity_ndjson_v1_2 import (  # noqa: E402
    SIMPLE_REF_FIELDS, LIST_REF_FIELDS, POLYMORPHIC_REF_FIELDS,
    find_nulls, find_missing_type_key, find_duplicate_keys,
    find_object_coercion_risk, find_extension_metadata_issues,
    load_schema_field_maps, find_unexpected_and_enum_errors, DEF_TO_SANITY_DOC_TYPE,
)

REF_ID_PATTERN = re.compile(r"^drafts\.[a-zA-Z]+-.+$")


def per_document_errors(doc, id_to_type, allowed_fields, enum_values):
    """Every contract error found on this ONE document (reused from the
    validator's own per-doc checks, minus the doc-vs-doc checks like
    duplicate-_id which don't belong to a single document)."""
    errs = []
    if not doc.get("id"):
        errs.append("missing id")
    errs += [f"null:{p}" for p in find_nulls(doc)]
    errs += [f"missing_type_key:{p}" for p in find_missing_type_key(doc)]
    errs += [f"dup_key:{p}" for p in find_duplicate_keys(doc)]
    errs += [f"coercion_risk:{p}" for p in find_object_coercion_risk(doc)]
    errs += [f"extension_metadata:{p}" for p in find_extension_metadata_issues(doc)]
    sanity_type = doc.get("_type")
    if sanity_type in DEF_TO_SANITY_DOC_TYPE.values():
        errs += find_unexpected_and_enum_errors(doc, sanity_type, allowed_fields, enum_values)
    return errs


def collect_refs(node, path=""):
    """Yields (field_name, ref_dict, path) for every resolved reference
    object found anywhere in the tree."""
    if isinstance(node, dict):
        for k, v in node.items():
            p = f"{path}.{k}"
            if isinstance(v, dict) and v.get("_type") == "reference":
                yield k, v, p
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    if isinstance(item, dict) and item.get("_type") == "reference":
                        yield k, item, f"{p}[{i}]"
            yield from collect_refs(v, p)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            yield from collect_refs(item, f"{path}[{i}]")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ndjson_path")
    parser.add_argument("--schema", required=True)
    args = parser.parse_args()

    docs = [json.loads(l) for l in open(args.ndjson_path, encoding="utf-8") if l.strip()]
    id_to_doc = {d["_id"]: d for d in docs if "_id" in d}
    allowed_fields, enum_values = load_schema_field_maps(args.schema)

    # Precompute per-document error lists once.
    doc_errors = {doc_id: per_document_errors(d, {i: dd.get("_type") for i, dd in id_to_doc.items()}, allowed_fields, enum_values)
                  for doc_id, d in id_to_doc.items()}

    counts = {"A_missing": 0, "B_wrong_type": 0, "C_malformed": 0, "E_target_invalid": 0, "F_other": 0, "clean": 0}
    examples = {k: [] for k in counts}
    total_refs = 0

    for doc in docs:
        for field, ref, path in collect_refs(doc):
            total_refs += 1
            ref_id = ref.get("_ref")
            problems = []

            if not REF_ID_PATTERN.match(ref_id or ""):
                counts["C_malformed"] += 1
                problems.append("C")
                if len(examples["C_malformed"]) < 3:
                    examples["C_malformed"].append(f"{doc['_id']}.{path} -> {ref_id!r}")

            target = id_to_doc.get(ref_id)
            if target is None:
                counts["A_missing"] += 1
                problems.append("A")
                if len(examples["A_missing"]) < 3:
                    examples["A_missing"].append(f"{doc['_id']}.{path} -> {ref_id!r}")
            else:
                expected_type = None
                if field in SIMPLE_REF_FIELDS:
                    expected_type = SIMPLE_REF_FIELDS[field]
                elif field in LIST_REF_FIELDS:
                    expected_type = LIST_REF_FIELDS[field]
                if expected_type and target.get("_type") != expected_type:
                    counts["B_wrong_type"] += 1
                    problems.append("B")
                    if len(examples["B_wrong_type"]) < 3:
                        examples["B_wrong_type"].append(
                            f"{doc['_id']}.{path} -> {ref_id!r} is a {target.get('_type')!r}, expected {expected_type!r}")

                target_errs = doc_errors.get(ref_id, [])
                if target_errs:
                    counts["E_target_invalid"] += 1
                    problems.append("E")
                    if len(examples["E_target_invalid"]) < 3:
                        examples["E_target_invalid"].append(f"{doc['_id']}.{path} -> {ref_id!r} (target errors: {target_errs[:2]})")

            if not problems:
                counts["clean"] += 1

    print(f"Audited {total_refs} references across {len(docs)} documents in {args.ndjson_path}\n")
    print(f"{'Category':<20} {'Count':>8}")
    print("-" * 30)
    print(f"{'clean':<20} {counts['clean']:>8}")
    print(f"{'A: target missing':<20} {counts['A_missing']:>8}")
    print(f"{'B: wrong type':<20} {counts['B_wrong_type']:>8}")
    print(f"{'C: malformed _ref':<20} {counts['C_malformed']:>8}")
    print(f"{'E: target invalid':<20} {counts['E_target_invalid']:>8}")
    print(f"{'D: draft/pub mismatch':<20} {'N/T':>8}  (not testable from a static file -- see docstring)")
    print()
    for cat, exs in examples.items():
        if exs:
            print(f"Examples for {cat}:")
            for e in exs:
                print(f"  {e}")


if __name__ == "__main__":
    main()
