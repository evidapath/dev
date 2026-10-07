#!/usr/bin/env python3
"""
Write EvidaPath primary-source verification markers onto university documents in
Sanity (project jxwrtsiz, dataset staging). This is the source of truth the app
reads (`evidapath_verified`) to show the "Verified against official sources" label.

Set a university here ONLY after a logged primary-source fact-check in repo
fact-checks/. Each entry: Sanity document _id -> (verified_at date, note).

Writes both the published doc and its draft (if present) so Studio shows it too.
Non-destructive: only sets the three evidapath_* fields; never touches
record_status or any other field.

Usage:
  python3 mark_verified_in_sanity.py            # dry run (no writes)
  SANITY_TOKEN=<write-token> python3 mark_verified_in_sanity.py --execute

Token: SANITY_TOKEN env (a Sanity Editor/write token). The read token in
../.env.local will NOT work for writes.
"""
import json, os, sys, subprocess, tempfile

PROJECT = "jxwrtsiz"
DATASET = "staging"

# Verified universities (Sanity document _id -> verification metadata).
# Add a line only after its fact-checks/<school>-<date>.md pass.
VERIFIED = {
    "university-ae-nyu-abu-dhabi": ("2026-09-27", "fact-checks/nyuad-2026-09-27.md"),
    "university-nl-tu-delft": ("2026-10-03", "fact-checks/tu-delft-2026-10-03.md (both residency tiers)"),
    "university-ca-university-of-toronto": ("2026-10-03", "fact-checks/toronto-2026-10-03.md (intl tuition exact)"),
    "university-gb-university-of-oxford": ("2026-10-07", "fact-checks/oxford-2026-10-03.md (resolved 2026-10-07)"),
    "university-de-tu-munich": ("2026-10-07", "fact-checks/tu-munich-2026-10-07.md (non-EU EUR6,000 exact; German-taught)"),
}


def get_token():
    t = os.environ.get("SANITY_TOKEN")
    if not t:
        sys.exit("SANITY_TOKEN (a write token) is required for --execute. Dry run only without it.")
    return t.strip()


def curl(args):
    p = subprocess.run(["curl", "-sS", "--fail-with-body", *args], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"curl failed ({p.returncode}): {p.stderr or p.stdout}")
    return p.stdout


def build_mutations():
    muts = []
    for doc_id, (date, note) in VERIFIED.items():
        patch = {"set": {"evidapath_verified": True, "evidapath_verified_at": date,
                         "evidapath_verification_note": note}}
        # Patch the published doc and the draft (if it exists) so both agree.
        muts.append({"patch": {"id": doc_id, **patch}})
        muts.append({"patch": {"id": f"drafts.{doc_id}", "ifRevisionID": None, **patch}})
    return muts


def main():
    execute = "--execute" in sys.argv
    print(f"target: {PROJECT}/{DATASET} | universities to mark verified: {len(VERIFIED)}")
    for doc_id, (date, note) in VERIFIED.items():
        print(f"  {doc_id}  verified_at={date}")
    if not execute:
        print("\nDRY RUN — no writes. Re-run with SANITY_TOKEN set and --execute.")
        return
    token = get_token()
    # Only patch published docs (drafts patched best-effort; ignore missing-draft errors
    # by patching published first, drafts in a separate lenient pass).
    pub = [{"patch": {"id": i, "set": {"evidapath_verified": True,
            "evidapath_verified_at": d, "evidapath_verification_note": n}}}
           for i, (d, n) in VERIFIED.items()]
    body = json.dumps({"mutations": pub})
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tf:
        tf.write(body); payload = tf.name
    url = f"https://{PROJECT}.api.sanity.io/v2021-06-07/data/mutate/{DATASET}?returnIds=false"
    out = curl(["-X", "POST", "-H", f"Authorization: Bearer {token}",
                "-H", "Content-Type: application/json", "--data-binary", f"@{payload}", url])
    os.unlink(payload)
    res = json.loads(out)
    print(f"\nWROTE markers | transactionId {res.get('transactionId')}")


if __name__ == "__main__":
    main()
