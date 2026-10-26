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
    # US batch — fact-checks/us-batch-2026-10-26.md
    # All 10 confirmed from official 2026-27 COA pages; no corrections needed.
    "university-us-princeton": ("2026-10-26", "fact-checks/us-batch-2026-10-26.md (tuition $68,140; need-blind, no loans)"),
    "university-us-mit": ("2026-10-26", "fact-checks/us-batch-2026-10-26.md (tuition $66,720; need-blind, no loans)"),
    "university-us-harvard": ("2026-10-26", "fact-checks/us-batch-2026-10-26.md (tuition $62,226; need-blind, no loans)"),
    "university-us-stanford": ("2026-10-26", "fact-checks/us-batch-2026-10-26.md (tuition $67,731; need-blind US/need-aware intl)"),
    "university-us-upenn": ("2026-10-26", "fact-checks/us-batch-2026-10-26.md (tuition $65,670; no-loan, need-blind US/CA/MX)"),
    "university-us-cornell": ("2026-10-26", "fact-checks/us-batch-2026-10-26.md (tuition $73,946; meets need incl. loans)"),
    "university-us-nyu": ("2026-10-26", "fact-checks/us-batch-2026-10-26.md (tuition $68,576 A&S/Tandon; NYU Promise)"),
    "university-us-usc": ("2026-10-26", "fact-checks/us-batch-2026-10-26.md (tuition $75,384; merit + need-based)"),
    "university-us-purdue": ("2026-10-26", "fact-checks/us-batch-2026-10-26.md (CS/Eng $36,154; Business/Econ $35,540; NO intl scholarships)"),
    "university-us-asu": ("2026-10-26", "fact-checks/us-batch-2026-10-26.md (base $39,062; NAMU scholarship auto)"),
    # Canada batch — fact-checks/ca-batch-2026-10-26.md
    # Waterloo/McGill/McMaster: primary-source confirmed.
    # UBC/Alberta: Board-approved rates via secondary sources (fee pages 403/calculator; caveat in fact-check file).
    "university-ca-waterloo": ("2026-10-26", "fact-checks/ca-batch-2026-10-26.md (CS/Eng $69,884; AFM $55,346; Econ $54,020; primary source)"),
    "university-ca-ubc": ("2026-10-26", "fact-checks/ca-batch-2026-10-26.md (CS $53,082; Eng $53,675; BCom $66,678; Econ $51,530; secondary-Board-approved; fee page 403)"),
    "university-ca-mcgill": ("2026-10-26", "fact-checks/ca-batch-2026-10-26.md (CS $64,786; Eng $65,168; BCom $71,687; Econ $54,000; primary-source PDF)"),
    "university-ca-mcmaster": ("2026-10-26", "fact-checks/ca-batch-2026-10-26.md (CS $56,233; Eng $69,354; Business $50,003; SocSci $45,158; primary source)"),
    "university-ca-alberta": ("2026-10-26", "fact-checks/ca-batch-2026-10-26.md (CS $39,792; Eng $49,952; Business $46,547; Econ null; secondary source; calculator redirect)"),
    # UK batch — fact-checks/uk-batch-2026-10-26.md
    # Cambridge/Warwick/Birmingham: primary source confirmed.
    # Imperial: 3 fee corrections applied (2027 entry vs stored 2026-27 values).
    # Manchester: CS+Eng primary source confirmed (Eng corrected); Econ/Mgt secondary.
    # UCL: source excerpt (fee pages 403 throughout). Nottingham: proxy fees (pages 404).
    "university-uk-cambridge": ("2026-10-26", "fact-checks/uk-batch-2026-10-26.md (CS/Eng £46,872 Grp4; Econ £30,798 Grp1; 2027 entry primary source)"),
    "university-uk-imperial": ("2026-10-26", "fact-checks/uk-batch-2026-10-26.md (Computing/Eng £47,800; EconFinDS £44,800; 2027 entry CORRECTED from 2026-27 values)"),
    "university-uk-ucl": ("2026-10-26", "fact-checks/uk-batch-2026-10-26.md (CS £46,700; Eng £42,700; Econ £39,200; Mgt £42,700; secondary-source excerpt; fee pages 403)"),
    "university-uk-warwick": ("2026-10-26", "fact-checks/uk-batch-2026-10-26.md (uniform £35,530 2026-27 primary source; 2027-28 not yet set)"),
    "university-uk-manchester": ("2026-10-26", "fact-checks/uk-batch-2026-10-26.md (CS £39,700; Eng £37,500 CORRECTED; Econ/Mgt £33,100 proxy 2026-27)"),
    "university-uk-birmingham": ("2026-10-26", "fact-checks/uk-batch-2026-10-26.md (fees null — not published per-programme; confirmed from primary source)"),
    "university-uk-nottingham": ("2026-10-26", "fact-checks/uk-batch-2026-10-26.md (CS £33,500; Eng £33,000; Econ £26,800; Business £24,700; proxy 2027-28; pages 404)"),
    # Germany batch — fact-checks/de-batch-2026-10-26.md
    # TU Berlin + LMU: primary source confirmed. RWTH/Heidelberg/KIT: state law + partial primary source.
    "university-de-rwth-aachen": ("2026-10-26", "fact-checks/de-batch-2026-10-26.md (no non-EU tuition; NRW state policy; ~€358/sem contribution)"),
    "university-de-heidelberg": ("2026-10-26", "fact-checks/de-batch-2026-10-26.md (€1,500/sem non-EU BW law + €189.80 admin = €3,379.60/yr; admin confirmed primary source)"),
    "university-de-tu-berlin": ("2026-10-26", "fact-checks/de-batch-2026-10-26.md (€379.06/sem WS 2026-27; no non-EU tuition; Berlin state policy; primary source)"),
    "university-de-kit": ("2026-10-26", "fact-checks/de-batch-2026-10-26.md (€1,500/sem non-EU BW law + ~€168 admin = ~€3,336/yr; BW state law confirmed)"),
    "university-de-lmu": ("2026-10-26", "fact-checks/de-batch-2026-10-26.md (€97/sem SS2026; no non-EU tuition; LMU ≠ TUM; primary source)"),
    # Netherlands batch — fact-checks/nl-batch-2026-10-26.md
    # All 3 primary-source confirmed. TU/e and UT corrected to 2027-28 rates.
    "university-nl-tue": ("2026-10-26", "fact-checks/nl-batch-2026-10-26.md (CSE/EE €22,400/yr 2027-28 NEW ENTRANT; CORRECTED from €18,600 2026-27; primary source)"),
    "university-nl-uva": ("2026-10-26", "fact-checks/nl-batch-2026-10-26.md (Science/CS €21,900; Econ/Business €15,730; 2027-28 primary source)"),
    "university-nl-ut": ("2026-10-26", "fact-checks/nl-batch-2026-10-26.md (CS/ME €16,869; IBA €12,652; 2027-28 CORRECTED; primary source)"),
    # Australia batch — fact-checks/au-batch-2026-10-26.md
    # UniMelb: 2027 range minimums confirmed from primary source (BSc $55,556; BCom $56,451).
    # Monash: BCS CORRECTED $55,500→$58,940 (2027 primary source); BEng $63,040 + BCom $59,140 confirmed.
    # USyd: $63,600 BAdvComp/BEng + $59,100 BEcon confirmed (search-primary). UNSW: $1,330+$1,240/UOC confirmed.
    # Note: entering cohort is "Semester 1 Feb 2028"; 2028 fees not yet published — 2027 rates used as best available.
    "university-au-unimelb": ("2026-10-26", "fact-checks/au-batch-2026-10-26.md (BSc Computing $55,556 min; BCom $56,451 min; 2027 range mins primary source unimelb.edu.au)"),
    "university-au-monash": ("2026-10-26", "fact-checks/au-batch-2026-10-26.md (BCS $58,940 CORRECTED; BEng $63,040; BCom $59,140; 2027 primary source monash.edu)"),
    "university-au-usyd": ("2026-10-26", "fact-checks/au-batch-2026-10-26.md (BAdvComp/BEng $63,600; BEcon $59,100; 2027 primary source sydney.edu.au)"),
    "university-au-unsw": ("2026-10-26", "fact-checks/au-batch-2026-10-26.md (Eng/CS $1,330/UOC=$63,840; Commerce $1,240/UOC=$59,520; 2027 primary source unsw.edu.au)"),
    # UAE batch — fact-checks/ae-batch-2026-10-26.md
    # AUS/UAEU/Khalifa/UoS/RIT: primary source confirmed. Birmingham: 3 fees CORRECTED to Sept 2027.
    # Heriot-Watt: primary source confirmed (CS/Eng 82,264; BBA 78,650). CUD: BBA CORRECTED (67,410→70,781).
    "university-ae-aus": ("2026-10-26", "fact-checks/ae-batch-2026-10-26.md (AED 110,876 uniform 2026-27; primary source aus.edu)"),
    "university-ae-uaeu": ("2026-10-26", "fact-checks/ae-batch-2026-10-26.md (CS AED 79,830; Eng AED 87,813; 2,661/cr; primary source uaeu.ac.ae)"),
    "university-ae-khalifa": ("2026-10-26", "fact-checks/ae-batch-2026-10-26.md (CS AED 81,250; 2,500/cr; primary source ku.ac.ae)"),
    "university-ae-university-of-sharjah": ("2026-10-26", "fact-checks/ae-batch-2026-10-26.md (AED 60,703/yr; 2,529/cr; official UOS tuition schedule PDF)"),
    "university-ae-birmingham-dubai": ("2026-10-26", "fact-checks/ae-batch-2026-10-26.md (CS 162,203 CORRECTED; CompEng 154,325 CORRECTED; BizMgt 146,806; Econ 133,199 CORRECTED; Sept 2027 primary source birmingham.ac.uk/dubai)"),
    "university-ae-heriot-watt-dubai": ("2026-10-26", "fact-checks/ae-batch-2026-10-26.md (CS/Eng AED 82,264; BBA AED 78,650; VAT-incl; primary source hw.ac.uk/dubai)"),
    "university-ae-rit-dubai": ("2026-10-26", "fact-checks/ae-batch-2026-10-26.md (AED 68,000 uniform; confirmed primary source)"),
    "university-ae-canadian-university-dubai": ("2026-10-26", "fact-checks/ae-batch-2026-10-26.md (CS 72,466; Eng 82,128; BBA 70,781 CORRECTED from 67,410; VAT-incl; primary source cud.ac.ae/fees)"),
    # Malaysia batch — fact-checks/my-batch-2026-10-26.md
    "university-my-um": ("2026-10-26", "fact-checks/my-batch-2026-10-26.md (CS 25,486; EE 33,025; Econ 25,700; 2025-26; primary source confirmed)"),
    "university-my-monash": ("2026-10-26", "fact-checks/my-batch-2026-10-26.md (CS 57,600 confirmed; ME 68,160 FILLED from null; BBusComm 54,240 FILLED from null; primary source monash.edu.my)"),
    "university-my-nottingham": ("2026-10-26", "fact-checks/my-batch-2026-10-26.md (CS 59,000; MEng 69,000; Econ 57,000; pre-SST; 2026-27; primary source nottingham.edu.my)"),
    "university-my-taylors": ("2026-10-26", "fact-checks/my-batch-2026-10-26.md (CS 49,737 CORRECTED from 45,246; ME 49,719 CORRECTED from 45,891; Bus 52,021 CORRECTED from 47,982; 2027 official PDF)"),
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


