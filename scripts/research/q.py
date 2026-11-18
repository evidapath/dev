# q.py '<GROQ query>' : run a read-only query on Sanity jxwrtsiz/staging (published perspective).
# Reads SANITY_READ_TOKEN from evidapath-navigator/.env.local; never prints it.
import json, re, subprocess, urllib.parse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
tok = re.search(r"^SANITY_READ_TOKEN=(.*)$", (ROOT / "evidapath-navigator/.env.local").read_text(), re.M).group(1).strip().strip('"')
def q(query, perspective="published"):
    url = "https://jxwrtsiz.api.sanity.io/v2024-01-01/data/query/staging?" + urllib.parse.urlencode({"query": query, "perspective": perspective})
    # token on stdin (-H @-), never in curl's arguments (process listings, tracebacks)
    r = subprocess.run(["curl", "-s", "-H", "@-", url], input=f"Authorization: Bearer {tok}\n", capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"Sanity query failed (curl exit {r.returncode}); try again")
    return json.loads(r.stdout)["result"]
if __name__ == "__main__":
    print(json.dumps(q(sys.argv[1]), indent=1, ensure_ascii=False))
