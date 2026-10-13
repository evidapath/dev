#!/usr/bin/env python3
"""
Apply verified data corrections to the 5-university set in Sanity (project jxwrtsiz,
dataset staging). Only corrections that were CHECKED against a primary source are
included (see fact-checks/5-uni-field-matrix.md). Non-destructive field patches;
patches both published doc and its draft so Studio agrees.

Corrections in this batch (verified 2026-10-13):
  1. TU Munich deadline was stale (WS 2026/27 / 2026-07-15 — that cycle has passed).
     The deadline is annually July 15; bump to the current applicant cycle
     WS 2027/28 / 2027-07-15 (matches the other 4 unis, all 2027 entry).
  2. Oxford decision release date is published as 12 Jan 2027 but was null.

NOT in this batch (need their own source pass, documented in the matrix):
  Toronto A-Level required subjects, Pearson/National award amounts, TU Delft
  application docs, TU Munich VPD requirement_type. The van Effen MSc-only fix was
  done in the APP (scholarship degree-level filter), not here.

Usage:
  python3 apply_data_corrections.py            # dry run
  SANITY_TOKEN=<write-token> python3 apply_data_corrections.py --execute
"""
import json, os, sys, subprocess, tempfile

PROJECT = "jxwrtsiz"
DATASET = "staging"

# doc _id -> {field: value}
CORRECTIONS = {
    "decisionPlan-de-tu-munich-decisionplan-ws2026-27": {
        "application_deadline": "2027-07-15",
        "academic_year": "Winter Semester 2027/28",
    },
    "decisionPlan-gb-university-of-oxford-decisionplan-2027": {
        "decision_release_date": "2027-01-12",
    },
}


def get_token():
    t = os.environ.get("SANITY_TOKEN")
    if not t:
        sys.exit("SANITY_TOKEN (write token) required for --execute. Dry run only without it.")
    return t.strip()


def curl(args):
    p = subprocess.run(["curl", "-sS", "--fail-with-body", *args], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"curl failed ({p.returncode}): {p.stderr or p.stdout}")
    return p.stdout


def main():
    execute = "--execute" in sys.argv
    print(f"target: {PROJECT}/{DATASET} | documents to patch: {len(CORRECTIONS)}")
    for doc_id, fields in CORRECTIONS.items():
        print(f"  {doc_id}")
        for k, v in fields.items():
            print(f"      {k} -> {v}")
    if not execute:
        print("\nDRY RUN — no writes. Re-run with SANITY_TOKEN set and --execute.")
        return
    token = get_token()
    muts = []
    for doc_id, fields in CORRECTIONS.items():
        muts.append({"patch": {"id": doc_id, "set": fields}})
        muts.append({"patch": {"id": f"drafts.{doc_id}", "set": fields}})
    body = json.dumps({"mutations": muts})
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tf:
        tf.write(body); payload = tf.name
    url = f"https://{PROJECT}.api.sanity.io/v2021-06-07/data/mutate/{DATASET}?returnIds=false"
    out = curl(["-X", "POST", "-H", f"Authorization: Bearer {token}",
                "-H", "Content-Type: application/json", "--data-binary", f"@{payload}", url])
    os.unlink(payload)
    res = json.loads(out)
    print(f"\nPATCHED | transactionId {res.get('transactionId')}")


if __name__ == "__main__":
    main()
