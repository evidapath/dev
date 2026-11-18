"""UNSW Sydney single bachelor's degrees (written 2026-11-18), same pattern as
biology/au-unsw-science.json: 2026 indicative international fees (the page's embedded data
says which figure is international), 2026 A-level and IB offer scores (a guide only).
  python3 -I scripts/research/gen/au_unsw.py
"""
import hashlib, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import write

PAGES = Path(__file__).resolve().parents[3] / ".research-cache/pages"
U = "https://www.unsw.edu.au/study/undergraduate/{}?studentType=International"
SCALE = "Entry scores are calculated from the best three or four A2 subjects (excluding repeated subjects) using the following values: A*=6, A=5, B=4, C=3, D=2, E=1."
INCL = ("Indicative fees to complete the degree/program include tuition plus an estimate of study-related costs of "
        "approximately $1,000 per year and have been calculated based on percentage increase for every year of the degree/program")

# folder, slug, page, name, field
COURSES = [
    ("economics", "economics", "bachelor-of-economics", "Economics", "Economics"),
    ("humanities", "arts", "bachelor-of-arts", "Arts", "Arts"),
    ("mathematics", "actuarial-studies", "bachelor-of-actuarial-studies", "Actuarial Studies", "Actuarial Studies"),
    ("mathematics", "data-science-decisions", "bachelor-of-data-science-and-decisions", "Data Science and Decisions", "Data Science"),
    ("biology", "medical-science", "bachelor-of-medical-science", "Medical Science", "Medical Science"),
    ("politics", "international-studies", "bachelor-of-international-studies", "International Studies", "International Relations"),
    ("humanities", "media-communication-journalism", "bachelor-of-media-communication-and-journalism", "Media (Communication and Journalism)", "Media and Communication"),
]


def build(folder, slug, page_name, name, field):
    url = U.format(page_name)
    page = hashlib.sha1(url.encode()).hexdigest()[:12]
    t = re.sub(r"\s+", " ", (PAGES / f"{page}.txt").read_text())
    raw = (PAGES / f"{page}-raw.txt").read_text()
    g = lambda p, s=t: re.search(p, s).group(0)
    years = g(r"\d Year\(s\)")
    codes = g(r"UAC code \d+ Program code \d+")
    scores = g(r"2026 A levels [\d.]+ 2026 IB Diploma [\d.]+")
    total_c = g(r'const feescompletedegree = isInternational \? "\$[\d,]+\*" : "\$[\d,]+\*"', raw)
    first_c = g(r'const feesfirstyear = isInternational \? "\$[\d,]+\*" : "\$[\d,]+\*"', raw)
    year_c = g(r'const feesyear = isInternational \? "2026" : "2026"', raw)
    total = re.search(r'\? "\$([\d,]+)', total_c).group(1)
    first = re.search(r'\? "\$([\d,]+)', first_c).group(1)
    pair = f"2026 Indicative first year full fee ${first}* 2026 Indicative full fee to complete degree ${total}*"
    assert pair in t and SCALE in t and INCL in t, slug
    dur = int(years[0])
    alev, ibs = re.match(r"2026 A levels ([\d.]+) 2026 IB Diploma ([\d.]+)", scores).groups()
    quotes = [years, codes, scores, SCALE, pair, INCL]
    ak = re.search(r"Assumed knowledge (.+?) Adjustment Factors", t)
    ak_txt = ""
    if ak and ak.group(1).strip() not in ("None", ""):
        quotes.append(f"Assumed knowledge {ak.group(1).strip()}")
        ak_txt = f" UNSW assumes knowledge of: {ak.group(1).strip()} (NSW subjects)."
    uac, prog = re.findall(r"\d+", codes)
    r = {
        "uni": "au-unsw", "slug": slug,
        "sources": {
            "course": {"url": url, "page": page, "title": f"Bachelor of {name} | UNSW Sydney", "organization": "UNSW Sydney", "quotes": quotes},
            "coursedata": {"url": url, "page": f"{page}-raw", "title": f"Bachelor of {name} | UNSW Sydney (fee data in the page)",
                           "organization": "UNSW Sydney", "quotes": [year_c, total_c, first_c]},
        },
        "program": {"name": name, "degree_type": "Bachelor", "field": field, "faculty": "", "duration_years": dur,
                    "languages": ["en"], "entry_year": "2027 entry", "platform": "UAC", "source": "course",
                    "summary": f"Bachelor of {name} (UAC {uac}, program {prog}), {dur} years.", "application_requirements": []},
        "costs": [{"residency": "international", "currency": "AUD", "tuition_formula": f"{total.replace(',', '')}/{dur}",
                   "academic_year": "2026 indicative fees", "source": ["coursedata", "course"],
                   "living_from": "costProfile-au-unsw-cost-beng-hons-international",
                   "note": (f"International, 2026 indicative: ${first} for the first year and ${total} for the whole degree "
                            f"(UNSW says the whole-degree figure includes about $1,000 a year of study-related costs and yearly increases). "
                            f"Shown as the whole-degree fee spread over {dur} years.")}],
        "admissions": [
            {"curriculum": "a-level", "source": "course", "required_subjects": [], "tests": [],
             "threshold": f"Bachelor of {name}: A-level score of {alev} from the best three or four A2 subjects (A*=6, A=5, B=4, C=3, D=2, E=1). This is the score that got an offer in 2026, a guide only.{ak_txt}"},
            {"curriculum": "ib", "source": "course", "required_subjects": [], "tests": [],
             "threshold": f"Bachelor of {name}: IB Diploma {ibs}. This is the score that got an offer in 2026, a guide only.{ak_txt}"},
        ],
    }
    write(folder, r)
    print(slug, dur, codes, scores, first, total, ak_txt)


for c in COURSES:
    build(*c)
