#!/usr/bin/env python3
"""Generate Sanity Studio v3 schema files (document-types/ and object-types/)
from evidapath-schema-v1.2.json. Deterministic, offline, no Sanity SDK calls.
"""
import json
import os

# Paths are resolved relative to this script's own location (package-root/
# 05-sanity/generation/), so the package is self-contained and this script
# is re-runnable from any extraction location without editing.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PACKAGE_ROOT = os.path.dirname(os.path.dirname(_THIS_DIR))
SCHEMA_PATH = os.path.join(_PACKAGE_ROOT, "02-schema-design", "evidapath-schema-v1.2.json")
OUT_DIR = os.path.join(_PACKAGE_ROOT, "05-sanity")

with open(SCHEMA_PATH, encoding="utf-8") as f:
    SCHEMA = json.load(f)
DEFS = SCHEMA["$defs"]

# def_name -> (sanity type name, title)
DOCUMENT_TYPES = {
    "country": ("country", "Country"),
    "city": ("city", "City"),
    "university": ("university", "University"),
    "campus": ("campus", "Campus"),
    "college": ("college", "College"),
    "program": ("program", "Program"),
    "program_pathway": ("programPathway", "Program Pathway"),
    "applicant_category": ("applicantCategory", "Applicant Category"),
    "admission_stage": ("admissionStage", "Admission Stage"),
    "admissions_requirement": ("admissionsRequirement", "Admissions Requirement"),
    "decision_plan": ("decisionPlan", "Decision Plan"),
    "cost_profile": ("costProfile", "Cost Profile"),
    "financial_requirement": ("financialRequirement", "Financial Requirement"),
    "scholarship": ("scholarship", "Scholarship"),
    "financial_aid_policy": ("financialAidPolicy", "Financial Aid Policy"),
    "source_record": ("sourceRecord", "Source Record"),
    "derived_cost_estimate": ("derivedCostEstimate", "Derived Cost Estimate"),
    "verification_record": ("verificationRecord", "Verification Record"),
    "change_record": ("changeRecord", "Change Record"),
}

OBJECT_TYPES = {
    "selection_criterion": ("selectionCriterion", "Selection Criterion"),
    "application_requirement": ("applicationRequirement", "Application Requirement"),
    "testing_policy": ("testingPolicy", "Testing Policy"),
    "accepted_assessment": ("acceptedAssessment", "Accepted Assessment"),
    "monthly_range": ("monthlyRange", "Monthly Range"),
    "progression_requirement": ("progressionRequirement", "Progression Requirement"),
    "living_cost_source_basis": ("livingCostSourceBasis", "Living Cost Source Basis"),
    "extension_metadata": ("extensionMetadata", "Extension Metadata"),
    "line_item": ("lineItem", "Line Item"),
    "test_requirement": ("testRequirement", "Test Requirement"),
    "language_requirement": ("languageRequirement", "Language Requirement"),
}

# Simple single-value *_ref field -> target Sanity document type (mirrors resolve_references.py)
SIMPLE_REF_FIELDS = {
    "country_ref": "country", "primary_city_ref": "city", "city_ref": "city",
    "university_ref": "university", "campus_ref": "campus", "college_ref": "college",
    "program_ref": "program", "program_pathway_ref": "programPathway",
    "prior_curriculum_category_ref": "applicantCategory", "residency_category_ref": "applicantCategory",
    "applicant_category_ref": "applicantCategory", "admission_stage_ref": "admissionStage",
    "cost_profile_ref": "costProfile",
}
LIST_REF_FIELDS = {"source_refs": "sourceRecord"}
POLYMORPHIC_REF_FIELDS = {"record_ref": "polymorphic", "source_ref": "polymorphic"}