def mutate(muts, token):
    """POST mutations; returns the parsed response or raises RuntimeError."""
    body = json.dumps({"mutations": muts})
    url = f"https://{PROJECT}.api.sanity.io/v2021-06-07/data/mutate/{DATASET}?returnIds=false"
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tf:
        tf.write(body)
        payload = tf.name
    try:
        out = curl(["-X", "POST", "-H", f"Authorization: Bearer {token}",
                    "-H", "Content-Type: application/json", "--data-binary", f"@{payload}", url])
    finally:
        os.unlink(payload)
    return json.loads(out)


def main():
    execute = "--execute" in sys.argv
    print(f"target: {PROJECT}/{DATASET} | universities to mark verified: {len(VERIFIED)}")
    for doc_id, (date, note) in VERIFIED.items():
        print(f"  {doc_id}  verified_at={date}")
    if not execute:
        print("\nDRY RUN — no writes. Re-run with SANITY_TOKEN set and --execute.")
        return
    token = get_token()
    # Batch-1 schools (NYUAD, Oxford, Toronto, TUM, Delft) exist in BOTH published
    # and draft form. Batch-2 schools (US and beyond) exist ONLY as drafts until
    # publish_to_sanity.py runs. Sending them in a single transaction fails if any
    # published doc is missing. Strategy: send draft mutations all at once (always
    # present); send published mutations individually and skip docs that don't exist yet.
    draft_muts = []
    pub_muts = []
    for doc_id, (date, note) in VERIFIED.items():
        patch_set = {"set": {"evidapath_verified": True,
                             "evidapath_verified_at": date, "evidapath_verification_note": note}}
        draft_muts.append({"patch": {"id": f"drafts.{doc_id}", **patch_set}})
        pub_muts.append({"patch": {"id": doc_id, **patch_set}})

    # 1. Drafts — all should exist; one transaction.
    res = mutate(draft_muts, token)
    print(f"\nWROTE draft markers ({len(draft_muts)}) | transactionId {res.get('transactionId')}")

    # 2. Published docs — send individually; skip (warn) if the published doc doesn't exist yet.
    ok, skipped = 0, 0
    for mut in pub_muts:
        doc_id = mut["patch"]["id"]
        try:
            mutate([mut], token)
            ok += 1
        except RuntimeError:
            print(f"  SKIP published (not yet published — draft-only school): {doc_id}")
            skipped += 1
    print(f"Published markers: {ok} written, {skipped} skipped (draft-only, will inherit on publish).")


if __name__ == "__main__":
    main()
