# EvidaPath V1.2 → Sanity serialization contract

**Status: normative.** This is the contract the transform
(`04-pipeline/normalized_to_sanity_ndjson_v1_2.py` +
`05-sanity/import/resolve_references.py`) and the generated Sanity schema
(`05-sanity/generation/gen_schema_files.py` → `05-sanity/{document,object}-
types/*.js`) are required to satisfy. Every rule below is enforced,
automatically, by `09-schema-transform-repair/validate_sanity_ndjson_v1_2.py`
— a rule stated here with no corresponding automated check is incomplete.

No rule in this document changes the canonical JSON Schema
(`02-schema-design/evidapath-schema-v1.2.json`) or any source fact. This is
purely the adapter contract between an already-valid canonical record and a
valid Sanity document.

## The pipeline

```
CANONICAL V1.2 (records-v1.2.json, JSON-Schema-valid)
    → 04-pipeline/normalized_to_sanity_ndjson_v1_2.py   (canonical record -> Sanity-shaped doc)
    → 05-sanity/import/resolve_references.py            (canonical-ID strings -> {_type: reference, _ref})
    → SANITY SCHEMA (05-sanity/{document,object}-types/*.js, generated from the same JSON Schema)
    → SANITY DOCUMENT (the .ndjson line actually imported)
```

The schema and the transform are generated/maintained from the same JSON
Schema `$defs` and must stay in lock-step; `gen_schema_files.py` regenerates
the schema files whenever `evidapath-schema-v1.2.json` changes, and this
contract is what the transform script implements against that regenerated
schema.

## Rule 1 — Canonical missing / unknown

**Canonical:** a field the pipeline never found evidence for is `null`,
with `verification_status: "UNKNOWN"` (or `VERIFIED_ABSENT` when the
absence itself was verified, or `CONFLICT` when sources disagree) — this is
schema-correct, deliberate, and never guessed.

**Sanity:** the key is **omitted entirely**, at every nesting depth,
recursively, in the final Sanity document. Sanity's own field types
(`reference`, `array`, `object`) do not have a valid "explicit null" shape,
and Studio can show a broken/blank editor state for one; omitting the key
is the shape Sanity actually expects for "no value," and is exactly
equivalent in meaning to the canonical `null`.

**Exception — fields where `null` is itself the verified finding, not an
absence of data about the field:** `VerificationRecord.proposed_value` and
`ChangeRecord.{previous_value,proposed_value}` can legitimately assert "the
correct value for this field is nothing" (a `VERIFIED_ABSENT` finding). For
these three fields ONLY, `null` is wrapped into the `anyValueBox` shape
(Rule 9) with `value_type: "null"` rather than pruned — pruning it would
delete a required field's only value and misrepresent a verified finding as
missing data.

**Empty is not null.** `[]` (e.g. `AdmissionsRequirement.required_subjects:
[]`, meaning "verified: no subjects required") and `""` are left exactly as
they are — this schema deliberately distinguishes a verified-empty finding
from an unknown one, and Rule 1 must never collapse that distinction.

## Rule 2 — Canonical explicit business ID

**Canonical:** every record has an `id` (its stable, human-legible,
country-prefixed canonical identifier — e.g.
`ae-nyu-abu-dhabi-curriculum-a-level`).

**Sanity:** kept, verbatim, as the document's own `id` field — every
generated Sanity document type declares this field independently of `_id`
(below), and every Sanity document created by this pipeline MUST have it
non-empty. This is not derived from or interchangeable with `_id`; the two
serve different purposes (see Rule 3) and both must be present.

## Rule 3 — Sanity document `_id`

**Strategy:** `drafts.<sanityType>-<idPrefix><canonicalId>`, where
`idPrefix` is `""` for globally-unique canonical IDs (Country, City,
University, Campus, Program, ApplicantCategory, AdmissionStage,
AdmissionsRequirement, DecisionPlan, CostProfile, FinancialRequirement,
Scholarship, FinancialAidPolicy, ProgramPathway, College,
DerivedCostEstimate — all country-prefixed by construction) and
`"<institutionSlug>-"` for the three institution-scoped types
(SourceRecord, VerificationRecord, ChangeRecord), whose own canonical IDs
(`src-01`, `vr-01`, …) are only unique within one institution's own run.

**Draft, never published, by this pipeline.** Every `_id` this pipeline
produces is `drafts.`-prefixed; nothing it writes is ever a bare
(published) `_id`. This is deliberate — see `import-readme.md` — and
publishing is a separate, later, human action this pipeline never performs
or assumes.

