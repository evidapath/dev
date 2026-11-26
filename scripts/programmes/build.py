#!/usr/bin/env python3
"""Turn programme research files into Sanity mutations, refusing anything unsourced.

  python3 -I scripts/programmes/build.py <research-dir> <pages-dir> <out.ndjson> [<new-university base.ndjson>]

Each research file (JSON, one programme) lists its sources with verbatim quotes
copied from the official page. Before writing anything this script checks, and
stops on the first failure:

  1. every quote appears word for word in the saved text of its page
     (<pages-dir>/<page>.txt, saved by the fetcher when the page was read);
  2. every number in a value we store (fees, grades, scores, years, places)
     appears in a quote of the source that value cites;
  3. deadlines: the day, the month name and the year appear in a cited quote;
  4. the faculty/school named appears on the programme's page.

Values copied from records already in Sanity ("from_existing", "living_from",
"fees_from", "college") are not re-checked
here: they were verified when they were added, and the record id is kept.

"college": where students are admitted to a college and choose the major later
(US universities), a new major reuses the entry requirements and fees of an
existing programme in the same college: {"from": "<program id>", "quote": "<a
quote of a university page saying the major sits in that college>",
"copy": ["admissions", "costs"]}. It stops if a copied requirement names the
other programme, or lists required subjects without a "subjects_quote" showing the
same subjects apply to the new major's group.

Reads SANITY_READ_TOKEN from evidapath-navigator/.env.local only to copy those
existing records (living costs, English requirement). Never prints it.
"""

import datetime, json, re, sys, hashlib, subprocess, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TODAY = datetime.date.today().isoformat()  # date this build checked the quotes
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


def nums(s: str, quote: bool = True) -> set[str]:
    out = set()
    # Space-separated thousands in a quote ("7 000 EUR/year", "1 980 000 HUF") = 7000, 1980000.
    # Quotes only: a value we built may list separate numbers with spaces ("700 200 200").
    for m in (re.findall(r"\b\d{1,3}(?: \d{3})+\b", s) if quote else []):
        out.add(m.replace(" ", ""))
    # Swiss thousands in a quote ("4’380", "11'300") = 4380, 11300.
    for m in (re.findall(r"\b\d{1,3}(?:[’']\d{3})+\b", s) if quote else []):
        out.add(re.sub(r"[’']", "", m))
    # European format in a quote ("2.040,00 €" = 2040.00): also read it the English way.
    for m in re.findall(r"\b\d{1,3}(?:\.\d{3})+(?:,\d+)?\b|\b\d+,\d{2}\b", s):
        whole, _, dec = m.replace(".", "").partition(",")
        out.add(whole)
        if dec and dec.strip("0"):
            out |= {f"{whole}.{dec}", f"{whole}.{dec}".rstrip("0")}
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
    # The token goes to curl on stdin (-H @-), never in its arguments: an argument list
    # shows up in process listings and in tracebacks when a call fails.
    r = subprocess.run(["curl", "-s", "-H", "@-", url], input=f"Authorization: Bearer {token}\n",
                       capture_output=True, text=True)
    if r.returncode != 0:
        fail(f"Sanity query failed (curl exit {r.returncode}); try again")
    return json.loads(r.stdout)["result"]


def ref(_id: str, key: str | None = None):
    r = {"_ref": _id, "_type": "reference", "_weak": True}
    if key:
        r["_key"] = key
    return r