ENUM_DEFS = {
    "degree_type": DEFS["degree_type"]["enum"],
    "duration_unit": DEFS["duration_unit"]["enum"],
    "institution_type": DEFS["institution_type"]["enum"],
    "record_status": DEFS["record_status"]["enum"],
    "verification_status": DEFS["verification_status"]["enum"],
    "source_type": DEFS["source_type"]["enum"],
    "provider_type": DEFS["provider_type"]["enum"],
    "award_type": DEFS["award_type"]["enum"],
    "tuition_basis": DEFS["tuition_basis"]["enum"],
    "living_cost_source_basis_kind": DEFS["living_cost_source_basis_kind"]["enum"],
    "blocking_status": DEFS["blocking_status"]["enum"],
    "resolution_status": DEFS["resolution_status"]["enum"],
    "test_required_flag": DEFS["test_required_flag"]["enum"],
    "requirement_necessity": DEFS["requirement_necessity"]["enum"],
    "applicant_category_dimension": DEFS["applicant_category_dimension"]["enum"],
    "admission_stage_type": DEFS["admission_stage_type"]["enum"],
    "pathway_type": DEFS["pathway_type"]["enum"],
    "decision_plan_type": DEFS["decision_plan_type"]["enum"],
    "financial_requirement_type": DEFS["financial_requirement_type"]["enum"],
    "financial_aid_policy_type": DEFS["financial_aid_policy_type"]["enum"],
    "need_aware_or_blind": DEFS["need_aware_or_blind"]["enum"],
    "application_requirement_type": DEFS["application_requirement_type"]["enum"],
}

LONG_TEXT_FIELDS = {
    "description", "notes", "excerpt", "conflict_or_limitation_notes", "reason_for_change",
    "award_basis_description", "max_award_cap_description", "eligible_population_notes",
    "renewal_conditions", "other_eligibility_criteria", "academic_criteria",
    "residency_restrictions", "scope_note", "formula_method", "assumptions",
}

# Bug fix (schema/transform alignment repair, 2026-09-24): a JSON-schema
# property typed bare `{"type": "object"}` with NO declared `properties` --
# today only $defs.extension_metadata.properties.fields -- is a genuine
# free-form string-keyed map (arbitrary source-backed facts, heterogeneous
# value shapes). Previously field_def() had no branch for this shape and
# fell through to the generic `else`, emitting a plain `type: 'string'`
# Sanity field. The actual transform (04-pipeline/normalized_to_sanity_
# ndjson_v1_2.py) copies the raw JS object straight into that field, and
# Sanity/Studio stringifies an object assigned to a string field as the
# literal text "[object Object]" -- the reported bug. Sanity has no native
# arbitrary-map type, so the schema-compatible, deterministic representation
# is an array of {key, value, value_type} entries (see
# extensionMetadataFieldEntry.js) -- never a hand-stringified blob.
FREEFORM_MAP_ARRAY_TYPE = "extensionMetadataFieldEntry"

# Bug fix (contract repair, 2026-09-24), found via the fixture's deliberate
# coverage of VerificationRecords checking a nested-object-shaped field
# (gb-university-of-oxford-vr-08/-11/-12, checking
# FinancialRequirement.extension_metadata.fields.visa_maintenance_monthly_range,
# itself a {min, max, currency}-shaped dict): exactly three properties in
# the whole schema -- verification_record.proposed_value,
# change_record.previous_value, change_record.proposed_value -- are declared
# as bare `{}` (JSON Schema for "any value, no fixed type"), by design: a
# VerificationRecord/ChangeRecord can be checking a proposed value for ANY
# canonical field, of ANY type (string, number, boolean, null, a nested
# object, or an array). The real dataset confirms every one of those shapes
# actually occurs (bool/list/dict/None/float/str/int, scanned across all
# five institutions' verification-records-v1.2.json). field_def() had no
# branch for a property with no `type` key at all and fell through to the
# generic `else`, emitting a plain Sanity string field -- the exact same
# "[object Object]" risk as FREEFORM_MAP_ARRAY_TYPE above, but worse, since
# this one can also silently truncate a number/boolean/null to Python's
# default str() rendering instead of a script ever actually running (this
# was caught by static schema/transform audit, not yet observed as a live
# Studio symptom -- see sanity-serialization-contract.md).
ANY_VALUE_BOX_TYPE = "anyValueBox"

# Bug fix (contract repair, 2026-09-24): JSON-Schema `"required": [...]` means
# "this key must be present on a valid instance" -- it says nothing about the
# value being non-empty. Sanity's `Rule.required()` means something stricter:
# the value must be non-empty/non-null (an empty string or empty array FAILS
# it). The generator previously treated the two as equivalent, mapping every
# JSON-Schema-required property straight to `Rule.required()`. For
# $defs.extension_metadata specifically, this is a genuine mismatch, not a
# hypothetical one: `note` is legitimately an empty string on the majority of
# real records (nothing to annotate), and `fields` is legitimately an empty
# map on many records too (open-audit confirmed: 28 of the 50 populated
# extension_metadata blocks in the real five-school dataset have `fields`
# empty, `note` empty, or both) -- these are correct, schema-conformant
# "nothing to say" values, not missing data, so requiring them to be
# non-empty produces permanent, meaningless Studio validation redness on a
# large fraction of otherwise-correct documents. This is corrected narrowly,
# for this one $def only (see NON_ENFORCED_REQUIRED below), not by weakening
# `Rule.required()` generation in general -- every other required field in
# the schema keeps it. The complementary fix (05-sanity/generation +
# 04-pipeline transform) omits `extension_metadata` ENTIRELY when it would
# otherwise have literally nothing in it (see
# 09-schema-transform-repair/sanity-serialization-contract.md).
NON_ENFORCED_REQUIRED = {
    "extension_metadata": {"note", "fields"},
}