**Deterministic and idempotent.** The same canonical record always produces
the same `_id`, run after run — this is what makes `--replace`-by-ID a safe,
idempotent re-import (Rule 3 is what Rule 8's import command depends on).

## Rule 4 — Reference (single)

**Canonical:** a string, either a bare canonical ID (`university_ref:
"nl-tu-delft"`) for a single-target-type field, or an `"EntityType:id"`
string (`record_ref: "Program:ae-nyu-abu-dhabi-computer-science-bs"`) for a
polymorphic field that can point at more than one document type.

**Sanity:**
```json
{ "_type": "reference", "_ref": "drafts.<sanityType>-<idPrefix><canonicalId>" }
```
`<sanityType>` is looked up from a fixed field-name → target-type table for
single-target fields (`SIMPLE_REF_FIELDS`), or parsed from the
`"EntityType:"` prefix for polymorphic fields (`record_ref`, `source_ref`).
The target type is never guessed or inferred from the ID string alone.

**Resolution happens on the FULL DOCUMENT TREE, not just top-level keys.**
A reference field nested inside an embedded object (e.g.
`Program.testing_policy.source_refs`) is resolved by the exact same rule as
a top-level one — `resolve_references.py`'s traversal is fully recursive.
This was a real, found-and-fixed bug (a top-level-only traversal silently
missed one nested field); the contract states the recursive requirement
explicitly so it can't regress silently again.

**A reference that cannot be resolved is never silently dropped or left as
a bare string in the shipped file.** `resolve_references.py` logs it and
exits non-zero; the pipeline treats a non-zero exit as a hard stop, not a
warning to route around.

## Rule 5 — Reference (array of references)

**Canonical:** a list of bare canonical-ID strings (`source_refs: ["src-01",
"src-02"]`).

**Sanity:** each element becomes the same `{_type: "reference", _ref: ...}`
shape as Rule 4 — never a bare string left in the array. No `_key` is
required on a reference array item beyond what Sanity itself may want for
its own array machinery; this pipeline does not currently add one (open
item — see "Known gaps," below), since none of the five institutions'
reference arrays have shown array-reordering symptoms.

## Rule 6 — Embedded object (single)

**Canonical:** a nested object matching one of the schema's non-document
`$defs` (e.g. `living_cost_source_basis`, `progression_requirement`,
`testing_policy`, `estimated_living_costs_monthly_range` /
`monthly_range`).

**Sanity:** the object is tagged with its Sanity object `_type` (e.g.
`"_type": "livingCostSourceBasis"`) so Studio/GROQ can resolve which object
schema applies. When the canonical value is `null` (field genuinely not
applicable), Rule 1 applies instead — the whole field is omitted, never
emitted as `{"_type": "...", ...all-fields-null}`.

## Rule 7 — Embedded object (array of objects)

**Canonical:** an array whose items match a non-document `$def` (e.g.
`language_requirement`, `test_requirement`, `line_item`,
`accepted_assessment`, `selection_criterion`, `application_requirement`).

**Sanity:** every item is tagged with its Sanity object `_type`, AND given
a `_key` that is unique within that array. `_key` is derived from a SHA-1
of the item's own canonical (`sort_keys=True`) JSON content, truncated to
12 hex characters — **never random**, so re-running the transform against
unchanged input reproduces the identical `_key` on the identical item
(verified: byte-identical output across repeated runs). The rare case of
two structurally-identical items in the same array is disambiguated with a
`-1`, `-2`, … suffix on the colliding hash.

## Rule 8 — Free-form string-keyed map (`extension_metadata.fields`)

**Canonical:** `extension_metadata.fields` is declared as a bare `{"type":
"object"}` with **no** fixed `properties` — genuinely arbitrary
`{key: value}` pairs, where `value` itself can be a string, a number, a
nested object, or an array, by design (real examples of all of these exist
in the five-school dataset).

**Sanity has no native arbitrary-map type**, so this is represented as an
array of typed entries (Sanity object type `extensionMetadataFieldEntry`):

```json
{
  "_type": "extensionMetadataFieldEntry",
  "_key": "<the map key itself>",
  "key": "<the map key itself>",
  "value": "<string>",
  "value_type": "string" | "json"
}
```

`value_type: "string"` when the original value was already a string (the
common case — the large majority of real entries); `value_type: "json"`
when it wasn't, in which case `value` is that value's canonical
(`sort_keys=True`) JSON serialization, always exactly recoverable with
`JSON.parse`. **Never** a Python/JS `str()`/implicit-toString
stringification — that is precisely the `"[object Object]"` bug this rule
exists to prevent. `_key` uses the map key verbatim (already unique within
one `fields` map by construction), not a content hash — more meaningful
than an opaque digest, and still fully deterministic.

## Rule 9 — Untyped "any value" (`proposed_value` / `previous_value`)

**Canonical:** exactly three properties in the whole schema —
`VerificationRecord.proposed_value`, `ChangeRecord.previous_value`,
`ChangeRecord.proposed_value` — are declared as bare `{}` (JSON Schema for
"any value, no fixed type"), because a verification or change record can be
checking a proposed value for *any* canonical field, of *any* type. Real
data confirms every JSON primitive shape occurs: string, number, boolean,
null, object, and array.

**Sanity has no native "any" type either**, so this is represented as a
single typed box (Sanity object type `anyValueBox`):

```json
{ "_type": "anyValueBox", "value": "<string>", "value_type": "string" | "number" | "boolean" | "json" | "null" }
```

`value` is always a string: the value verbatim when it was already a
string, `json.dumps(v)` for a number, `"true"`/`"false"` for a boolean, the
canonical JSON serialization for an object/array, or `""` when the value is
`null` (with `value_type: "null"` carrying the actual meaning — see the
Rule 1 exception above for why this is wrapped rather than pruned). Every
one of these is fully recoverable from `value` + `value_type` alone —
again, never an implicit stringification.

## Rule 10 — `extension_metadata`: omit when contentless

**Canonical:** `extension_metadata.note` and `.fields` are both marked
`"required"` in the JSON Schema, but JSON-Schema `required` means only "the
key must be present" — it says nothing about the value being non-empty.
Real data legitimately has `note: ""` and/or `fields: {}` on a large
fraction of records (28 of 50 populated `extension_metadata` blocks in the
five-school dataset: 7 fully empty, 21 with note-only content and an empty
`fields` map) — this is "nothing to annotate here," a correct and
meaningful value, not missing data.

**Sanity's `Rule.required()` is stricter than JSON-Schema `required`**: it
fails on an empty string or empty array, not just on an absent key. Mapping
every JSON-Schema-required property straight to `Rule.required()` (as the
generator did before this contract) therefore produces permanent, false
"required field" redness in Studio on every one of those 28 records, for
information that was never missing in the first place.

**The fix, two parts, applied together:**
1. In the generated Sanity schema, `note` and `fields` on the
   `extensionMetadata` object type do **not** carry `Rule.required()` (a
   narrow, named, evidence-based exception —
   `NON_ENFORCED_REQUIRED` in `gen_schema_files.py` — not a general
   weakening of `Rule.required()` generation, which every other required
   field in the schema keeps).
2. When the resulting `extension_metadata` block would have **no**
   information at all — blank `note`, empty `fields`, and no
   `proposed_v1_2_fields` — the whole `extension_metadata` property is
   **omitted** from the document, exactly like any other absent optional
   field (Rule 1's own principle, applied to this one object as a whole
   rather than field-by-field).

A record with a real `note` but an empty `fields` map (the 21-record case)
now keeps `extension_metadata` with `fields: []` and no validation
complaint, since `fields` is no longer `Rule.required()`.

## Rule 11 — Unexpected fields and enums

Every top-level key on a Sanity document, other than the pipeline's own
`_id`/`_type`/`id`/`_evidapathMeta`, must be a property the JSON Schema's
own `$def` for that entity type declares — no field invented by the
transform, no field silently dropped by the schema generator that the
transform still emits. Every enum-typed field's value must be a member of
that field's JSON-Schema `enum` list. Both are checked directly against the
JSON Schema itself (not a hand-maintained copy of its vocabulary) by the
validator, so this rule can't drift out of sync with schema changes.

## Known gaps (disclosed, not hidden)

- **Rule 5's reference arrays have no `_key`.** No symptom has been
  observed from this in the real dataset (these arrays are always
  regenerated wholesale by re-running the pipeline, never hand-reordered in
  Studio), but a future Studio-side manual reorder of a `source_refs` array
  could behave unexpectedly without one. Flagged as a candidate follow-up,
  not fixed in this pass since it has no evidence behind it yet (per the
  "don't guess" standing instruction).
- **No live Sanity schema compile/typecheck was run.** This environment
  has no Sanity CLI or the user's actual Studio `node_modules` installed;
  "TypeScript check" in this pass means `node --check` (ES-module syntax
  validity) on every generated `.js` file (31/31 pass), not a full Sanity
  schema type-check. A real `sanity schema validate` (or opening the
  Studio locally) is the outstanding, stronger check — see the final
  report's "what's next" section.
- **Rule about draft/published ID collisions (contract question D) is not
  testable from static files at all** — see
  `reference_root_cause_audit.py`'s own docstring and the final report.
