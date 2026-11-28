"""Hebrew University of Jerusalem (THE #169): the 3-year international BA (English-taught double major), one
record per published track (written 2026-11-28). Fee table on the Rothberg International School "BA Degree
Tuition" page (tabs 2025-26 and 2026-27; the same amounts appear in the page text).
  python3 -I scripts/research/gen/il_huji.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog, slugify

ORG = "Hebrew University"
BA = src("d5f468c08f0f", "BA English Programs | Hebrew University", ORG,
         ["If you prefer to study in English, Hebrew University offers a 3-year international BA degree",
          "choose 2 out of 3 fields of specialization – liberal arts, business, and English – and design the double-major degree",
          "Immerse yourself in Jerusalem's captivating energy"])
FE = src("09a290847598", "BA Degree Tuition | Rothberg International School, Hebrew University", ORG,
         ["BA Degree Tuition 2025-26 2026-27",
          "Business Administration & Liberal Arts Track US $120 US $15,500 US $7,330 US $770 US $23,720 Business Administration & English Track US $120 US $15,500 US $7,330 US $770 US $23,720 Liberal Arts & English Track US $120 US $15,500 US $7,330 US $770 US $23,720",
          "RIS reserves the right to change fees at any time."])
spec("il-huji", ORG, ["Hebrew University", "HUJI"], "public", "https://en.huji.ac.il", ("il", "Israel", "ILS"), ("il-jerusalem", "Jerusalem"),
     {"main": BA, "fees": FE}, [("international", "International students", "Tuition for the English-taught international BA.", "fees")])
for name, field in (("Business Administration & Liberal Arts", "Business"), ("Business Administration & English", "Business"), ("Liberal Arts & English", "Liberal Arts")):
    prog("il-huji", "ba-" + slugify(name), {"course": BA, "fees": FE},
         {"name": name, "degree_type": "BA (double major)", "field": field, "faculty": "", "duration_years": 3, "duration_source": "course",
          "languages": ["en"], "entry_year": "", "platform": "", "source": "course",
          "summary": f"International BA, {name} track, Hebrew University of Jerusalem; a 3-year double-major degree taught in English.",
          "application_requirements": []},
         [{"residency": "international", "currency": "USD", "tuition_annual": 15500, "academic_year": "2025-26 / 2026-27 (BA Degree Tuition page)", "source": "fees",
           "note": "Tuition US $15,500 a year; health insurance US $770; application fee US $120 (non-refundable). Fees may change.",
           "living": {"monthly": [], "months": 12, "yearly": [7330], "source": "fees", "kind": "official_housing_only",
                      "note": "Housing US $7,330 a year (university figure; food and other costs not included)."}}], [])
print("wrote il-huji")
