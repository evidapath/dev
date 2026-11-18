#!/bin/sh
# secret-scan.sh : reads text on stdin (e.g. `git diff --cached`), prints how many lines contain a
# secret, exits 1 if any. Generic token shapes are listed here; private values (the test password)
# are listed one per line in the git-ignored file .secret-patterns at the repo root, so they are
# never committed. A missing .secret-patterns file is itself an error.
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
# Written with [x] classes so this line doesn't match itself: JWT header, Anthropic key, sk- keys, long sk tokens.
GENERIC='ey[J]hbGci|s[k]-ant-|\bs[k]-[A-Za-z0-9_-]{20,}|\bs[k][A-Za-z0-9]{70,}'
if [ ! -s "$ROOT/.secret-patterns" ]; then echo "secret-scan: $ROOT/.secret-patterns is missing (one private pattern per line)" >&2; exit 2; fi
tmp=$(mktemp); cat > "$tmp"
n=$( { grep -E -e "$GENERIC" "$tmp"; grep -F -f "$ROOT/.secret-patterns" "$tmp"; } | wc -l | tr -d ' ')
rm -f "$tmp"; echo "$n"; [ "$n" = 0 ]
