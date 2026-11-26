"""California Institute of Technology: base records + Computer Science B.S. (written 2026-11-26). THE queue #50.

Sources, Caltech Catalog (catalog.caltech.edu/current):
  - Undergraduate Expenses: "Estimated Cost of Attendance 2026-27", on-campus "Tuition $68,574 Fees 1,2 2,655
    Housing 12,711 Food/Meals 9,285" (nine-month budget); address "California Institute of Technology 1200 East
    California Boulevard Pasadena";
  - Graduation Requirements, All Options: "The baccalaureate degree requires four years (12 terms) of academic
    enrollment", "Computer Science Option and Minor (CS)".
Not stored: grade thresholds (none published), test policy (testing page 404), international aid.
  python3 -I scripts/research/gen/us_caltech.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newuni import src, spec, prog

ORG = "California Institute of Technology"
EXP = src("1d13dc064c5c", "Undergraduate Expenses | Caltech Catalog", ORG,
          ["California Institute of Technology 1200 East California Boulevard Pasadena",
           "Estimated Cost of Attendance 2026-27 The charts below list the estimated nine-month, full-time cost of attendance budgets",
           "Category On-Campus Tuition $68,574 Fees 1,2 2,655 Housing 12,711 Food/Meals 9,285 Total Direct Costs $93,225"])
spec("us-caltech", ORG, ["Caltech"], "private", "https://www.caltech.edu", ("us", "United States", "USD"), ("us-pasadena", "Pasadena"),
     {"main": EXP}, [("international", "All undergraduates", "Caltech tuition is the same for all undergraduates.", "main")])
prog("us-caltech", "bs-computer-science",
     {"course": src("f9106107c912", "Graduation Requirements, All Options | Caltech Catalog", ORG,
                    ["The baccalaureate degree requires four years (12 terms) of academic enrollment", "Computer Science Option and Minor (CS)"]),
      "costs": EXP},
     {"name": "Computer Science", "degree_type": "B.S.", "field": "Computer Science", "faculty": "", "duration_years": 4, "duration_source": "course",
      "languages": [], "entry_year": "2026-27", "platform": "", "source": "course",
      "summary": "Computer Science option (B.S.), California Institute of Technology; four years (12 terms).", "application_requirements": []},
     [{"residency": "international", "currency": "USD", "tuition_annual": 68574, "academic_year": "2026-27", "source": "costs",
       "note": "On-campus tuition $68,574 for 2026-27 (nine-month budget); fees $2,655 are separate.",
       "living": {"monthly": [], "months": 12, "yearly": [12711, 9285], "source": "costs", "kind": "genuine_cost_of_living_estimate",
                  "note": "Caltech's 2026-27 on-campus budget: housing $12,711 + food $9,285 = $21,996 for nine months (our calculation)."}}],
     [])
print("wrote caltech")
