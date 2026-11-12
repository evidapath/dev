#!/usr/bin/env python3
"""Turn programme research files into Sanity mutations, refusing anything unsourced.

  python3 -I scripts/programmes/build.py <research-dir> <pages-dir> <out.ndjson>

Each research file (JSON, one programme) lists its sources with verbatim quotes
copied from the official page. Before writing anything this script checks, and
stops on the first failure:

  1. every quote appears word for word in the saved text of its page
     (<pages-dir>/<page>.txt, saved by the fetcher when the page was read);
  2. every number in a value we store (fees, grades, scores, years, places)
     appears in a quote of the source that value cites;
  3. deadlines: the day, the month name and the year appear in a cited quote.

Values copied from records already in Sanity ("from_existing", "living_from",
"fees_from") are not re-checked
here: they were verified when they were added, and the record id is kept.

Reads SANITY_READ_TOKEN from evidapath-navigator/.env.local only to copy those
existing records (living costs, English requirement). Never prints it.
"""

import json, re, sys, hashlib, subprocess, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TODAY = "2026-11-11"
MONTHS = "january february march april may june july august september october november december".split()

# curriculum key → (curriculum_type label the decision engine matches, category suffix)
CURRICULA = {
    "a-level": ("GCE A-Level", "curriculum-a-level"),
    "ib": ("International Baccalaureate (IB) Diploma", "curriculum-ib"),
    "us-hs": ("US High School Diploma", "curriculum-us-hs"),
    "cbse": ("Indian CBSE / ISC (Class XII)", "curriculum-cbse"),
    "abitur": ("German Abitur", "curriculum-abitur"),
    "uae-shs": ("UAE Secondary School Certificate (Emirati)", "curriculum-uae-shs"),
    "international-other": ("General International Secondary Qualification", "curriculum-international-other"),
}


def norm(s: str) -> str:
    s = s.replace(" ", " ").replace("’", "'").replace("‘", "'").replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", s).strip().lower()


def nums(s: str) -> set[str]:
    out = set()
    for n in re.findall(r"\d[\d,]*(?:\.\d+)?", s):
        n = n.replace(",", "")
        out.add(n)
        if "." in n:
            out.add(n.rstrip("0").rstrip("."))
    return out


def fail(msg: str):
    print("STOP:", msg)
    sys.exit(1)


def sanity(query: str):
    env = (ROOT / "evidapath-navigator/.env.local").read_text()
    token = re.search(r"^SANITY_READ_TOKEN=(.*)$", env, re.M).group(1).strip().strip('"')
    url = "https://jxwrtsiz.api.sanity.io/v2024-01-01/data/query/staging?" + urllib.parse.urlencode(
        {"query": query, "perspective": "raw"}
    )
    out = subprocess.run(["curl", "-s", "-H", f"Authorization: Bearer {token}", url],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)["result"]


def ref(_id: str, key: str | None = None):
    r = {"_ref": _id, "_type": "reference", "_weak": True}
    if key:
        r["_key"] = key
    return r