# Bug fix (schema/transform alignment repair, 2026-09-24): the original
# preview-field heuristic below (gen_document_type) only checked for
# canonical_name/program_name/name/title and otherwise fell back to the bare
# `id` field for BOTH title and subtitle. Combined with the separate `id`-
# stripping bug in the NDJSON transform (now fixed), every document of these
# 10 types rendered as "Untitled" in Studio -- and even once `id` is present,
# a raw canonical-id slug repeated as both title and subtitle is not a useful
# preview. Each override below composes an existing, already-populated
# canonical field (never a new field) into a real title/subtitle, with `id`
# kept as a guaranteed-non-empty fallback via prepare(). Audited against
# every one of the 19 document defs; the 9 not listed here already resolved
# to a genuine name/title/canonical_name/program_name field and were left
# unchanged (see 09-schema-transform-repair/schema-transform-alignment.md).
PREVIEW_OVERRIDES = {
    "program_pathway": {
        "select": {"a": "degree_type_local", "b": "pathway_type", "id": "id"},
        "prepare": "({a, b, id}) => ({ title: a || id, subtitle: [b, id].filter(Boolean).join(' · ') })",
    },
    "applicant_category": {
        "select": {"a": "label", "b": "dimension", "id": "id"},
        "prepare": "({a, b, id}) => ({ title: a || id, subtitle: [b, id].filter(Boolean).join(' · ') })",
    },
    "admissions_requirement": {
        "select": {"a": "curriculum_type", "b": "academic_year", "id": "id"},
        "prepare": "({a, b, id}) => ({ title: a || id, subtitle: [b, id].filter(Boolean).join(' · ') })",
    },
    "decision_plan": {
        "select": {"a": "plan_type", "b": "academic_year", "id": "id"},
        "prepare": "({a, b, id}) => ({ title: a || id, subtitle: [b, id].filter(Boolean).join(' · ') })",
    },
    "cost_profile": {
        "select": {"currency": "currency", "tuition": "tuition_annual", "year": "academic_year", "id": "id"},
        "prepare": "({currency, tuition, year, id}) => ({ title: (tuition !== undefined && tuition !== null) ? [currency, tuition].filter(Boolean).join(' ') : id, subtitle: [year, id].filter(Boolean).join(' · ') })",
    },
    "financial_requirement": {
        "select": {"a": "requirement_type", "currency": "currency", "amount": "amount", "id": "id"},
        "prepare": "({a, currency, amount, id}) => ({ title: a || id, subtitle: (amount !== undefined && amount !== null) ? [currency, amount, id].filter(Boolean).join(' · ') : id })",
    },
    "financial_aid_policy": {
        "select": {"a": "policy_type", "b": "need_aware_or_blind", "id": "id"},
        "prepare": "({a, b, id}) => ({ title: a || id, subtitle: [b, id].filter(Boolean).join(' · ') })",
    },
    "derived_cost_estimate": {
        "select": {"a": "field_name", "b": "value", "id": "id"},
        "prepare": "({a, b, id}) => ({ title: a || id, subtitle: [(b !== undefined && b !== null) ? String(b) : null, id].filter(Boolean).join(' · ') })",
    },
    "verification_record": {
        "select": {"a": "field_checked", "b": "verification_status", "id": "id"},
        "prepare": "({a, b, id}) => ({ title: a || id, subtitle: [b, id].filter(Boolean).join(' · ') })",
    },
    "change_record": {
        "select": {"a": "field", "b": "resolution_status", "id": "id"},
        "prepare": "({a, b, id}) => ({ title: a || id, subtitle: [b, id].filter(Boolean).join(' · ') })",
    },
}

DEF_NAME_TO_SANITY = {}
for _n, (_s, _t) in {**DOCUMENT_TYPES, **OBJECT_TYPES}.items():
    DEF_NAME_TO_SANITY[_n] = _s


