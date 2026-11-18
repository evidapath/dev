# raw.py <id> : save .research-cache/pages/<id>-raw.txt = the page source with JSON escapes decoded,
# for figures that exist only in data embedded in the page (e.g. UNSW fee constants).
# The builder gives such a source its own record (url + "#page-data").
import sys, html, re, shutil
from pathlib import Path
D = Path(__file__).resolve().parents[2] / ".research-cache" / "pages"
h = (D / f"{sys.argv[1]}.html").read_text(encoding="utf-8", errors="replace")
h = re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), h)
(D / f"{sys.argv[1]}-raw.txt").write_text(html.unescape(h))
shutil.copy(D / f"{sys.argv[1]}.url", D / f"{sys.argv[1]}-raw.url")
