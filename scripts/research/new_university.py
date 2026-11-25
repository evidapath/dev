#!/usr/bin/env python3
"""Create a new university's base records, refusing anything unsourced (written 2026-11-25).

  python3 -I scripts/research/new_university.py <spec.json> <pages-dir> <out.ndjson>

Programmes, fees and entry rules still go through scripts/programmes/build.py; this makes
the records those reference and that build.py can't create: the country (only when it
isn't in Sanity yet), the city, the university, its fee groups (residency categories) and
the source records for its pages. Same checks as build.py:

  1. every quote appears word for word in the saved page (<pages-dir>/<page>.txt), and the
     saved .url matches the source url;
  2. the university's name and the city's name appear in the main source's quotes;
  3. each fee group names a source with quotes;
  4. the university doesn't exist yet (this never overwrites a university).

Spec (one JSON file per university, kept in fact-checks/research/universities-2026-11/):
  {"uni": "it-polimi", "name": "...", "aliases": [], "type": "public", "website": "https://...",
   "country": {"cc": "it", "name": "Italy", "currency": "EUR"},
   "city": {"slug": "it-milan", "name": "Milan"},
   "sources": {"main": {"url", "page", "title", "organization", "quotes": [...]}, ...},
   "main_source": "main",
   "residency": [{"key": "all-students", "label": "...", "description": "...", "source": "fees"}]}
"""
import datetime, hashlib, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "programmes"))
from build import fail, norm, ref, sanity  # noqa: E402  (same checks and Sanity reader)

TODAY = datetime.date.today().isoformat()


def main(spec_path: str, pages_dir: str, out_path: str):
    s = json.loads(Path(spec_path).read_text())
    uni, cc = s["uni"], s["country"]["cc"]
    if not re.fullmatch(r"[a-z]{2}-[a-z0-9-]+", uni) or not uni.startswith(cc + "-"):
        fail(f"uni id {uni} must be <country code>-<name>")

    quotes: dict[str, str] = {}
    for key, src in s["sources"].items():
        page = Path(pages_dir) / f"{src['page']}.txt"
        if not page.exists():
            fail(f"source '{key}' page {src['page']} not saved")
        if (Path(pages_dir) / f"{src['page']}.url").read_text().strip() != src["url"]:
            fail(f"source '{key}' url doesn't match the saved page")
        text = norm(page.read_text())
        for q in src["quotes"]:
            if norm(q) not in text:
                fail(f"quote not found on {src['url']}:\n   {q}")
        quotes[key] = norm(" ".join(src["quotes"]))

    main_q = quotes[s["main_source"]]
    for label, value in (("university name", s["name"]), ("city", s["city"]["name"])):
        if norm(value) not in main_q:
            fail(f"{label} '{value}' isn't in the quotes of source '{s['main_source']}'")
    for r in s["residency"]:
        if not s["sources"].get(r["source"], {}).get("quotes"):
            fail(f"fee group {r['key']}: source '{r['source']}' missing or without quotes")

    ids = [f"university-{uni}", f"country-{cc}", f"city-{s['city']['slug']}"]
    existing = set(sanity(f"*[_id in {json.dumps(ids)}]._id"))
    if f"university-{uni}" in existing:
        fail(f"university-{uni} already exists; this script only creates new universities")

    muts = []
    if f"country-{cc}" not in existing:
        muts.append({"_id": f"country-{cc}", "_type": "country", "id": cc, "name": s["country"]["name"],
                     "currency_default": s["country"]["currency"]})
    if f"city-{s['city']['slug']}" not in existing:
        muts.append({"_id": f"city-{s['city']['slug']}", "_type": "city", "id": s["city"]["slug"],
                     "name": s["city"]["name"], "country_ref": ref(f"country-{cc}")})

    src_ids = {}
    for key, src in s["sources"].items():
        h = hashlib.sha1(src["url"].encode()).hexdigest()[:12]  # same scheme as build.py
        src_ids[key] = f"sourceRecord-ev-{h}"
        muts.append({"_id": src_ids[key], "_type": "sourceRecord", "id": f"ev-{h}", "url": src["url"],
                     "title": src["title"], "source_organization": src["organization"],
                     "source_type": "official_university", "excerpt": " ".join(src["quotes"]),
                     "retrieved_at": f"{TODAY}T00:00:00Z",
                     "retrieval_method": f"Read by EvidaPath new-university pass {TODAY}; quotes checked against the saved page",
                     "fields_supported": [], "notes": ""})

    muts.append({"_id": f"university-{uni}", "_type": "university", "id": uni, "canonical_name": s["name"],
                 "aliases": s.get("aliases", []), "institution_type": s["type"], "official_website": s["website"],
                 "country_ref": ref(f"country-{cc}"), "primary_city_ref": ref(f"city-{s['city']['slug']}"),
                 "record_status": "VERIFIED", "evidapath_verified": True, "evidapath_verified_at": TODAY,
                 "last_researched": TODAY, "last_verified": TODAY,
                 "evidapath_verification_note": f"New university, {TODAY}: {Path(spec_path).name}",
                 "source_refs": [ref(src_ids[s["main_source"]], "sm")],
                 "extension_metadata": {"_type": "extensionMetadata", "fields": []}})
    for r in s["residency"]:
        muts.append({"_id": f"applicantCategory-{uni}-residency-{r['key']}", "_type": "applicantCategory",
                     "id": f"{uni}-residency-{r['key']}", "university_ref": ref(f"university-{uni}"),
                     "dimension": "residency", "label": r["label"], "description": r["description"]})

    # Source records that already exist are left alone (build.py appends to their excerpts).
    have = set(sanity(f'*[_id in {json.dumps([m["_id"] for m in muts])}]._id'))
    out = [{"createOrReplace": m} for m in muts if m["_id"] not in have]
    Path(out_path).write_text("".join(json.dumps(m, ensure_ascii=False) + "\n" for m in out))
    print(f"OK: {uni}, {len(out)} mutations → {out_path}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        fail(__doc__)
    main(*sys.argv[1:])