def js_str(v):
    return json.dumps(v)


def field_def(name, prop, required_set, def_name):
    lines = []
    is_required = name in required_set
    # The canonical living-cost basis allows null (UNKNOWN/no supplied basis).
    # Sanity represents that absence by omitting this parent; populated bases
    # still retain all three child Rule.required() validations.
    if def_name == "cost_profile" and name == "living_cost_source_basis":
        is_required = False
    nullable = isinstance(prop.get("type"), list) and "null" in prop.get("type", [])

    # $ref to an enum
    if "$ref" in prop:
        ref_name = prop["$ref"].split("/")[-1]
        if ref_name in ENUM_DEFS:
            options = ENUM_DEFS[ref_name]
            lines.append(f"    defineField({{\n      name: '{name}',\n      title: '{_title(name)}',\n      type: 'string',\n      options: {{ list: {js_str(options)} }},")
        elif ref_name in OBJECT_TYPES:
            sanity_type = OBJECT_TYPES[ref_name][0]
            lines.append(f"    defineField({{\n      name: '{name}',\n      title: '{_title(name)}',\n      type: '{sanity_type}',")
        elif ref_name == "url":
            lines.append(f"    defineField({{\n      name: '{name}',\n      title: '{_title(name)}',\n      type: 'url',")
        else:
            lines.append(f"    defineField({{\n      name: '{name}',\n      title: '{_title(name)}',\n      type: 'string', // unresolved $ref: {ref_name}")
    elif "type" not in prop and "$ref" not in prop and "enum" not in prop:
        # Bare `{}` -- genuinely untyped "any value". See ANY_VALUE_BOX_TYPE comment above.
        lines.append(f"    defineField({{\n      name: '{name}',\n      title: '{_title(name)}',\n      type: '{ANY_VALUE_BOX_TYPE}', // untyped-any in JSON Schema -> deterministic value/value_type box, never a stringified value")
    elif prop.get("type") == "object" and not prop.get("properties"):
        # Free-form string-keyed map (see FREEFORM_MAP_ARRAY_TYPE comment above).
        lines.append(f"    defineField({{\n      name: '{name}',\n      title: '{_title(name)}',\n      type: 'array',\n      of: [{{ type: '{FREEFORM_MAP_ARRAY_TYPE}' }}], // free-form map -> deterministic key/value/value_type entries, never a stringified object")
    elif prop.get("type") == "array":
        items = prop.get("items", {})
        if name in LIST_REF_FIELDS:
            target = LIST_REF_FIELDS[name]
            lines.append(f"    defineField({{\n      name: '{name}',\n      title: '{_title(name)}',\n      type: 'array',\n      of: [{{ type: 'reference', to: [{{ type: '{target}' }}] }}],")
        elif "$ref" in items:
            ref_name = items["$ref"].split("/")[-1]
            if ref_name in OBJECT_TYPES:
                sanity_type = OBJECT_TYPES[ref_name][0]
                lines.append(f"    defineField({{\n      name: '{name}',\n      title: '{_title(name)}',\n      type: 'array',\n      of: [{{ type: '{sanity_type}' }}],")
            else:
                lines.append(f"    defineField({{\n      name: '{name}',\n      title: '{_title(name)}',\n      type: 'array',\n      of: [{{ type: 'string' }}],")
        else:
            lines.append(f"    defineField({{\n      name: '{name}',\n      title: '{_title(name)}',\n      type: 'array',\n      of: [{{ type: 'string' }}],")
    elif name in SIMPLE_REF_FIELDS:
        target = SIMPLE_REF_FIELDS[name]
        lines.append(f"    defineField({{\n      name: '{name}',\n      title: '{_title(name)}',\n      type: 'reference',\n      to: [{{ type: '{target}' }}],")
    elif name in POLYMORPHIC_REF_FIELDS:
        all_doc_types = [v[0] for v in DOCUMENT_TYPES.values()]
        lines.append(f"    defineField({{\n      name: '{name}',\n      title: '{_title(name)}',\n      type: 'reference',\n      to: {js_str([{'type': t} for t in all_doc_types])}, // polymorphic: 'EntityType:id' resolved at import time")
    elif prop.get("type") in ("number", "integer") or (
        isinstance(prop.get("type"), list) and any(t in ("number", "integer") for t in prop["type"])
        and not any(t == "string" for t in prop["type"])
    ):
        lines.append(f"    defineField({{\n      name: '{name}',\n      title: '{_title(name)}',\n      type: 'number',")
    elif prop.get("type") == "boolean" or (
        isinstance(prop.get("type"), list) and "boolean" in prop["type"]
    ):
        lines.append(f"    defineField({{\n      name: '{name}',\n      title: '{_title(name)}',\n      type: 'boolean',")
    elif isinstance(prop.get("type"), list) and "number" in prop["type"] and "string" in prop["type"]:
        # mixed string-or-number (e.g. selection_criterion.weight) -- Sanity has no
        # native union primitive; model as a string field, documented in
        # validation-rules.md, since the source data itself is one-or-the-other per record.
        lines.append(f"    defineField({{\n      name: '{name}',\n      title: '{_title(name)}',\n      type: 'string', // source field is string|number|null -- see validation-rules.md")
    else:
        field_type = "text" if name in LONG_TEXT_FIELDS else "string"
        lines.append(f"    defineField({{\n      name: '{name}',\n      title: '{_title(name)}',\n      type: '{field_type}',")

    if is_required and not nullable:
        lines.append("      validation: (Rule) => Rule.required(),")
    lines.append("    }),")
    return "\n".join(lines)


