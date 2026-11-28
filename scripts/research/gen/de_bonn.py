"""University of Bonn (THE #94): every Bachelor of Science, Bachelor of Arts (major subject / two-subject) and
international BA in the university's "Studiengänge A-Z" (written 2026-11-28; list in de_bonn_urls.txt). Left out:
minor-subject entries (Begleitfach) and teacher-training (Lehramt) combinations. Each programme's key facts (degree,
model, language, standard length) are quoted from its own page. Fees: no tuition; semester contribution "around
EUR 300 per semester" (applications page). Living: "roughly €1,000 a month" (costs page).
  python3 -I scripts/research/gen/de_bonn.py
"""
import os, re, sys, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, slugify, PAGES
from us_fields import field_for

ORG = "University of Bonn"
FEE = src("3214d133c7d2", "Applications from International Students | University of Bonn", ORG,
          ["Public universities in Germany do not charge tuition fees, only semester fees. At the University of Bonn, these are around EUR 300 per semester (EUR 600 per year).",
           "around EUR 300 per semester", "(EUR 600 per year)"])
LIV = src("c01c09ecc935", "Costs and Financing for International Students | University of Bonn", ORG,
          ["The University of Bonn does not charge tuition fees.", "Living expenses for a student in Bonn amount to roughly €1,000 a month and will mainly go on your rent."])
BFIELD = {"Agrarwissenschaften": "Agriculture", "Altamerikanistik und Ethnologie": "Anthropology", "Archäologien": "Archaeology",
          "Asiatische und Islamische Kunstgeschichte": "Art History", "Asienwissenschaften": "Asian Studies", "Cyber Security": "Computer Science",
          "Deutsch als Zweit- und Fremdsprache": "Linguistics", "Deutsch-Französische Studien": "Languages", "Deutsch-Italienische Studien": "Languages",
          "Ernährungs- und Lebensmittelwissenschaften": "Nutrition Sciences", "Evangelische Theologie und Hermeneutik": "Theology", "Französistik": "French",
          "Geodäsie und Geoinformation": "Geography", "Geographie": "Geography", "Geowissenschaften": "Earth Sciences", "Germanistik": "German",
          "Germanistik, Vergleichende Literatur- und Kulturwissenschaft": "German", "Geschichte": "History", "Griechische Literatur der Antike und ihr Fortleben": "Classics",
          "Hispanistik": "Spanish", "Informatik": "Computer Science", "Italianistik": "Italian", "Katholische Theologie": "Theology", "Komparatistik": "Comparative Literature",
          "Kunstgeschichte": "Art History", "Lateinamerika- und Altamerikastudien": "Latin American Studies", "Lateinische Literatur der Antike und ihr Fortleben": "Classics",
          "Medienwissenschaft": "Media and Communication", "Meteorologie und Geophysik": "Meteorology", "Molekulare Biomedizin": "Biomedical Science",
          "Mongolistik": "Asian Studies", "Musikwissenschaft/ Sound Studies": "Music", "Physik": "Physics", "Politik und Gesellschaft": "Politics",
          "Romanistik": "Languages", "Skandinavistik": "Languages", "Sprache und Kommunikation in der globalisierten Mediengesellschaft": "Linguistics",
          "Südasienwissenschaft": "Asian Studies", "Südostasienwissenschaft": "Asian Studies", "Tibetologie": "Asian Studies",
          "Vergleichende Religionswissenschaft": "Religious Studies", "Volkswirtschaftslehre": "Economics", "Wirtschaftswissenschaften": "Economics"}
LANG = {"Deutsch": "de", "Englisch": "en", "Französisch": "fr", "Italienisch": "it", "Spanisch": "es"}
first, seen = None, set()
for u in open(os.path.join(os.path.dirname(__file__), "de_bonn_urls.txt")).read().split():
    pid = hashlib.sha1(u.encode()).hexdigest()[:12]
    t = re.sub(r"\s+", " ", (PAGES / f"{pid}.txt").read_text(errors="replace"))
    k = re.search(r"Keyfacts Studienabschluss (.+?) Studienmodell (.+?) Unterrichtssprache (.+?) Regelstudienzeit (\d+) Semester", t)
    title = t[: t.index(" — Universität Bonn")].strip()
    if not k:
        print("skip", u); continue
    deg, model, langs, sem = k.group(1), k.group(2), k.group(3), int(k.group(4))
    C = src(pid, f"{title} — Universität Bonn", ORG, [f"{title} — Universität Bonn", k.group(0)])
    if first is None:
        first = C
        spec("de-bonn", ORG, ["Universität Bonn", "Rheinische Friedrich-Wilhelms-Universität Bonn", "Uni Bonn"], "public", "https://www.uni-bonn.de",
             ("de", "Germany", "EUR"), ("de-bonn", "Bonn"), {"main": LIV, "fees": FEE},
             [("all-students", "All students", "University of Bonn: no tuition fees; semester contribution.", "fees")])
    name = f"{title} ({model})" if model not in ("Mono", "Ein-Fach") else title
    slug = slugify(f"{deg} {name}".replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss"))[:70].rstrip("-")
    if slug in seen:
        continue
    seen.add(slug)
    lang = [LANG[w] for w in langs.split() if w in LANG] or ["de"]
    prog("de-bonn", slug, {"course": C, "fees": FEE, "liv": LIV},
         {"name": name, "degree_type": deg, "field": BFIELD.get(title) or field_for(title), "faculty": "", "duration_years": sem / 2, "duration_source": "course",
          "languages": lang, "entry_year": "2027", "platform": "", "source": "course",
          "summary": f"{title}, {deg} ({model}), University of Bonn; regular duration {sem} semesters, taught in {langs}.",
          "application_requirements": []},
         [{"residency": "all-students", "currency": "EUR", "tuition_per_term": 0, "terms_per_year": 2,
           "terms_evidence": ["around EUR 300 per semester", "(EUR 600 per year)"], "mandatory_per_term": 300,
           "academic_year": "current (page undated)", "source": "fees",
           "note": "No tuition fees; semester contribution around EUR 300 per semester (EUR 600 per year).",
           "living": {"monthly": [1000], "months": 12, "yearly": [], "source": "liv", "kind": "genuine_cost_of_living_estimate",
                      "note": "Living expenses in Bonn: roughly €1,000 a month (university estimate), €12,000 a year (our calculation)."}}], [])
print("de-bonn", len(seen))
