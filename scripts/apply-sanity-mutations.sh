#!/usr/bin/env bash
# Apply a reviewed file of Sanity mutations (one JSON mutation per line) to the
# `staging` dataset, using SANITY_READ_TOKEN from evidapath-navigator/.env.local.
#
#   scripts/apply-sanity-mutations.sh fact-checks/pending/<file>.ndjson
#
# Take a backup first (the fact-check note for each file says where it is).
set -euo pipefail
FILE="${1:?usage: $0 <mutations.ndjson>}"
ROOT="$(git rev-parse --show-toplevel)"
TOKEN="$(grep '^SANITY_READ_TOKEN=' "$ROOT/evidapath-navigator/.env.local" | cut -d= -f2- | tr -d '"')"
[[ -n "$TOKEN" ]] || { echo "No SANITY_READ_TOKEN in .env.local" >&2; exit 1; }
echo "Applying $(wc -l < "$FILE" | tr -d ' ') mutations from $FILE to jxwrtsiz/staging…"
BODY="$(jq -s -c '{mutations: .}' "$FILE")"
CODE="$(curl -s -o /tmp/sanity-mutate-resp.json -w '%{http_code}' -X POST \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "https://jxwrtsiz.api.sanity.io/v2024-01-01/data/mutate/staging" -d "$BODY")"
if [[ "$CODE" == "200" ]]; then echo "Done."; else echo "Failed ($CODE):"; cat /tmp/sanity-mutate-resp.json; exit 1; fi
