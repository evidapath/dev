"""Shared helpers for the new-university generators (written 2026-11-25).

  src(page, title, org, quotes)  a source dict; asserts every quote is on the saved page
  on(page, quotes)               the same check, returns the quotes
  spec(...)                      writes fact-checks/research/universities-2026-11/<uni>.json
  prog(...)                      writes one programme research file via common.write
Every check here is repeated by new_university.py / build.py; these only fail earlier.
"""
import json, os, re, sys
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import write  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
PAGES = ROOT / ".research-cache/pages"


def norm(s):
    return re.sub(r"\s+", " ", s.replace("\xa0", " ").replace("’", "'")).strip().lower()


def text(page):
    return norm((PAGES / f"{page}.txt").read_text(errors="replace"))


def on(page, qs):
    t = text(page)
    for q in qs:
        assert norm(q) in t, f"{page}: not on page: {q}"
    return list(qs)


def url(page):
    return (PAGES / f"{page}.url").read_text().strip()


def src(page, title, org, quotes):
    return {"url": url(page), "page": page, "title": title, "organization": org, "quotes": on(page, quotes)}


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower().replace("&", "and")).strip("-")


def spec(uni, name, aliases, kind, website, country, city, sources, residency, main="main"):
    s = {"uni": uni, "name": name, "aliases": aliases, "type": kind, "website": website,
         "country": dict(zip(("cc", "name", "currency"), country)), "city": dict(zip(("slug", "name"), city)),
         "sources": sources, "main_source": main,
         "residency": [dict(zip(("key", "label", "description", "source"), r)) for r in residency]}
    (ROOT / "fact-checks/research/universities-2026-11").mkdir(parents=True, exist_ok=True)
    (ROOT / f"fact-checks/research/universities-2026-11/{uni}.json").write_text(json.dumps(s, indent=2, ensure_ascii=False) + "\n")


def prog(uni, slug, sources, program, costs, admissions):
    (ROOT / f"fact-checks/research/courses-2026-11/{uni}").mkdir(parents=True, exist_ok=True)
    write(uni, {"uni": uni, "slug": slug, "sources": sources, "program": program, "costs": costs, "admissions": admissions})


def adm_all(threshold_by_cur, source, english=None, tests=None, subjects=None):
    """One admissions row per curriculum key given."""
    return [{"curriculum": cur, "source": source, "threshold": th, "required_subjects": subjects or [],
             "tests": tests or [], **({"english": english} if english else {})} for cur, th in threshold_by_cur.items()]
