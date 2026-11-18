#!/bin/zsh
# ubcreq.sh <program url> <country label regex> <outname> : pick the country in UBC's requirement selector, save visible text
ROOT=${0:A:h:h:h}
cd $ROOT/evidapath-navigator
playwright-cli -s=res goto "$1" >/dev/null 2>&1; sleep 5
playwright-cli -s=res eval "(()=>{const t=[...document.querySelectorAll('a')].find(e=>e.innerText.trim()==='International high schools'&&e.className!=='current'&&e.closest('main,body')); const s=document.getElementById('country-select'); const o=[...s.options].find(o=>new RegExp('$2').test(o.text)); s.value=o.value; s.dispatchEvent(new Event('change',{bubbles:true})); return o.text})()" >/dev/null 2>&1; sleep 4
playwright-cli -s=res eval "document.body.innerText" 2>/dev/null | python3 -I -c "
import sys,json,re
raw=sys.stdin.read(); m=re.search(r'### Result\n(.*?)\n### Ran Playwright', raw, re.S)
print(re.sub(r'[ \t]*\n\s*','\n',json.loads(m.group(1)) if m else ''))" > $ROOT/.research-cache/pages/$3.txt
print -r -- "$1" > $ROOT/.research-cache/pages/$3.url; echo "$3 chars=$(wc -c < $ROOT/.research-cache/pages/$3.txt)"
