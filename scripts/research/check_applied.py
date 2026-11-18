# check_applied.py <pending.ndjson> : report, mutation by mutation, whether a pending file is already
# fully in Sanity (every createOrReplace excerpt, every patched field, every inserted source ref).
# Use it when an apply fails with a revision error (409): if everything is in place, the file was
# applied before and must not be applied again.
import json, sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from q import q
bad = n = 0
for l in open(sys.argv[1]):
    m = json.loads(l); n += 1
    if "createOrReplace" in m:
        d = m["createOrReplace"]; cur = q(f'*[_id=="{d["_id"]}"][0]')
        ok = cur is not None and all(cur.get(k) == v for k, v in d.items() if not k.startswith("_") and k not in ("retrieved_at", "last_checked"))
        if not ok: print("not in place:", d["_id"])
    else:
        p = m["patch"]; d = q(f'*[_id=="{p["id"]}"][0]'); ok = d is not None
        for k, v in (p.get("set") or {}).items():
            mm = re.match(r'([\w.]+)\[_key=="(\w+)"\]\.(\w+)$', k)
            try:
                if mm:
                    o = d
                    for part in mm.group(1).split("."): o = o[part]
                    cur = [x for x in o if x["_key"] == mm.group(2)][0][mm.group(3)]
                else:
                    cur = d
                    for part in k.split("."): cur = cur[part]
            except Exception:
                cur = None
            if cur != v: ok = False; print("differs:", p["id"], k)
        for r in (p.get("insert") or {}).get("items", []):
            if r.get("_ref") and r["_ref"] not in [x["_ref"] for x in (d or {}).get("source_refs", [])]:
                ok = False; print("missing ref:", p["id"], r["_ref"])
    bad += not ok
print(f"{n} mutations checked, {bad} not in place")
