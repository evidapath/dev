# keep_new.py <built.ndjson> <out.ndjson> : keep only records not already in Sanity (so a re-built
# subject folder doesn't rewrite records that were applied before), plus source-excerpt patches,
# and check every excerpt patch only appends to the current excerpt.
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from q import q
lines = [json.loads(l) for l in open(sys.argv[1])]
ids = [m["createOrReplace"]["_id"] for m in lines if "createOrReplace" in m]
existing = set(q("*[_id in %s]._id" % json.dumps(ids)))
out = [m for m in lines if "patch" in m or m["createOrReplace"]["_id"] not in existing]
for m in out:
    if "patch" in m and "excerpt" in m["patch"].get("set", {}):
        i = m["patch"]["id"]; old = q(f'*[_id=="{i}"][0].excerpt') or ""
        assert m["patch"]["set"]["excerpt"].startswith(old), f"{i}: excerpt patch would remove text"
open(sys.argv[2], "w").write("".join(json.dumps(m, ensure_ascii=False) + "\n" for m in out))
progs = sorted(m["createOrReplace"]["_id"] for m in out if "createOrReplace" in m and m["createOrReplace"]["_type"] == "program")
print(f"{len(lines)} built, {len(existing)} already in Sanity, {len(out)} kept; new programmes: {progs}")
