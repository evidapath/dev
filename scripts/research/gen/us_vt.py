"""Virginia Tech (THE #138 =): every bachelor's major on vt.edu "Undergraduate Majors" whose own page names its
college and degree type (written 2026-11-28). Left out: "undecided"/exploratory entries, the associate degree,
pre-professional tracks, and majors whose page carries no college tag (listed in the queue file).
Costs: Financial Aid "Estimated Cost of Attendance, Out-of-State, Undergraduate, On-Campus, 2026-2027 Academic
Year" (UPDATED 05/13/2026 sheet; the original sheet at the same address gives slightly different figures). The
sheet's college/major fees are added to tuition for the majors they name. Length: catalog Undergraduate Policies
(four-year degree programs; five-year Bachelor of Architecture and Bachelor of Landscape Architecture).
  python3 -I scripts/research/gen/us_vt.py
"""
import os, re, sys, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, slugify, PAGES
from us_fields import field_for

ORG = "Virginia Tech"
S = os.path.join(os.path.dirname(__file__), "us_vt_urls.txt")
FQ = {750: "College of Agriculture and Biochemistry Majors: $750", 1500: "College of Architecture: $1,500*",
      2000: "College of Engineering: $2,000", 2001: "Building Construction: $2,000", 2550: "Pamplin College of Business: $2,550",
      1000: "College of Science $1,000"}
MF = src("vt-UGNRON_UPDATED_05132026", "Estimated Cost of Attendance, Out-of-State, Undergraduate, On-Campus, 2026-2027 | Virginia Tech Financial Aid", ORG,
         ["Estimated Cost of Attendance Out-of-State, Undergraduate, On-Campus 2026-2027 Academic Year",
          "Tuition $36,428", "Fees $3,754", "Housing $10,394", "Food $6,826",
          "*(Includes majors in Architecture, Industrial Design, Interior Design, and Landscape Architecture)"] + list(FQ.values()))
MA = src("86ac851d0e8d", "About | Virginia Tech", ORG, ["Main campus located in Blacksburg, Virginia", "Part of every Virginia Tech plate purchase funds scholarships"])
MY = src("570b097af881", "Undergraduate Policies | Virginia Tech Undergraduate Catalog", ORG,
         ["Virginia Tech offers four-year degree programs leading to a Bachelor of Arts, Bachelor of Science, or Bachelor of Fine Arts degree.",
          "Also offered are five-year Bachelor of Architecture and Bachelor of Landscape Architecture programs."])


def extra(name, college):
    if name in ("Architecture", "Industrial Design", "Interior Design", "Landscape Architecture"): return 1500, FQ[1500]
    if name == "Building Construction": return 2000, FQ[2001]
    if college == "College of Agriculture and Life Sciences" or name == "Biochemistry": return 750, FQ[750]
    if college == "College of Engineering": return 2000, FQ[2000]
    if college == "Pamplin College of Business": return 2550, FQ[2550]
    if college == "College of Science": return 1000, FQ[1000]
    return 0, ""


first = None
seen = set()
for u in open(S).read().split():
    pid = hashlib.sha1(u.encode()).hexdigest()[:12]
    t = re.sub(r"\s+", " ", (PAGES / f"{pid}.txt").read_text(errors="replace"))
    seg = t[t.rfind(" Tags "):] if " Tags " in t else ""
    c = re.search(r"Colleges (.*?) Degree Types (.*?) (?:Keywords|Undergraduate Major|Related|Get Directions)", seg)
    if not c:
        continue
    college, types = c.group(1).strip(), c.group(2)
    deg = re.match(r"(Bachelor of (?:Landscape Architecture|Architecture|Fine Arts|Arts|Science|Music))\b", types)
    hm = re.search(r"Study Abroad (.+?) (?=[A-Z][a-z]+ )", t)
    name_m = re.search(r"/ Undergraduate Majors / (.+?) / Explore", t)
    if not deg or not name_m or college.startswith("Pre-Professional") or "College of" not in college and "Pamplin" not in college:
        continue
    name = name_m.group(1).strip()
    if "undecided" in name.lower() or "Associate" in name or name.startswith("Pre-"):
        continue
    years = 5 if name in ("Architecture", "Landscape Architecture") and "Bachelor of Architecture" in types or name == "Landscape Architecture" and "Bachelor of Landscape" in types else 4
    q = [f"/ Undergraduate Majors / {name} / Explore", f"Colleges {college} Degree Types {deg.group(1)}", "© 2026 Virginia Polytechnic Institute and State University.", "Apply to Virginia Tech now"]
    C = src(pid, f"{name} | Undergraduate Majors | Virginia Tech", ORG, q)
    if first is None:
        first = C
        spec("us-vt", ORG, ["Virginia Polytechnic Institute and State University", "VT", "Virginia Tech (Blacksburg)"], "public", "https://www.vt.edu",
             ("us", "United States", "USD"), ("us-blacksburg-va", "Blacksburg"), {"main": MA, "coa": MF},
             [("nonresident", "Out-of-state students", "Virginia Tech estimated cost of attendance, out-of-state undergraduate on campus, 2026-2027.", "coa")])
    slug = slugify(f"{deg.group(1)} {name}")[:60].rstrip("-")
    if slug in seen:
        continue
    seen.add(slug)
    add, fq = extra(name, college)
    cost = {"residency": "nonresident", "currency": "USD", "tuition_formula": f"{years}*(36428{'+' + str(add) if add else ''})/{years}",
            "mandatory_fees_annual": 3754, "academic_year": "2026-2027", "source": "coa",
            "note": "Out-of-state 2026-2027 estimate: tuition $36,428 + fees $3,754" + (f"; plus the programme fee on the cost sheet ({fq})" if add else "") + ". Estimates; actual charges can differ by college, major and housing.",
            "living": {"monthly": [], "months": 9, "yearly": [10394, 6826], "source": "coa", "kind": "genuine_cost_of_living_estimate",
                       "note": "On campus 2026-2027: housing $10,394 + food $6,826 = $17,220 (our calculation)."}}
    prog("us-vt", slug, {"course": C, "y": MY, "coa": MF},
         {"name": name, "degree_type": deg.group(1), "field": field_for(name), "faculty": college, "duration_years": years, "duration_source": "y",
          "languages": ["en"], "entry_year": "2026-2027", "platform": "", "source": "course",
          "summary": f"{name} ({deg.group(1)}), {college}, Virginia Tech; " + ("a five-year professional degree." if years == 5 else "Virginia Tech's bachelor's degrees are four-year programmes."),
          "application_requirements": []},
         [cost], [])
print("us-vt", len(seen))
