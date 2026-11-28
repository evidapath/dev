"""Abu Dhabi University (THE #5 =): every undergraduate programme in ADU's Program Finder (written 2026-11-28).
List from the finder's own data feed (/api/program-finder/programs, 38 undergraduate entries); each programme's
facts (duration, credits, campuses, language) are quoted from its own detail page. Bachelor of Law (Arabic) is left
out: its page gives no credit total. Fees: "Tuition and Fee Rates, Academic Year 2026-2027" PDF, Abu Dhabi Campus
table, AED per credit hour by college; yearly tuition = rate x credits / years (our calculation). Al Ain and Dubai
campuses have their own tables (not stored).
  python3 -I scripts/research/gen/ae_adu.py
"""
import os, re, sys, json, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, slugify, PAGES

FEED = json.loads((PAGES / "b29a7967d2f5.html").read_text())
ORG = "Abu Dhabi University"
FQ = {1620: "Arts, Education and Social Sciences (BA in Digital Media and Strategic Communication) 1620",
      1680: "Arts, Education and Social Sciences (Mass Communication Arabic), (BA in Film and Media Production) 1680",
      1715: "Arts, Education and Social Sciences (BA in International Relations), (BA in Psychology) 1715",
      1890: "Arts, Education and Social Sciences (BA in Video Game Design) 1890",
      1800: "Business 1800", 2000: "Engineering 2000", 2085: "Health Sciences 2085",
      1745: "Other Health Sciences Programs (BSc in Environmental Health & Safety, and BSc in Public Health) 1745"}
FEES = src("adu-fees", "Tuition and Fee Rates, Academic Year 2026-2027 | Abu Dhabi University", ORG,
           ["Abu Dhabi University Tuition and Fee Rates Academic Year 2026-2027",
            "Undergraduate Tuition And Fee Rates | Abu Dhabi Campus Academic Year 2026 - 2027",
            "Registration Fee (Non-refundable; Paid once upon admission) 2850", "Healthcare Services 110 55 Student Services 350 175",
            "The above fees are subject to VAT 5% excluding the Accommodation and the transportation fees."] + list(FQ.values()))


def rate(slug, college):
    if "digital-media" in slug: return 1620
    if "film-and-media" in slug or "mass-communication" in slug: return 1680
    if "international-relations" in slug or slug == "bachelor-of-arts-in-psychology": return 1715
    if "video-game" in slug: return 1890
    if college == "College of Business": return 1800
    if college == "College of Engineering": return 2000
    if "environmental-health" in slug or "public-health" in slug: return 1745
    if college == "College of Health Sciences": return 2085
    return None


FIELD = {"architecture": "Architecture", "digital-media": "Media and Communication", "film-and-media": "Media and Communication",
         "international-relations": "International Relations", "arts-in-psychology": "Psychology", "clinical-psychology": "Psychology",
         "video-game": "Design", "business-administration": "Business", "mass-communication": "Media and Communication",
         "artificial-intelligence-engineering": "Computer Science", "aviation": "Aviation", "biomedical": "Biomedical Engineering",
         "chemical-engineering": "Chemical Engineering", "civil-engineering": "Civil Engineering", "computer-engineering": "Computer Science",
         "cybersecurity": "Computer Science", "electrical-engineering": "Electrical and Electronic Engineering", "environmental-health": "Public Health",
         "nutrition": "Nutrition Sciences", "industrial-engineering": "Engineering", "information-technology": "Computer Science",
         "interior-design": "Design", "mechanical-engineering": "Mechanical Engineering", "medical-laboratory": "Biomedical Science",
         "genetics": "Genetics", "public-health": "Public Health", "renewable": "Engineering", "software-engineering": "Computer Science",
         "accounting": "Accounting", "finance": "Finance", "marketing": "Marketing", "human-resources": "Business"}
field = lambda s: next(v for k, v in sorted(FIELD.items(), key=lambda kv: -len(kv[0])) if k in s)

first = None
for it in FEED["items"]:
    if it["studyLevel"] != "Undergraduate":
        continue
    s = it["urlName"]
    pid = hashlib.sha1(f"https://adu.ac.ae/academics/program-finder/programdetail/{s}".encode()).hexdigest()[:12]
    t = re.sub(r"\s+", " ", (PAGES / f"{pid}.txt").read_text(errors="replace"))
    q = re.search(r"Quick Facts Duration (\d) Years Credits (\d+) Campuses (.*?) Mode (.*?) Language (\w+)", t)
    r = rate(s, it["college"])
    if not q or not r:
        print("skip", s); continue
    years, credits, lang = int(q.group(1)), int(q.group(2)), q.group(5)
    name = t[: t.index(" AR EN Apply Now")].strip()
    C = src(pid, f"{name} | Abu Dhabi University", ORG, [f"{name} AR EN Apply Now", q.group(0)])
    if first is None:
        first = C
        spec("ae-adu", ORG, ["ADU"], "private", "https://www.adu.ac.ae", ("ae", "United Arab Emirates", "AED"), ("ae-abu-dhabi", "Abu Dhabi"),
             {"main": FEES, "fees": FEES}, [("all-students", "All students (Abu Dhabi campus)", "ADU per-credit-hour tuition, Abu Dhabi campus, 2026-2027.", "fees")])
    prog("ae-adu", slugify(name)[:80].rstrip("-"), {"course": C, "fees": FEES},
         {"name": name, "degree_type": "Bachelor", "field": field(s), "faculty": it["college"], "duration_years": years, "duration_source": "course",
          "languages": ["ar" if lang == "Arabic" else "en"], "entry_year": "2026-2027", "platform": "", "source": "course",
          "summary": f"{name}, {it['college']}, Abu Dhabi University; {years} years, {credits} credits, taught in {lang}; campuses: {q.group(3)}.",
          "application_requirements": []},
         [{"residency": "all-students", "currency": "AED", "tuition_per_credit": r, "degree_credits": credits, "credits_source": "course",
           "academic_year": "2026-2027", "source": "fees",
           "note": f"Abu Dhabi campus, 2026-2027: AED {r} per credit hour × the programme's credit total ÷ its years (our calculation). Plus per Fall/Spring semester: healthcare services AED 110 and student services AED 350; one-time registration fee AED 2850. Fees are subject to VAT 5% (not accommodation or transport)."}],
         [])
print("wrote ae-adu")
