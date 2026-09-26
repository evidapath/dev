# Empty optional object repair — offline audit

## Root cause and scope

The current local import artifact does NOT contain the reported empty living-cost object.
All 399 staging-ready documents and all 399 canonical source records were audited.
Toronto's three CostProfiles contain canonical `living_cost_source_basis: null`;
the existing transform correctly omits that property. The generated Studio schema
nevertheless applied `Rule.required()` to the parent. The generator checked
nullability only on the property's inline definition, missing nullability behind
`$ref: #/$defs/living_cost_source_basis` (`type: ["object", "null"]`).

With explicit approval, only that Sanity parent is now optional. Its children
`kind`, `description`, and `administering_body` remain required. Canonical JSON,
UNKNOWN semantics, references, IDs, previews, and imported artifacts are unchanged.

A separate latent transform gap tagged `{}` or all-null dictionaries with `_type`
instead of omitting them. The new schema-aware guard omits empty optional or
nullable objects and rejects empty required objects. The output validator rejects
present empty objects. Populated/incomplete objects retain normal child validation.
The existing extension metadata adapter is unchanged. Zero, false, UNKNOWN,
meaningful empty arrays, and arbitrary verification value boxes are preserved.

## Counts

- Staging-ready NDJSON: 399 documents, 10 CostProfiles, **0 empty nested objects**.
- CostProfiles affected by the parent-required mismatch: **3 Toronto profiles**.
- Empty living-cost basis objects in NDJSON: **0**; bases already absent: **3**.
- Other optional empty objects in canonical source: `extension_metadata` on
  Country **1**, City **1**, ApplicantCategory **5**. All **7** are already omitted
  by the existing transform; none needs cleanup in the audited artifact.
- Empty canonical `extension_metadata.fields` maps: Country **1**, City **1**,
  University **3**, Campus **2**, ApplicantCategory **5**, AdmissionStage **8**,
  CostProfile **3**, Scholarship **3**, FinancialAidPolicy **2** = **28**.
  These are free-form maps, not additional empty optional typed objects. Seven
  belong to the omitted blocks above; the other 21 remain legitimate empty
  arrays inside populated metadata. No change was made to their serialization.
- Two populated Delft bases have blank `administering_body`. They remain intact;
  their child-required validation remains in effect. No facts were invented.

Exact document IDs and artifact SHA-256 are in `empty-optional-object-audit.json`.
These counts describe local source/import files, not a fresh export of live staging.
No live dataset was read or changed.

## Verification

Seven regression tests cover absent/empty/typed-only/all-null bases, populated and
partial bases, other optional objects, zero/false/UNKNOWN/empty arrays, arbitrary
value boxes, required-object rejection, validator rejection, nonmutation, and
repeatable output. All 399 regenerated documents are semantically identical to
the existing raw import artifact; the staging-ready artifact passes the updated
contract validator. No existing NDJSON was rewritten.

## Cleanup / re-import recommendation (NOT executed)

**No re-import is required for the audited artifact.** Restart/reload Studio with
the corrected local schema. The three Toronto bases are already omitted.

If the live dataset still shows an empty basis, inspect the raw draft first using
project `jxwrtsiz`, dataset `staging`, perspective `raw` and this GROQ query:

```groq
*[_type == "costProfile" && _id in path("drafts.**")]{
  _id, _rev, id, living_cost_source_basis
}
```

For each returned document, require a present object with no meaningful values
before preparing a cleanup. Do not clean populated partial objects, including the
Delft records. A metadata-only object (`_type` / `_key`) is empty. An absent field
already needs no action. UNKNOWN, zero, false, and meaningful arrays are values.

The exact recommended mutation is a revision-guarded unset of that one field,
on the specific confirmed draft ID. Example payload (only after raw inspection):

```json
{
  "mutations": [{
    "patch": {
      "id": "drafts.costProfile-ca-university-of-toronto-cost-domestic-ontario",
      "ifRevisionID": "<fresh _rev from inspected draft>",
      "unset": ["living_cost_source_basis"]
    }
  }]
}
```

Send that payload to the Sanity data mutation API for project `jxwrtsiz`, dataset
`staging`, only when cleanup is authorized. With the installed JS client, the
same operation is `client.patch(draftId).ifRevisionId(rev).unset(['living_cost_source_basis']).commit()`.
If the revision changed, re-read and re-check emptiness; do not blindly retry.
Re-read the draft and confirm property absence afterward. This does not publish.
No mutation was sent, and no executable import/cleanup was run in this task.

A full 399-document replacement import is unnecessary. If import is chosen
instead of an unset, export/read the latest affected drafts, remove only the empty
property, retain exact `drafts.*` IDs and weak base-ID references, validate the
resulting draft-only NDJSON, and use `sanity dataset import <reviewed-file> staging
--replace` from this Studio. Avoid using the historical full batch to overwrite
subsequent Studio edits. This alternative is documentation only.
