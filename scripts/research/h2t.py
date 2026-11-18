# h2t.py <file.html> : HTML to plain text (scripts/styles dropped, block tags become line breaks).
import sys, re, html
s = open(sys.argv[1], encoding="utf-8", errors="replace").read()
s = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", s)
s = re.sub(r"(?i)<br\s*/?>|</(p|div|li|h[1-6]|tr|td|th|section|dd|dt)>", "\n", s)
s = re.sub(r"(?s)<[^>]+>", " ", s)
s = html.unescape(s).replace("\xa0", " ")
s = re.sub(r"[ \t\r\f\v]+", " ", s)
s = re.sub(r"\n\s*\n+", "\n", s)
print(s.strip())
