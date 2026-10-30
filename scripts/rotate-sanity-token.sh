#!/usr/bin/env bash
# Swap a new Sanity token into the local (git-ignored) env files without it ever
# appearing on screen or in chat. Run it after creating the new token at
# sanity.io/manage → project jxwrtsiz → API → Tokens.
#
#   scripts/rotate-sanity-token.sh write    # Editor token  → .env.local SANITY_READ_TOKEN + .dev.vars SANITY_TOKEN
#   scripts/rotate-sanity-token.sh read     # Viewer token  → .dev.vars SANITY_READ_TOKEN
#
# The token is checked against the API before anything is written; old files are
# backed up next to themselves as *.bak-<date>.
set -euo pipefail
KIND="${1:?usage: $0 write|read}"
ROOT="$(git rev-parse --show-toplevel)"
NAV="$ROOT/evidapath-navigator"

read -r -s -p "Paste the new $KIND token (input hidden): " TOKEN; echo
[[ -n "$TOKEN" ]] || { echo "No token entered." >&2; exit 1; }

# Check it works (read), and for a write token that it can write (dry-run mutation).
CODE="$(curl -s -o /dev/null -w '%{http_code}' -H "Authorization: Bearer $TOKEN" \
  "https://jxwrtsiz.api.sanity.io/v2024-01-01/data/query/staging?query=count(*%5B_type%3D%3D%22university%22%5D)")"
[[ "$CODE" == "200" ]] || { echo "Token rejected by Sanity (HTTP $CODE). Nothing changed." >&2; exit 1; }
if [[ "$KIND" == "write" ]]; then
  CODE="$(curl -s -o /dev/null -w '%{http_code}' -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
    "https://jxwrtsiz.api.sanity.io/v2024-01-01/data/mutate/staging?dryRun=true" \
    -d '{"mutations":[{"createIfNotExists":{"_id":"rotation-check","_type":"rotationCheck"}}]}')"
  [[ "$CODE" == "200" ]] || { echo "Token can read but not write (HTTP $CODE) — create it with the Editor role. Nothing changed." >&2; exit 1; }
fi

set_key() { # file key — replace or append KEY=TOKEN
  local f="$1" k="$2"
  [[ -f "$f" ]] && cp "$f" "$f.bak-$(date +%Y%m%d)"
  touch "$f"
  python3 -I - "$f" "$k" "$TOKEN" <<'PY'
import sys
f,k,v=sys.argv[1:]
lines=open(f).read().splitlines()
out=[];done=False
for l in lines:
    if l.startswith(k+"="): out.append(f"{k}={v}"); done=True
    else: out.append(l)
if not done: out.append(f"{k}={v}")
open(f,"w").write("\n".join(out)+"\n")
PY
  echo "Updated $k in ${f#$ROOT/}"
}

if [[ "$KIND" == "write" ]]; then
  set_key "$NAV/.env.local" SANITY_READ_TOKEN
  set_key "$NAV/.dev.vars" SANITY_TOKEN
else
  set_key "$NAV/.dev.vars" SANITY_READ_TOKEN
fi
echo "Done. Now delete the OLD token in sanity.io/manage, then delete the *.bak-* files."
