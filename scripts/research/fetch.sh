#!/bin/zsh
# fetch.sh <url> : save a page's raw HTML and plain text to .research-cache/pages/<id>.{html,txt,url,code}
# <id> = first 12 hex of sha1(url); the builder's source-record id uses the same scheme.
# Prints "<id> http=<status> chars=<text length>". A status other than 200, or a tiny text,
# means the page didn't really load (bot check, 404, script-only page): don't quote from it.
ROOT=${0:A:h:h:h}; D=$ROOT/.research-cache/pages; mkdir -p $D
U="$1"; H=$(print -rn -- "$U" | shasum | cut -c1-12)
curl -sL --compressed --max-time 40 -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36" -H "Accept-Language: en" -o "$D/$H.html" -w "%{http_code}" "$U" > "$D/$H.code"
print -r -- "$U" > "$D/$H.url"
python3 -I ${0:A:h}/h2t.py "$D/$H.html" > "$D/$H.txt" 2>/dev/null
echo "$H http=$(cat $D/$H.code) chars=$(wc -c < $D/$H.txt | tr -d ' ')"
