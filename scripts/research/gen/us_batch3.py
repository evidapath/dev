"""Five US universities from THE's most-international list (written 2026-11-26): UC Berkeley (#62), Yale (#66),
Carnegie Mellon (#69), Johns Hopkins (#76), Georgia Tech (#77). One computer science bachelor each, fees and
on-campus housing + food from each university's own 2026-27 cost page. Admission is holistic at all five and no
grade threshold is published, so no admission rows are stored (the site shows "not published").
  python3 -I scripts/research/gen/us_batch3.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog


def one(uni, org, aliases, kind, site, city, main, sources, residency, slug, program, cost):
    spec(uni, org, aliases, kind, site, ("us", "United States", "USD"), city, {"main": main, **sources}, [residency])
    prog(uni, slug, sources, program, [cost], [])


def P(name, deg, faculty, src_key, summary, dur_src="course"):
    return {"name": name, "degree_type": deg, "field": "Computer Science", "faculty": faculty, "duration_years": 4,
            "duration_source": dur_src, "languages": ["en"], "entry_year": "2026-27", "platform": "", "source": src_key,
            "summary": summary, "application_requirements": []}


# UC Berkeley
ORG = "University of California, Berkeley"
INTL = src("f5a9f16ed599", "Requirements for International Students - Office of Undergraduate Admissions", ORG,
           ["International students in the U.S. on a visa cannot be classified as California residents for tuition purposes.",
            "Office of Undergraduate Admissions University of California, Berkeley 110 Sproul Hall #5800, Berkeley, CA 94720-5800"])
COA = src("1b27bebfa8c6", "Student Budgets (Cost of Attendance) - Financial Aid & Scholarships", ORG,
          ["New out-of-state students pay an additional Nonresident Supplemental Tuition of $39,270.",
           "New Students Starting in the 2026-27 Academic Year add Living Arrangement for 2026-27: Living in a Campus Residence Hall Living in an On-Campus Apartment Living in an Off-Campus Apartment Living with Relatives Tuition and Fees $18,214 $18,214 $18,214 $18,214 Housing $16,640 $20,500 n/a n/a Meal Plan $7,000 n/a n/a n/a Student Health Insurance Plan $5,066",
           "Final approved 2026-27 tuition and fee levels may be higher or lower than the amounts presented."])
EE = src("f46decf77b8d", "EECS Bachelor of Science - EECS at Berkeley", ORG,
         ["First-years are admitted directly into the EECS major and spend all four years in the program."])
one("us-berkeley", ORG, ["UC Berkeley", "Berkeley"], "public", "https://www.berkeley.edu", ("us-berkeley-ca", "Berkeley"), INTL,
    {"course": EE, "coa": COA, "intl": INTL},
    ("nonresident", "Nonresident students (including international students)", "Students who are not California residents for tuition purposes pay Nonresident Supplemental Tuition.", "coa"),
    "bs-electrical-engineering-and-computer-sciences",
    {**P("Electrical Engineering and Computer Sciences", "B.S.", "", "course",
         "EECS B.S., University of California, Berkeley; first-years are admitted directly into the major and spend all four years in it."),
     "field": "Computer Science"},
    {"residency": "nonresident", "currency": "USD", "tuition_formula": "4*(18214+39270)/4", "academic_year": "2026-27", "source": ["coa", "intl"],
     "note": "New students 2026-27: tuition and fees $18,214 plus Nonresident Supplemental Tuition $39,270 = $57,484 a year (our calculation); figures may not be final.",
     "living": {"monthly": [], "months": 12, "yearly": [16640, 7000], "source": "coa", "kind": "genuine_cost_of_living_estimate",
                "note": "Campus residence hall 2026-27: housing $16,640 + meal plan $7,000 = $23,640 (our calculation); health insurance ($5,066) not included."}})

# Yale
ORG = "Yale University"
REG = src("3028e6247def", "Requirements for the B.A. or B.S. Degree < Yale University", ORG,
          ["A. Requirements for the B.A. or B.S. Degree < Yale University",
           "A student may normally complete no more than eight terms of enrollment in order to fulfill these requirements.",
           "while the student was enrolled as a secondary school student in the New Haven area"])
YC = src("a765a3f85e9e", "Cost of Attendance | Yale Undergraduate Financial Aid", ORG,
         ["2026-27 Estimated Cost of Attendance for Yale Undergraduate Students $72,500 Tuition $185 Student Activity Fee $12,080 Housing $9,520 Food",
          "Planning for Four Years As you plan ahead for the next four years"])
YCS = src("ae4a4353955d", "Computer Science < Yale University", ORG,
          ["B.S. degree program The B.S. degree program requires a total of twelve term courses"])
one("us-yale", ORG, ["Yale", "Yale College"], "private", "https://www.yale.edu", ("us-new-haven-ct", "New Haven"), REG,
    {"course": YCS, "reg": REG, "coa": YC},
    ("international", "All undergraduates", "Yale College tuition is the same for all undergraduates.", "coa"),
    "bs-computer-science",
    P("Computer Science", "B.S.", "", "course", "Computer Science B.S., Yale College; eight terms of enrollment (four years).", dur_src="coa"),
    {"residency": "international", "currency": "USD", "tuition_annual": 72500, "academic_year": "2026-27", "source": "coa",
     "note": "Tuition $72,500 (2026-27); student activity fee $185 is separate.",
     "living": {"monthly": [], "months": 12, "yearly": [12080, 9520], "source": "coa", "kind": "genuine_cost_of_living_estimate",
                "note": "Yale College 2026-27: housing $12,080 + food $9,520 = $21,600 (our calculation)."}})

# Carnegie Mellon
ORG = "Carnegie Mellon University"
CMC = src("cb4224f5dcd9", "2026-2027 Undergraduate Tuition - Student Financial Services - Carnegie Mellon University", ORG,
          ["2026-2027 Undergraduate Tuition & Fees First-Years Entering Fall 2026 Per-Unit Tuition Rate - $969 RESIDENT COMMUTER Tuition $69,702 $69,702 Housing 1 11,700 0 Food 2 7,950 3,976"])
CMB = src("a9e52e92cd13", "Computer Science, B.S. < Carnegie Mellon University", ORG,
          ["these students should still be able to complete their degree in four years.",
           "Carnegie Mellon University 5000 Forbes Avenue Pittsburgh, PA 15213", "School of Computer Science"])
one("us-cmu", ORG, ["CMU", "Carnegie Mellon"], "private", "https://www.cmu.edu", ("us-pittsburgh-pa", "Pittsburgh"), CMB,
    {"course": CMB, "coa": CMC},
    ("international", "All undergraduates", "Carnegie Mellon undergraduate tuition is the same for all undergraduates.", "coa"),
    "bs-computer-science",
    P("Computer Science", "B.S.", "School of Computer Science", "course", "Computer Science B.S., School of Computer Science, Carnegie Mellon University; four years."),
    {"residency": "international", "currency": "USD", "tuition_annual": 69702, "academic_year": "2026-27 (first-years entering Fall 2026)", "source": "coa",
     "note": "Tuition $69,702 for first-years entering Fall 2026; university fees are separate.",
     "living": {"monthly": [], "months": 12, "yearly": [11700, 7950], "source": "coa", "kind": "genuine_cost_of_living_estimate",
                "note": "First-year resident 2026-2027: housing $11,700 + food $7,950 = $19,650 (our calculation)."}})

# Johns Hopkins
ORG = "Johns Hopkins University"
JC = src("e7c2af495756", "Cost and Tuition | Johns Hopkins Student Financial Services", ORG,
         ["2026-27 Academic Year On-Campus Living (Freshman)",
          "On-Campus Living (Freshman) Tuition* $68,670 Matriculation Fee (One-time only) $500 Living Expenses, Housing (On-Campus) $13,073 Living Expenses, Meals (On-Campus) $8,894",
          "3400 N Charles Street Levering Hall, Suite 102 Baltimore, MD 21218", "Johns Hopkins University Est. 1876"])
JR = src("5dd8553a7e8a", "Requirements for a Bachelor's Degree | Johns Hopkins University Academic Catalogue", ORG,
         ["in order to assure that they will complete requirements for graduation in four years."])
JB = src("09cca5084029", "Computer Science, Bachelor of Science | Johns Hopkins University Academic Catalogue", ORG,
         ["Computer Science, Bachelor of Science Whiting School of Engineering 2026-27 Edition"])
one("us-jhu", ORG, ["Johns Hopkins", "JHU"], "private", "https://www.jhu.edu", ("us-baltimore-md", "Baltimore"), JC,
    {"course": JB, "req": JR, "coa": JC},
    ("international", "All undergraduates", "Johns Hopkins undergraduate tuition is the same for all undergraduates.", "coa"),
    "bs-computer-science",
    P("Computer Science", "Bachelor of Science", "Whiting School of Engineering", "course", "Computer Science, Bachelor of Science, Whiting School of Engineering, Johns Hopkins University; four years.", dur_src="req"),
    {"residency": "international", "currency": "USD", "tuition_annual": 68670, "academic_year": "2026-27", "source": "coa",
     "note": "Tuition $68,670 (2026-27); one-time matriculation fee $500 in the first year.",
     "living": {"monthly": [], "months": 12, "yearly": [13073, 8894], "source": "coa", "kind": "genuine_cost_of_living_estimate",
                "note": "First-year on-campus 2026-27: housing $13,073 + meals $8,894 = $21,967 (our calculation)."}})

# Georgia Tech
ORG = "Georgia Institute of Technology"
GC = src("e6d0da398205", "Undergraduate Costs | Georgia Tech Scholarships & Financial Aid", ORG,
         ["2026-2027 Cost of Attendance First-Year Georgia Resident",
          "First-Year Out of Country Cost On Campus Cost Off Campus Cost Tuition $35,610 $35,610 Mandatory Student Fees $1,716 $1,716 Books, Course Materials, Supplies, and Equipment $800 $800 Housing Allowance $8,318 $12,084 Standard Food Service Plan $6,310 $6,310",
          "Estimated 2027-2028 Cost of Attendance",
          "First-Year Out of Country Cost On Campus Cost Off Campus Cost Tuition $34,572 $34,572"])
GB = src("0cf9dd035a48", "Bachelor of Science in Computer Science | Georgia Tech Catalog", ORG,
         ["In addition to the standard four-year plan, a five-year cooperative plan is offered",
          "Georgia Institute of Technology North Avenue Atlanta, GA", "College of Computing"])
one("us-gatech", ORG, ["Georgia Tech", "GT"], "public", "https://www.gatech.edu", ("us-atlanta-ga", "Atlanta"), GB,
    {"course": GB, "coa": GC},
    ("out-of-country", "Out-of-country students", "Georgia Tech's cost of attendance for out-of-country (international) students.", "coa"),
    "bs-computer-science",
    P("Computer Science", "Bachelor of Science", "College of Computing", "course", "Bachelor of Science in Computer Science, Georgia Tech; standard four-year plan (five-year co-op plan also offered)."),
    {"residency": "out-of-country", "currency": "USD", "tuition_annual": 35610, "mandatory_fees_annual": 1716, "academic_year": "2026-2027", "source": "coa",
     "note": "First-year out-of-country 2026-2027: tuition $35,610 and mandatory student fees $1,716. The page's estimate for 2027-2028 shows lower out-of-country tuition ($34,572); to check with Georgia Tech.",
     "living": {"monthly": [], "months": 12, "yearly": [8318, 6310], "source": "coa", "kind": "genuine_cost_of_living_estimate",
                "note": "First-year on campus 2026-2027: housing allowance $8,318 + standard food plan $6,310 = $14,628 (our calculation)."}})
print("wrote us batch3")
