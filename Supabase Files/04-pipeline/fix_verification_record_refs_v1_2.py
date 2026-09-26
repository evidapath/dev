#!/usr/bin/env python3
"""
EvidaPath pipeline -- V1.2 VerificationRecord.record_ref cleanup.

Fixes VerificationRecord.record_ref values that still point at a retired
V1.1 entity which this V1.2 migration replaced with a new canonical entity
of a DIFFERENT type (a CostProfile retired in favor of a FinancialRequirement,
in every currently-known case -- see RETIRED_REF_MAP below). This is
reference cleanup only: it never touches verification_status, source_refs,
blocking_status, timestamps, or the substance of conflict_or_limitation_notes
-- it only repoints record_ref at the record that now carries the same
underlying fact, and appends one auditable migration annotation explaining
why.

WHY THIS IS SAFE: in every mapped case, the retired record and its
replacement were confirmed (by direct inspection, not inference) to
describe the exact same underlying fact -- same amount/mechanism, same
source_refs, same institution -- with only the entity TYPE having changed
during the V1.1 -> V1.2 migration (see each institution's migration-report.md
"Structural fixes applied" section, and 05-sanity/README.md's "Known
limitation" note this script resolves).

RETIRED_REF_MAP is intentionally hardcoded and small: it is not a general
"fix any dangling reference" tool. Adding an entry requires the same
direct-inspection confirmation this script's authors did, not blind
inference from naming similarity.

Usage:
    python3 fix_verification_record_refs_v1_2.py <verification-records-v1.2.json> --out <output-path>

Idempotent: re-running against an already-fixed file makes no further
changes (record_ref values already at their mapped target are left alone,
and the migration annotation is not duplicated if already present).
"""
import argparse
import json
import sys

# old "EntityType:id" -> new "EntityType:id". Confirmed by direct inspection
# of each institution's migration-report.md and its records-v1.2.json
# FinancialRequirement record (not inferred from ID similarity alone).
RETIRED_REF_MAP = {
    "CostProfile:de-tu-munich-cost-non-eu-immigration-liquidity":
        "FinancialRequirement:de-tu-munich-finreq-blocked-account",
    "CostProfile:gb-university-of-oxford-cost-visa-maintenance-funds":
        "FinancialRequirement:gb-university-of-oxford-finreq-visa-maintenance",
}

MIGRATION_NOTE_TEMPLATE = (
    " [V1.2 reference migration: record_ref updated from {old_ref} to {new_ref} "
    "because the underlying factual record changed entity type during the "
    "V1.1-to-V1.2 migration (CostProfile retired in favor of FinancialRequirement); "
    "the verification claim itself is unchanged and continues to apply to the "
    "same underlying fact, now carried by the replacement record.]"
)


def fix_verification_records(vr_data, ref_map=RETIRED_REF_MAP):
    changes = []
    for vr in vr_data.get("verification_records", []):
        old_ref = vr.get("record_ref")
        if old_ref not in ref_map:
            continue
        new_ref = ref_map[old_ref]
        note_text = MIGRATION_NOTE_TEMPLATE.format(old_ref=old_ref, new_ref=new_ref)
        already_annotated = note_text.strip() in (vr.get("conflict_or_limitation_notes") or "")
        vr["record_ref"] = new_ref
        if not already_annotated:
            vr["conflict_or_limitation_notes"] = (vr.get("conflict_or_limitation_notes") or "").rstrip() + note_text
        changes.append({
            "verification_record_id": vr.get("id"),
            "old_record_ref": old_ref,
            "new_record_ref": new_ref,
            "verification_status_preserved": vr.get("verification_status"),
            "verifier_pass_timestamp_preserved": vr.get("verifier_pass_timestamp"),
            "source_refs_preserved": vr.get("source_refs"),
            "blocking_status_preserved": vr.get("blocking_status"),
        })
    return vr_data, changes


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("verification_records_path")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    with open(args.verification_records_path, encoding="utf-8") as f:
        vr_data = json.load(f)

    fixed_data, changes = fix_verification_records(vr_data)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(fixed_data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    if changes:
        print(f"Fixed {len(changes)} VerificationRecord(s) in {args.verification_records_path}:")
        for c in changes:
            print(f"  {c['verification_record_id']}: {c['old_record_ref']} -> {c['new_record_ref']}")
    else:
        print(f"No matching retired references found in {args.verification_records_path} (already clean, or none apply).")

    sys.exit(0)


if __name__ == "__main__":
    main()
