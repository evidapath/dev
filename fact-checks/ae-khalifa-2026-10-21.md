# Khalifa University of Science and Technology — verification log (2026-10-21)

Batch-2 import #3 (UAE). Created as **Sanity DRAFTS**. Public STEM research university, Abu Dhabi. Sources: ku.ac.ae.

| Field | Value | Source |
|---|---|---|
| Name / type | Khalifa University of Science and Technology; **public**, STEM-focused | ku.ac.ae |
| Location | Abu Dhabi, UAE (reused existing published city) | ku.ac.ae |
| Tuition | **AED 2,500/credit ≈ AED 81,250/yr** (fee page); uniform across colleges & nationalities; seat deposit AED 5,000 | [fee guidelines](https://www.ku.ac.ae/fee-and-payment-guidelines) |
| English | Direct: IELTS 6.0 / TOEFL iBT 79 / EmSAT English 1400; conditional IELTS 5.5 / iBT 70 / EmSAT 1250 | ku.ac.ae admissions |
| Admission | Grade 12 (last 2 yrs), strong grades (UAE 80% Advanced/Elite, 90% General); CS requires Math; SAT Math ≥700 considered | ku.ac.ae |

## ⚠️ Source conflict (shown, not reconciled)
- Fee page: AED 2,500/credit ≈ **AED 81,250/yr**.
- Scholarship page: states a **"base tuition AED 100,000/yr"** (≈40-credit nominal) against which discounts are computed.
- Both from ku.ac.ae. `tuition_annual` uses the fee-page 81,250 basis; scholarship net figures use KU's 100,000 base. Flagged in the cost note rather than silently picking one.

## Programs (2 pillars — STEM-only, NO Business/Economics)
- **Computer Science** — BSc, College of Computing and Mathematical Sciences (AI & Cybersecurity concentrations). Math required.
- **Engineering** — BSc, College of Engineering (Aerospace, Biomedical, Chemical, Civil, Electrical, Industrial & Systems, Mechanical, Petroleum, Computer). Math + Physics.
- **Business / Economics** — ⚠️ OMITTED (verified absent): Khalifa is a science/technology university with no undergraduate business or economics programs. Not fabricated (same discipline as Delft/TUM).

## Scholarships (partial, competitive-threshold; maintain CGPA 3.0+)
- **College of Science — 75% tuition discount** (net ~AED 25,000/yr on KU's 100,000 base).
- **College of Engineering — 50% tuition discount** (net ~AED 50,000/yr).
- The search-summary "100% / CGPA 3.3 full scholarship" tier was **not confirmed** on the official partial-scholarships page → omitted, not asserted.

## Marked uncertain / not fabricated
- **Living costs** — dorms/transport charged separately; no cost-of-living estimate captured → `not_published`.
- Fee-page **academic year** not explicitly stated → noted in cost year field.