def _title(name):
    return " ".join(w.capitalize() for w in name.replace("_ref", "").replace("_", " ").split())


def gen_document_type(def_name, sanity_type, title):
    node = DEFS[def_name]
    required = set(node.get("required", []))
    props = node.get("properties", {})
    field_lines = []
    for pname, pdef in props.items():
        field_lines.append(field_def(pname, pdef, required, def_name))
    fields_str = "\n".join(field_lines)

    if def_name in PREVIEW_OVERRIDES:
        override = PREVIEW_OVERRIDES[def_name]
        select_str = json.dumps(override["select"])
        preview_block = f"""preview: {{
    select: {select_str},
    prepare: {override["prepare"]},
  }},"""
    else:
        preview_field = "id"
        if "canonical_name" in props: preview_field = "canonical_name"
        elif "program_name" in props: preview_field = "program_name"
        elif "name" in props: preview_field = "name"
        elif "title" in props: preview_field = "title"
        preview_block = f"""preview: {{
    select: {{ title: '{preview_field}', subtitle: 'id' }},
  }},"""

    content = f"""// AUTO-GENERATED from evidapath-schema-v1.2.json ($defs.{def_name}) by
// 05-sanity/generation/gen_schema_files.py. Regenerate rather than
// hand-editing if the JSON Schema changes -- keeps the two in lockstep.
import {{ defineType, defineField }} from 'sanity'

export default defineType({{
  name: '{sanity_type}',
  title: '{title}',
  type: 'document',
  fields: [
{fields_str}
  ],
  {preview_block}
}})
"""
    return content


def gen_object_type(def_name, sanity_type, title):
    node = DEFS[def_name]
    required = set(node.get("required", [])) - NON_ENFORCED_REQUIRED.get(def_name, set())
    props = node.get("properties", {})
    field_lines = []
    for pname, pdef in props.items():
        field_lines.append(field_def(pname, pdef, required, def_name))
    fields_str = "\n".join(field_lines)

    content = f"""// AUTO-GENERATED from evidapath-schema-v1.2.json ($defs.{def_name}) by
// 05-sanity/generation/gen_schema_files.py. Embedded object type -- has no
// own Sanity document lifecycle; nests inside the document types that
// reference it (see sanity-content-model.md).
import {{ defineType, defineField }} from 'sanity'

export default defineType({{
  name: '{sanity_type}',
  title: '{title}',
  type: 'object',
  fields: [
{fields_str}
  ],
}})
"""
    return content


