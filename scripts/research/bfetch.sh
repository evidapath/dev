#!/bin/zsh
# bfetch.sh <url> [wait-seconds] : read a page in the browser (playwright-cli session "res") and save its
# visible text to .research-cache/pages/<id>.txt. For pages that only render with JavaScript.
# Never use it to get past a bot check or CAPTCHA: if the text says "verify you are human" or similar,
# the page is blocked; record it as blocked instead.
ROOT=${0:A:h:h:h}; D=$ROOT/.research-cache/pages; mkdir -p $D
U="$1"; H=$(print -rn -- "$U" | shasum | cut -c1-12)
cd $ROOT/evidapath-navigator
playwright-cli -s=res goto "$U" >/dev/null 2>&1 || { playwright-cli -s=res open "$U" >/dev/null 2>&1; }
sleep ${2:-5}
playwright-cli -s=res eval "(()=>{document.querySelectorAll('details').forEach(d=>d.open=true);return document.body.innerText})()" 2>/dev/null | python3 -I -c "
import sys,json,re
raw=sys.stdin.read(); m=re.search(r'### Result\n(.*?)\n### Ran Playwright', raw, re.S)
print(json.loads(m.group(1)) if m else '')" > "$D/$H.txt"
print -r -- "$U" > "$D/$H.url"; echo 200 > "$D/$H.code"
echo "$H chars=$(wc -c < $D/$H.txt | tr -d ' ')"