def main(research_dir: str, pages_dir: str, out_path: str):
    files = sorted(Path(research_dir).glob("*.json"))
    if not files:
        fail("no research files")
    muts: list[dict] = []
    categories_needed: dict[str, dict] = {}
    for f in files:
        r = json.loads(f.read_text())
        uni, slug = r["uni"], r["slug"]
        where = f.name

        # 1. quotes are on their pages
        quotes: dict[str, str] = {}
        for key, s in r["sources"].items():
            page = Path(pages_dir) / f"{s['page']}.txt"
            if not page.exists():
                fail(f"{where}: source '{key}' page {s['page']} not saved")
            text = norm(page.read_text())
            saved_url = (Path(pages_dir) / f"{s['page']}.url").read_text().strip()
            if saved_url != s["url"]:
                fail(f"{where}: source '{key}' url doesn't match the saved page ({saved_url})")
            for q in s["quotes"]:
                if norm(q) not in text:
                    fail(f"{where}: quote not found on {s['url']}:\n   {q}")
            quotes[key] = " ".join(s["quotes"])

        def q_of(src) -> str:
            return " ".join(quotes[x] for x in (src if isinstance(src, list) else [src]))

        def check_numbers(value, src, label: str):
            missing = nums(str(value)) - nums(q_of(src))
            if missing:
                fail(f"{where}: {label} has {sorted(missing)} not in the quotes of source '{src}'")

        prog_id = f"{uni}-{slug}"
        src_ids = {}
        for key, s in r["sources"].items():
            # Same id scheme as earlier passes (sha1 of the URL); figures read from a
            # page's embedded data ("-raw") get their own record.
            key_url = s["url"] + ("#page-data" if s["page"].endswith("-raw") else "")
            h = hashlib.sha1(key_url.encode()).hexdigest()[:12]
            sid = f"sourceRecord-ev-{h}"
            src_ids[key] = sid
            muts.append({"createOrReplace": {
                "_id": sid, "_type": "sourceRecord", "id": f"ev-{h}", "url": s["url"],
                "title": s["title"], "source_organization": s["organization"],
                "source_type": "official_university" if s.get("type", "university") == "university" else s["type"],
                "excerpt": " ".join(s["quotes"]), "retrieved_at": f"{TODAY}T00:00:00Z",
                "retrieval_method": f"Read by EvidaPath course-expansion pass {TODAY}; quotes checked against the saved page",
                "fields_supported": [], "notes": "",
            }})

        p = r["program"]
        check_numbers(p["duration_years"], p["source"], "duration")
        for k in ("degree_type", "summary"):
            check_numbers(p.get(k, ""), p["source"], k)
        reqs = []
        for i, a in enumerate(p.get("application_requirements", [])):
            check_numbers(a["description"], a["source"], f"application requirement '{a['name']}'")
            reqs.append({"_key": f"r{i+1}", "_type": "applicationRequirement", "name": a["name"],
                         "description": a["description"], "necessity": a.get("necessity", "required"),
                         "notes": "", "requirement_type": a.get("type", "other")})
        muts.append({"createOrReplace": {
            "_id": f"program-{prog_id}", "_type": "program", "id": prog_id,
            "university_ref": ref(f"university-{uni}"),
            "program_name": p["name"], "degree_type": p["degree_type"],
            "degree_type_local": p["summary"], "field_of_study": p["field"],
            "duration_value": p["duration_years"], "duration_unit": "years",
            "language_of_instruction": p["languages"], "faculty_school": p.get("faculty", ""),
            "official_program_url": r["sources"][p["source"]]["url"],
            "decision_context_academic_year": p["entry_year"],
            "application_platform": p.get("platform", ""),
            "application_requirements": reqs,
            "record_status": "VERIFIED",
            "source_refs": [ref(src_ids[k], f"s{i+1}") for i, k in enumerate(r["sources"])],
            "extension_metadata": {"_type": "extensionMetadata"},
        }})

        # costs
        for c in r.get("costs", []):
            # A fee that differs by year is averaged here, from quoted numbers only:
            # "tuition_formula": "(2*33750+3*53880)/5".
            if c.get("tuition_formula"):
                f_ = c["tuition_formula"]
                if not re.fullmatch(r"[\d+*/(). ]+", f_):
                    fail(f"{where}: tuition_formula may only hold numbers and + * / ( )")
                years = sum(int(x) for x in re.findall(r"(\d+)\*", f_))
                total_over_years = re.fullmatch(r"\s*\d+\s*/\s*(\d+)\s*", f_)  # published total ÷ years
                if total_over_years and int(total_over_years.group(1)) == p["duration_years"]:
                    years = p["duration_years"]
                if years != p["duration_years"] or not f_.replace(" ", "").endswith(f"/{p['duration_years']}"):
                    fail(f"{where}: tuition_formula must cover all {p['duration_years']} years and divide by them")
                check_numbers(re.sub(r"(\d+)\*", "", f_).split("/")[0], c["source"], "tuition_formula fees")
                c["tuition_annual"] = round(eval(f_, {"__builtins__": {}}))
            else:
                check_numbers(c["tuition_annual"], c["source"], f"{c['residency']} tuition")
            if not c.get("fees_from"):
                check_numbers(c.get("mandatory_fees_annual", ""), c["source"], f"{c['residency']} compulsory fees")
            living = None
            if c.get("living_from"):
                living = sanity(f'*[_id=="{c["living_from"]}"][0]{{estimated_living_costs_annual, living_cost_source_note, living_cost_source_basis, mandatory_fees_annual, currency, "university": program_ref._ref}}')
                if not living:
                    fail(f"{where}: living_from {c['living_from']} not found")
                if living["currency"] != c["currency"]:
                    fail(f"{where}: living_from is in {living['currency']}, this fee is in {c['currency']}; amounts can't be mixed")
                if not living["university"].startswith(f"program-{uni}"):
                    fail(f"{where}: living_from belongs to another university")
            # Compulsory non-tuition fees that apply to every programme at the university
            # (e.g. a visa fee) are copied from an existing verified record, like living costs.
            extra = None
            if c.get("fees_from"):
                extra = sanity(f'*[_id=="{c["fees_from"]}"][0]{{mandatory_fees_annual, currency, "university": program_ref._ref, "note": extension_metadata.fields[key=="compulsory_fees_note"][0].value}}')
                if not extra or not extra["university"].startswith(f"program-{uni}") or extra["currency"] != c["currency"]:
                    fail(f"{where}: fees_from {c['fees_from']} missing, another university or another currency")
                if c.get("mandatory_fees_annual"):
                    fail(f"{where}: give mandatory_fees_annual or fees_from, not both")
                c["mandatory_fees_annual"] = extra["mandatory_fees_annual"]
            cid = f"{uni}-cost-{slug}-{c['residency']}"
            doc = {
                "_id": f"costProfile-{cid}", "_type": "costProfile", "id": cid,
                "program_ref": ref(f"program-{prog_id}"),
                "residency_category_ref": ref(f"applicantCategory-{uni}-residency-{c['residency']}"),
                "academic_year": c["academic_year"], "currency": c["currency"],
                "tuition_annual": c["tuition_annual"], "tuition_basis": "institutional",
                "mandatory_fees_annual": c.get("mandatory_fees_annual", 0),
                "duration_years": p["duration_years"],
                "mandatory_fees_breakdown": [], "other_material_costs": [],
                "record_status": "VERIFIED", "verification_status": "VERIFIED",
                "last_checked": TODAY,
                "source_refs": [ref(src_ids[x], f"s{i+1}") for i, x in enumerate(c["source"] if isinstance(c["source"], list) else [c["source"]])],
                "extension_metadata": {"_type": "extensionMetadata", "fields": [
                    {"_key": "fee_note", "_type": "extensionMetadataFieldEntry", "key": "fee_note",
                     "value": c["note"], "value_type": "string"}]},
            }
            if extra and extra["note"]:
                doc["extension_metadata"]["fields"].append(
                    {"_key": "compulsory_fees_note", "_type": "extensionMetadataFieldEntry",
                     "key": "compulsory_fees_note", "value": extra["note"], "value_type": "string"})
            check_numbers(c["note"].replace(f"{c['tuition_annual']:,}", ""), c["source"], f"{c['residency']} fee note")
            if living:
                doc["estimated_living_costs_annual"] = living["estimated_living_costs_annual"]
                doc["living_cost_source_note"] = living["living_cost_source_note"]
                doc["living_cost_source_basis"] = living["living_cost_source_basis"]
            muts.append({"createOrReplace": doc})

        # entry requirements, one per curriculum
        for a in r.get("admissions", []):
            label, cat = CURRICULA[a["curriculum"]]
            check_numbers(a["threshold"], a["source"], f"{a['curriculum']} threshold")
            for t in a.get("tests", []):
                check_numbers(t.get("notes", ""), a["source"], f"{a['curriculum']} test note")
            langs = []
            e = a.get("english")
            if e and e.get("from_existing"):
                ex = sanity(f'*[_id=="{e["from_existing"]}"][0]{{language_requirements, program_ref}}')
                if not ex or not ex["program_ref"]["_ref"].startswith(f"program-{uni}"):
                    fail(f"{where}: english from_existing {e['from_existing']} missing or another university")
                langs = ex["language_requirements"]
            elif e:
                check_numbers(e["min_score"], e["source"], "english")
                langs = [{"_key": "lr1", "_type": "languageRequirement", "language": "English",
                          "test_name": e["test_name"], "min_score": e["min_score"], "notes": e.get("notes", "")}]
            aid = f"{uni}-admreq-{slug}-{a['curriculum']}"
            cat_id = f"applicantCategory-{uni}-{cat}"
            categories_needed[cat_id] = {"uni": uni, "label": label, "cat": cat}
            src_list = [a["source"]] + ([e["source"]] if e and e.get("source") and e["source"] != a["source"] else [])
            muts.append({"createOrReplace": {
                "_id": f"admissionsRequirement-{aid}", "_type": "admissionsRequirement", "id": aid,
                "program_ref": ref(f"program-{prog_id}"),
                "prior_curriculum_category_ref": ref(cat_id),
                "curriculum_type": label, "academic_threshold": a["threshold"],
                "academic_year": p["entry_year"], "required_subjects": a.get("required_subjects", []),
                "standardized_tests": [
                    {"_key": f"t{i+1}", "_type": "testRequirement", "test_name": t["name"],
                     "required": t.get("required", "required"), "notes": t.get("notes", "")}
                    for i, t in enumerate(a.get("tests", []))],
                "language_requirements": langs,
                "record_status": "VERIFIED", "verification_status": "VERIFIED", "last_checked": TODAY,
                "source_refs": [ref(src_ids[k], f"s{i+1}") for i, k in enumerate(src_list)],
            }})

        # programme-specific deadline
        d = r.get("deadline")
        if d:
            q = norm(quotes[d["source"]])
            y, m, day = d["date"][:10].split("-")
            month = MONTHS[int(m) - 1]
            if not (re.search(rf"\b{int(day)}\b", q) and y in q and re.search(rf"\b{month[:3]}({month[3:]})?\b", q)):
                fail(f"{where}: deadline {d['date']} not in the quotes of source '{d['source']}'")
            did = f"{uni}-decisionplan-{slug}-{p['entry_year'][:4]}"
            muts.append({"createOrReplace": {
                "_id": f"decisionPlan-{did}", "_type": "decisionPlan", "id": did,
                "university_ref": ref(f"university-{uni}"), "program_ref": ref(f"program-{prog_id}"),
                "academic_year": p["entry_year"], "application_deadline": d["date"],
                "application_platform": d.get("platform", p.get("platform", "")), "binding": False,
                "plan_type": "program_specific_stage", "extension_metadata": {"note": f"Round: {d['round']}"},
                "notes": d.get("note", ""), "last_checked": TODAY,
                "record_status": "VERIFIED", "verification_status": "SUPPORTED",
                "source_refs": [ref(src_ids[d["source"]], "s1")],
            }})

    # Curriculum categories that don't exist yet (e.g. Indian CBSE at a UK university)
    existing = set(sanity('*[_type=="applicantCategory"]._id'))
    for cid, c in categories_needed.items():
        if cid not in existing:
            muts.append({"createOrReplace": {
                "_id": cid, "_type": "applicantCategory", "id": cid.removeprefix("applicantCategory-"),
                "university_ref": ref(f"university-{c['uni']}"), "dimension": "prior_curriculum",
                "label": c["label"], "description": c["label"],
            }})
    # Residency categories must already exist (fees are always for an existing fee group)
    for m in muts:
        d = m["createOrReplace"]
        if d["_type"] == "costProfile" and d["residency_category_ref"]["_ref"] not in existing:
            fail(f"{d['_id']}: residency category {d['residency_category_ref']['_ref']} doesn't exist")

    # Source records that already exist (same URL, same id) are kept as they are.
    existing_src = set(sanity('*[_type=="sourceRecord"]._id'))
    muts = [m for m in muts if not (m["createOrReplace"]["_type"] == "sourceRecord" and m["createOrReplace"]["_id"] in existing_src)]
    ids = [m["createOrReplace"]["_id"] for m in muts]
    dupes = {i for i in ids if ids.count(i) > 1 and not i.startswith("sourceRecord-")}
    if dupes:
        fail(f"duplicate ids: {sorted(dupes)}")
    seen, out = set(), []
    for m in muts:
        i = m["createOrReplace"]["_id"]
        if i in seen:
            continue
        seen.add(i)
        out.append(m)
    Path(out_path).write_text("".join(json.dumps(m, ensure_ascii=False) + "\n" for m in out))
    print(f"OK: {len(files)} programmes, {len(out)} mutations → {out_path}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