def main(research_dir: str, pages_dir: str, out_path: str, base_path: str | None = None):
    files = sorted(Path(research_dir).glob("*.json"))
    if not files:
        fail("no research files")
    muts: list[dict] = []
    categories_needed: dict[str, dict] = {}
    # A page can be a source for several subjects (e.g. one fee table). Every batch
    # writes the same source record with the quotes of all subjects, so applying the
    # batches in any order leaves the same excerpt.
    shared: dict[str, list[str]] = {}
    for other in sorted(Path(research_dir).resolve().parent.glob("*/*.json")):
        for s in json.loads(other.read_text())["sources"].values():
            k = s["url"] + ("#page-data" if s["page"].endswith("-raw") else "")
            shared.setdefault(k, [])
            shared[k] += [q for q in s["quotes"] if q not in shared[k]]
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
            missing = nums(str(value), quote=False) - nums(q_of(src))
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
                "excerpt": " ".join(shared.get(key_url, s["quotes"])), "retrieved_at": f"{TODAY}T00:00:00Z",
                "retrieval_method": f"Read by EvidaPath course-expansion pass {TODAY}; quotes checked against the saved page",
                "fields_supported": [], "notes": "",
            }})

        p = r["program"]
        # The faculty/school named must be on the programme's own page (or left blank).
        fac_page = Path(pages_dir) / f"{r['sources'][p['source']]['page']}.txt"
        if p.get("faculty") and norm(p["faculty"]) not in norm(fac_page.read_text()):
            fail(f"{where}: faculty '{p['faculty']}' isn't on the programme page")
        col = r.get("college")
        base_years = col and sanity(f'*[_id=="{col["from"]}"][0].duration_value')
        dq = norm(q_of(p.get("duration_source", p["source"])))
        word = {3: "three", 4: "four", 5: "five", 6: "six"}.get(p["duration_years"], "-")
        ordinal = {3: "third", 4: "fourth", 5: "fifth", 6: "sixth"}.get(p["duration_years"], "-")
        in_months = (f"{round(p['duration_years'] * 12)} months" in dq  # e.g. "36 months"
                     or re.search(rf"\b{p['duration_years'] * 2:g} semesters\b", dq) is not None  # e.g. BME's "7 semesters" = 3.5 years
                     or re.search(rf"\b{word}[- ](?:academic )?years?\b", dq) is not None  # e.g. "a four-year degree", "four academic years"
                     # the last year of a published typical course sequence (e.g. RIT's "Fifth Year"),
                     # only when no later year is named in the same quotes
                     or (re.search(rf"\b{ordinal} year\b", dq) is not None
                         and not any(re.search(rf"\b{o} year\b", dq) for n, o in {4: "fourth", 5: "fifth", 6: "sixth", 7: "seventh"}.items() if n > p["duration_years"])))
        later = [o for n, o in {4: "fourth", 5: "fifth", 6: "sixth", 7: "seventh"}.items()
                 if n > p["duration_years"] and re.search(rf"\b{o} year\b", dq)]
        if later:  # the programme's own sequence names a later year than the length given
            fail(f"{where}: duration {p['duration_years']} but the quotes name a '{later[0]} year'")
        if base_years != p["duration_years"] and not in_months:  # a college major's length can come from its college's record
            check_numbers(p["duration_years"], p.get("duration_source", p["source"]), "duration")
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
            if c.get("tuition_per_semester"):
                # Per-semester fee where the programme page gives "N semesters (Y years)" (e.g. ELTE):
                # semesters a year = N ÷ Y from that quote; yearly fee our calculation.
                sq = c["semesters_quote"]
                # A bare "N semesters" (e.g. Szeged) counts as N ÷ 2 years, as for programme lengths.
                m = re.fullmatch(r".*?(\d+) semesters(?: \((\d+) years?\))?.*", sq)
                if not m or norm(sq) not in norm(q_of(c["semesters_source"])):
                    fail(f"{where}: semesters_quote must be a quote of '{c['semesters_source']}' reading 'N semesters' or 'N semesters (Y years)'")
                sem_years = int(m.group(2)) if m.group(2) else int(m.group(1)) / 2
                if sem_years != p["duration_years"]:
                    fail(f"{where}: semesters_quote gives {sem_years:g} years, the programme {p['duration_years']}")
                check_numbers(c["tuition_per_semester"], c["source"], "per-semester fee")
                c["tuition_annual"] = round(c["tuition_per_semester"] * int(m.group(1)) / sem_years, 2)
            elif c.get("tuition_per_term"):
                # Per-term fee (e.g. Waterloo): the term fee is quoted; the terms per year
                # must be backed by quotes naming the terms (e.g. "fall term – September to
                # December", "winter term – January to April").
                check_numbers(c["tuition_per_term"], c["source"], "per-term fee")
                for q in c["terms_evidence"]:
                    if norm(q) not in norm(q_of(c["source"])):
                        fail(f"{where}: terms_evidence quote isn't among the fee's quotes: {q}")
                if len(c["terms_evidence"]) != c["terms_per_year"]:
                    fail(f"{where}: give one quote per term for terms_per_year")
                c["tuition_annual"] = round(c["tuition_per_term"] * c["terms_per_year"], 2)
                if c.get("mandatory_per_term"):
                    check_numbers(c["mandatory_per_term"], c["source"], "per-term compulsory fees")
                    c["mandatory_fees_annual"] = round(c["mandatory_per_term"] * c["terms_per_year"], 2)
                    c["_computed_fees"] = True
            elif c.get("tuition_per_credit") and c.get("credits_per_year"):
                # Per-credit fee with a published yearly credit load (e.g. CUD's "Cr Hrs per Year").
                check_numbers(f'{c["tuition_per_credit"]:.2f} {c["credits_per_year"]}', c["source"], "per-credit fee and yearly credits")
                c["tuition_annual"] = round(c["tuition_per_credit"] * c["credits_per_year"], 2)
            elif c.get("tuition_per_credit"):
                # Per-credit fee (e.g. UBC): rate × the degree's quoted credit total ÷ its years.
                # The credit total may be quoted on another source of the same record
                # ("credits_source", e.g. HCT: fee on the admissions page, credits in the catalogue).
                if c.get("credits_source"):
                    check_numbers(f'{c["tuition_per_credit"]:.2f}', c["source"], "per-credit fee")
                    check_numbers(c["degree_credits"], c["credits_source"], "degree credits")
                else:
                    check_numbers(f'{c["tuition_per_credit"]:.2f} {c["degree_credits"]}', c["source"], "per-credit fee and credits")
                c["tuition_annual"] = round(c["tuition_per_credit"] * c["degree_credits"] / p["duration_years"], 2)
            elif c.get("tuition_formula"):
                f_ = c["tuition_formula"]
                if not re.fullmatch(r"[\d+*/(). ]+", f_):
                    fail(f"{where}: tuition_formula may only hold numbers and + * / ( )")
                years = sum(int(x) for x in re.findall(r"(\d+)\*", f_))
                total_over_years = re.fullmatch(r"\s*\d+\s*/\s*(\d+(?:\.\d+)?)\s*", f_)  # published total ÷ years (e.g. 3.5)
                if total_over_years and float(total_over_years.group(1)) == p["duration_years"]:
                    years = p["duration_years"]
                if years != p["duration_years"] or not f_.replace(" ", "").endswith(f"/{p['duration_years']}"):
                    fail(f"{where}: tuition_formula must cover all {p['duration_years']} years and divide by them")
                check_numbers(re.sub(r"(\d+)\*", "", f_).split("/")[0], c["source"], "tuition_formula fees")
                c["tuition_annual"] = round(eval(f_, {"__builtins__": {}}))
            else:
                check_numbers(c["tuition_annual"], c["source"], f"{c['residency']} tuition")
            if not c.get("fees_from") and not c.get("_computed_fees"):
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
            elif c.get("living"):
                # Living costs quoted from the university's own page (a new university has no
                # record to copy from). Monthly items from the page; the yearly figure is our
                # calculation: sum of the quoted monthly amounts × the months given.
                lv = c["living"]
                if lv["kind"] not in ("genuine_cost_of_living_estimate", "official_housing_only"):
                    fail(f"{where}: living kind must be genuine_cost_of_living_estimate or official_housing_only")
                # Weekly items × 52 and yearly items (e.g. health insurance) may be added.
                check_numbers(" ".join(str(x) for x in lv["monthly"] + lv.get("weekly", []) + lv.get("yearly", [])), lv["source"], "living costs")
                if lv["months"] != 12 and norm(lv.get("months_quote", "-")) not in norm(q_of(lv["source"])):
                    fail(f"{where}: living months other than 12 need a months_quote among the source's quotes")
                annual = round(sum(lv["monthly"]) * lv["months"] + sum(lv.get("weekly", [])) * 52 + sum(lv.get("yearly", [])))
                if f"{annual:,}" not in lv["note"]:
                    fail(f"{where}: living note must state the yearly figure {annual:,}")
                check_numbers(lv["note"].replace(f"{annual:,}", "").replace(f"× {lv['months']}", "").replace("× 52", ""), lv["source"], "living note")
                living = {
                    "estimated_living_costs_annual": annual,
                    "living_cost_source_note": lv["note"],
                    "living_cost_source_basis": {"_type": "livingCostSourceBasis", "kind": lv["kind"],
                                                 "administering_body": r["sources"][lv["source"]]["organization"],
                                                 "description": lv["note"]},
                }
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
            check_numbers(c["note"].replace(f"{c['tuition_annual']:,.2f}", "").replace(f"{c['tuition_annual']:,}", ""), c["source"], f"{c['residency']} fee note")
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

        # entry requirements and fees shared by the whole college (see the top of this file)
        if col:
            if not col["from"].startswith(f"program-{uni}-"):
                fail(f"{where}: college.from {col['from']} belongs to another university")
            if norm(col["quote"]) not in norm(" ".join(quotes.values())):
                fail(f"{where}: college.quote isn't one of the quotes")
            base = sanity(f'*[_id=="{col["from"]}"][0]{{program_name, field_of_study}}')
            if not base:
                fail(f"{where}: college.from {col['from']} not found")
            names = {base["program_name"].lower(), base["field_of_study"].lower()} - {p["name"].lower(), p["field"].lower()}
            copied = sanity(f'*[_type in ["admissionsRequirement", "costProfile"] && program_ref._ref=="{col["from"]}" && !(_id in path("drafts.**"))]')
            kinds = set(col.get("copy", ["admissions", "costs"]))
            for d in copied:
                kind = "admissions" if d["_type"] == "admissionsRequirement" else "costs"
                if kind not in kinds:
                    continue
                if kind == "admissions":
                    text = d.get("academic_threshold", "").lower()
                    # Required subjects can only be copied when a quote says the same subjects
                    # apply to this group of majors (e.g. AUS: "Science majors ... Math and a Science subject").
                    shared_subjects = col.get("subjects_quote") and norm(col["subjects_quote"]) in norm(" ".join(quotes.values()))
                    if (d.get("required_subjects") and not shared_subjects) or any(n in text for n in names):
                        fail(f"{where}: {d['_id']} is specific to {base['program_name']}, not college-wide")
                    suffix = d["prior_curriculum_category_ref"]["_ref"].removeprefix(f"applicantCategory-{uni}-curriculum-")
                    nid = f"{uni}-admreq-{slug}-{suffix}"
                else:
                    suffix = d["residency_category_ref"]["_ref"].removeprefix(f"applicantCategory-{uni}-residency-")
                    nid = f"{uni}-cost-{slug}-{suffix}"
                    d["duration_years"] = p["duration_years"]
                doc = {k: v for k, v in d.items() if not k.startswith("_") or k == "_type"}
                doc.update({"_id": f"{d['_type']}-{nid}", "id": nid, "program_ref": ref(f"program-{prog_id}")})
                em = doc.setdefault("extension_metadata", {"_type": "extensionMetadata"})
                em.setdefault("fields", [])
                em["fields"] = [f_ for f_ in em["fields"] if f_.get("key") != "copied_from"] + [
                    {"_key": "copied_from", "_type": "extensionMetadataFieldEntry", "key": "copied_from",
                     "value": f"Same as {d['_id']}: entry requirements and fees shared by this college's programmes",
                     "value_type": "string"}]
                muts.append({"createOrReplace": doc})
            if not any(m["createOrReplace"].get("program_ref", {}).get("_ref") == f"program-{prog_id}"
                       and m["createOrReplace"]["_type"] == "admissionsRequirement" for m in muts) and "admissions" in kinds:
                fail(f"{where}: college.from {col['from']} has no entry requirements to copy")

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
    # A new university's base records (scripts/research/new_university.py) may still be a
    # pending file: its fee groups count as existing, and that file must be applied first.
    if base_path:
        existing |= {json.loads(l)["createOrReplace"]["_id"] for l in Path(base_path).read_text().splitlines() if l.strip()}
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

    # Source records that already exist (same URL, same id) are kept. Quotes now used
    # from that page that their excerpt lacks are added to the end; nothing already
    # there is removed (older records may rely on it).
    existing_src = {d["_id"]: d["excerpt"] or "" for d in sanity('*[_type=="sourceRecord"]{_id, excerpt}')}
    patches = []
    for m in muts:
        d = m["createOrReplace"]
        if d["_type"] != "sourceRecord" or d["_id"] not in existing_src:
            continue
        if d["_id"] in {p["patch"]["id"] for p in patches}:
            continue
        old_ex = existing_src[d["_id"]]
        url = d["url"] + ("#page-data" if d["_id"] != f"sourceRecord-ev-{hashlib.sha1(d['url'].encode()).hexdigest()[:12]}" else "")
        missing = [q for q in shared.get(url, []) if norm(q) not in norm(old_ex)]
        if missing:
            patches.append({"patch": {"id": d["_id"], "set": {"excerpt": " ".join([old_ex, *missing]).strip(), "retrieved_at": d["retrieved_at"]}}})
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
    out += patches
    Path(out_path).write_text("".join(json.dumps(m, ensure_ascii=False) + "\n" for m in out))
    print(f"OK: {len(files)} programmes, {len(out)} mutations ({len(patches)} source excerpts updated) → {out_path}")


if __name__ == "__main__":
    main(*sys.argv[1:5])
