#!/bin/zsh
# utreq.sh <program url> <school system label> <outname> : choose the school system in U of T's requirement form, save the page text
ROOT=${0:A:h:h:h}
cd $ROOT/evidapath-navigator
playwright-cli -s=res goto "$1" >/dev/null 2>&1; sleep 5
playwright-cli -s=res eval "(()=>{const f=document.getElementById('academic-requirements-form'); const l=[...f.querySelectorAll('label')].find(l=>l.innerText.trim()==='$2'); const i=document.getElementById(l.htmlFor); i.click(); [...f.querySelectorAll('input[type=submit]')].find(b=>b.value==='Apply').click(); return i.value})()" 2>&1 | sed -n 2p
sleep 6
playwright-cli -s=res eval "document.body.innerText" 2>/dev/null | python3 -I -c "
import sys,json,re
raw=sys.stdin.read(); m=re.search(r'### Result\n(.*?)\n### Ran Playwright', raw, re.S)
print(re.sub(r'[ \t]*\n\s*','\n',json.loads(m.group(1)) if m else ''))" > $ROOT/.research-cache/pages/$3.txt
print -r -- "$1" > $ROOT/.research-cache/pages/$3.url; echo "$3 chars=$(wc -c < $ROOT/.research-cache/pages/$3.txt)"
