#!/usr/bin/env python3
"""
Publish the fact-checked five-school data from the `staging` DRAFTS into a
resolvable, PUBLISHED form (Sanity project jxwrtsiz) so the app can dereference
relationships (city, country, cost profile, scholarships).

Why this exists: in staging the docs are drafts whose *_ref fields point at
published IDs that don't exist, so `country_ref->` etc. resolve to null. Writing
the docs back with the `drafts.` prefix stripped "publishes" them and makes every
reference resolve.

Pipeline (deterministic, offline except the two Sanity API calls):
  1. export staging (read-only)
  2. transform: drop Sanity system docs; strip `drafts.` from _id and every _ref;
     drop server-managed fields (_rev/_createdAt/_updatedAt)
  3. scope: keep all five schools (--scope all) or just the NYUAD subgraph
     (--scope nyuad), selected by reference traversal + scholarship string-links
  4. validate: 0 dangling refs (and, for nyuad, exactly 1 university)
  5. with --execute: createOrReplace into the chosen --dataset

Usage:
  python3 publish_to_sanity.py --dataset staging --scope all             # dry run
  python3 publish_to_sanity.py --dataset staging --scope all --execute   # write
  python3 publish_to_sanity.py --dataset production --scope nyuad --execute

Token: read from ../.env.local (first line) or the SANITY_TOKEN env var.
"""
import json, os, sys, collections, subprocess, tempfile

PROJECT = "jxwrtsiz"
SRC_DATASET = "staging"
API = "2021-10-21"

def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default

def get_token():
    t = os.environ.get("SANITY_TOKEN")
    if t:
        return t.strip()
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "..", ".env.local")) as f:
        return f.readline().strip()

def _curl(args):
    # curl uses the system cert store (python.org Python does not) — portable on macOS.
    p = subprocess.run(["curl", "-sS", "--fail-with-body", *args], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"curl failed ({p.returncode}): {p.stderr or p.stdout}")
    return p.stdout

def export_staging(token):
    url = f"https://{PROJECT}.api.sanity.io/v{API}/data/export/{SRC_DATASET}"
    data = _curl(["-H", f"Authorization: Bearer {token}", url])
    return [json.loads(l) for l in data.splitlines() if l.strip()]

def strip_drafts(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "_ref" and isinstance(v, str) and v.startswith("drafts."):
                obj[k] = v[len("drafts."):]
            else:
                strip_drafts(v)
    elif isinstance(obj, list):
        for it in obj:
            strip_drafts(it)

def transform(raw):
    out = []
    for d in raw:
        t, _id = d.get("_type", ""), d.get("_id", "")
        if t.startswith("system.") or _id.startswith("_."):
            continue
        if _id.startswith("drafts."):
            d["_id"] = _id[len("drafts."):]
        for f in ("_rev", "_createdAt", "_updatedAt"):
            d.pop(f, None)
        strip_drafts(d)
        out.append(d)
    return out

def refs_of(d):
    out = []
    def w(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "_ref" and isinstance(v, str): out.append(v)
                else: w(v)
        elif isinstance(o, list):
            for it in o: w(it)
    w(d); return out

def select_nyuad(docs):
    by_id = {d["_id"]: d for d in docs}
    fwd = {d["_id"]: set(r for r in refs_of(d) if r in by_id) for d in docs}
    rev = collections.defaultdict(set)
    for s, ts in fwd.items():
        for t in ts: rev[t].add(s)
    uni = [d for d in docs if d["_type"] == "university"
           and "abu dhabi" in d.get("canonical_name", "").lower()]
    assert len(uni) == 1, f"expected 1 NYUAD university, found {len(uni)}"
    nyuad_id, nyuad_domain = uni[0]["_id"], uni[0].get("id")
    selected, frontier = {nyuad_id}, {nyuad_id}
    while frontier:                       # reverse closure (descendants)
        nxt = set()
        for n in frontier:
            for r in rev[n]:
                if r in selected or (by_id[r]["_type"] == "university" and r != nyuad_id): continue
                selected.add(r); nxt.add(r)
        frontier = nxt
    sel_prog = {by_id[i].get("id") for i in selected if by_id[i]["_type"] == "program"}
    for d in docs:                        # scholarships via string-array links
        if d["_type"] == "scholarship" and (
                nyuad_domain in set(d.get("institutions_covered") or [])
                or set(d.get("programs_covered") or []) & sel_prog):
            selected.add(d["_id"])
    frontier = set(selected)
    while frontier:                       # forward closure (referenced docs)
        nxt = set()
        for n in frontier:
            for t in fwd[n]:
                if t in selected or (by_id[t]["_type"] == "university" and t != nyuad_id): continue
                selected.add(t); nxt.add(t)
        frontier = nxt
    return [by_id[i] for i in selected]

def import_docs(docs, dataset, token):
    body = json.dumps({"mutations": [{"createOrReplace": d} for d in docs]})
    url = f"https://{PROJECT}.api.sanity.io/v2021-06-07/data/mutate/{dataset}?returnIds=false"
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tf:
        tf.write(body); payload = tf.name
    out = _curl(["-X", "POST", "-H", f"Authorization: Bearer {token}",
                 "-H", "Content-Type: application/json", "--data-binary", f"@{payload}", url])
    os.unlink(payload)
    return json.loads(out)

def main():
    dataset = arg("--dataset", "staging")
    scope = arg("--scope", "all")
    execute = "--execute" in sys.argv
    assert dataset in ("staging", "production"), "dataset must be staging or production"
    assert scope in ("all", "nyuad"), "scope must be all or nyuad"

    token = get_token()
    docs = transform(export_staging(token))
    sel = select_nyuad(docs) if scope == "nyuad" else docs
    by_id = {d["_id"] for d in sel}
    dangling = {r for d in sel for r in refs_of(d) if r not in by_id and any(r == x["_id"] for x in docs)}
    n_uni = sum(1 for d in sel if d["_type"] == "university")
    assert not dangling, f"dangling refs: {sorted(dangling)[:10]}"
    if scope == "nyuad":
        assert n_uni == 1, f"expected 1 university, found {n_uni}"

    print(f"target: {dataset} | scope: {scope} | docs: {len(sel)} | universities: {n_uni} | dangling: 0")
    print("by type:", dict(sorted(collections.Counter(d['_type'] for d in sel).items())))
    if not execute:
        print("\nDRY RUN — no writes. Add --execute to publish.")
        return
    res = import_docs(sel, dataset, token)
    print(f"\nWROTE {len(sel)} docs to {dataset} | transactionId {res.get('transactionId')}")

if __name__ == "__main__":
    main()
