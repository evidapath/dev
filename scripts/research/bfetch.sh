#!/bin/zsh
# bfetch.sh <url> [wait-seconds] : read a page in headless Chromium (scripts/research/browser/render.mjs) and save
# its visible text, plus the text of hidden tabs/collapsed sections the page already loaded, to
# .research-cache/pages/<id>.txt (and .html, .url, .code), the same format as fetch.sh. For pages that only
# render with JavaScript. If the page is a bot check or CAPTCHA, render.mjs saves nothing and this prints
# "BLOCKED": record the site as blocked. Never try to get past a bot check (CLAUDE.md rule 1).
# A failed render never overwrites an existing saved page.
# One-time setup: cd scripts/research/browser && npm install && npx playwright-core install chromium-headless-shell
ROOT=${0:A:h:h:h}; D=$ROOT/.research-cache/pages; mkdir -p $D
U="$1"; H=$(print -rn -- "$U" | shasum | cut -c1-12)
if [[ -s "$D/$H.txt" && $(wc -c < "$D/$H.txt") -gt 100 && -z "$FORCE" ]]; then
  echo "$H KEPT (a saved copy exists; FORCE=1 to replace it; generators may quote it)"; exit 0
fi
T=$(mktemp -d)
out=$(node $ROOT/scripts/research/browser/render.mjs "$U" "$T/p" ${2:-4} 2>&1); rc=$?
if [[ $rc -eq 3 ]]; then echo "$H BLOCKED ($out)"; rm -rf $T; exit 3; fi
if [[ $rc -ne 0 || ! -s $T/p.txt ]]; then echo "$H ERROR ($out)"; rm -rf $T; exit 1; fi
mv $T/p.txt "$D/$H.txt"; mv $T/p.html "$D/$H.html"; rm -rf $T
print -r -- "$U" > "$D/$H.url"
code=${${out#*status=}%% *}; echo $code > "$D/$H.code"
echo "$H http=$code chars=$(wc -c < $D/$H.txt | tr -d ' ')"