def main():
    doc_dir = os.path.join(OUT_DIR, "document-types")
    obj_dir = os.path.join(OUT_DIR, "object-types")
    os.makedirs(doc_dir, exist_ok=True)
    os.makedirs(obj_dir, exist_ok=True)

    index_doc_lines = []
    for def_name, (sanity_type, title) in DOCUMENT_TYPES.items():
        content = gen_document_type(def_name, sanity_type, title)
        path = os.path.join(doc_dir, f"{sanity_type}.js")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        index_doc_lines.append(f"import {sanity_type} from './document-types/{sanity_type}'")

    index_obj_lines = []
    for def_name, (sanity_type, title) in OBJECT_TYPES.items():
        content = gen_object_type(def_name, sanity_type, title)
        path = os.path.join(obj_dir, f"{sanity_type}.js")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        index_obj_lines.append(f"import {sanity_type} from './object-types/{sanity_type}'")

    # Not derived from a $defs entry -- this is the deterministic key/value/
    # value_type entry shape that extension_metadata.fields (a free-form
    # string-keyed map with no fixed properties) is represented as, since
    # Sanity has no native arbitrary-map type. See FREEFORM_MAP_ARRAY_TYPE
    # above and 09-schema-transform-repair/schema-transform-alignment.md.
    entry_content = """// AUTO-GENERATED by 05-sanity/generation/gen_schema_files.py. Not derived
// from a $defs entry -- extension_metadata.fields is a free-form,
// string-keyed map (arbitrary source-backed facts of heterogeneous value
// shape), and Sanity has no native arbitrary-map field type. This is the
// deterministic entry shape the transform (04-pipeline/
// normalized_to_sanity_ndjson_v1_2.py) converts each map entry into: one
// entry per original key, `value` always a string (the value as-is when the
// original was already a string, or its canonical JSON serialization
// otherwise), and `value_type` telling a reader which case it is so the
// original shape is always recoverable -- never a lossy stringified object.
import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'extensionMetadataFieldEntry',
  title: 'Extension Metadata Field Entry',
  type: 'object',
  fields: [
    defineField({
      name: 'key',
      title: 'Key',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'value',
      title: 'Value',
      type: 'text',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'value_type',
      title: 'Value Type',
      type: 'string',
      options: { list: ['string', 'json'] },
      validation: (Rule) => Rule.required(),
    }),
  ],
  preview: {
    select: { title: 'key', subtitle: 'value' },
  },
})
"""
    with open(os.path.join(obj_dir, "extensionMetadataFieldEntry.js"), "w", encoding="utf-8") as f:
        f.write(entry_content)
    index_obj_lines.append("import extensionMetadataFieldEntry from './object-types/extensionMetadataFieldEntry'")

    # Not derived from a $defs entry -- see ANY_VALUE_BOX_TYPE comment above.
    any_value_box_content = """// AUTO-GENERATED by 05-sanity/generation/gen_schema_files.py. Not derived
// from a $defs entry -- verification_record.proposed_value and
// change_record.previous_value/proposed_value are declared in the JSON
// Schema as bare `{}` (untyped: "any value"), since a VerificationRecord or
// ChangeRecord can be checking a proposed value for any canonical field, of
// any type. Sanity has no native "any" field type, so this is the
// deterministic box every such value is wrapped in: `value` is always a
// string (the value's own text when it was already a string, or its
// canonical JSON serialization otherwise), and `value_type` records which
// primitive case applies (including 'null', since a verification record
// asserting "the correct value is genuinely absent" is meaningful domain
// data, not missing data -- it is never pruned the way an ordinary null is
// elsewhere in this pipeline).
import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'anyValueBox',
  title: 'Any Value',
  type: 'object',
  fields: [
    defineField({
      name: 'value',
      title: 'Value',
      type: 'text',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'value_type',
      title: 'Value Type',
      type: 'string',
      options: { list: ['string', 'number', 'boolean', 'json', 'null'] },
      validation: (Rule) => Rule.required(),
    }),
  ],
  preview: {
    select: { title: 'value', subtitle: 'value_type' },
  },
})
"""
    with open(os.path.join(obj_dir, "anyValueBox.js"), "w", encoding="utf-8") as f:
        f.write(any_value_box_content)
    index_obj_lines.append("import anyValueBox from './object-types/anyValueBox'")

    all_names = [v[0] for v in DOCUMENT_TYPES.values()] + [v[0] for v in OBJECT_TYPES.values()] + ["extensionMetadataFieldEntry", "anyValueBox"]
    schema_js = "// AUTO-GENERATED index -- assembles all document and object types for sanity.config.js\n"
    schema_js += "\n".join(index_doc_lines) + "\n\n" + "\n".join(index_obj_lines) + "\n\n"
    schema_js += "export const schemaTypes = [\n  " + ",\n  ".join(all_names) + ",\n]\n"
    with open(os.path.join(OUT_DIR, "schema.js"), "w", encoding="utf-8") as f:
        f.write(schema_js)

    print(f"Generated {len(DOCUMENT_TYPES)} document-types, {len(OBJECT_TYPES) + 2} object-types, and schema.js index.")


if __name__ == "__main__":
    main()
