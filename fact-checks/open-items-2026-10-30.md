# Open items resolved — 2026-10-30

**Authority:** Subhan (full authority to decide, 2026-10-30) — replaces the earlier "needs Suhail sign-off" holds.
**Method:** official pages read in a real (headed) Chrome via playwright-cli; quotes copied from the page.
**Data changes:** `fact-checks/pending/2026-10-30-open-items.ndjson` (81 mutations).
Backup first: `~/Desktop/evidapath-sanity-backups/staging-backup-2026-10-30-before-open-items.ndjson`.
Apply: `scripts/apply-sanity-mutations.sh fact-checks/pending/2026-10-30-open-items.ndjson`

## 1. NYUAD Sheikh Mohamed bin Zayed Scholarship — APPROVED (HUMAN_REVIEW → VERIFIED)
- Scholarships page: "offered to all admitted UAE nationals and children of an Emirati mother or father."
- UAE applicants page: "All admitted Emirati students and children of Emirati mothers are awarded…"
- Same group: under Federal Law No. 17 of 1972 (Nationality and Passports), Art. 2, a person born to an Emirati
  father is a national by law. The Ministry of Justice site (elaws.moj.gov.ae) refused connections today; the
  article was confirmed from the law's published English translations (UNHCR Refworld / ecoi.net / GCC
  legal network copies). Card now quotes the explicit wording and explains the equivalence.

## 2. Nottingham Malaysia High Achiever's Scholarship — CONFIRMED (UNKNOWN → VERIFIED)
Official page (Fees-and-Scholarships/Scholarships/Foundation-undergraduate-scholarships.aspx) + Appendix B PDF:
automatic; 25% / 20% / 15% off **first-year** tuition only; A-level AAA/AAB/ABB, IB 36/34/32, AP 5,5,5/5,5,4/5,4,4;
Computer Science must include Maths. Our earlier figures were right; IB/AP thresholds added.

## 3. UAE living costs
- **University of Birmingham Dubai publishes an official estimate: AED 6,860/month** (rent 4,600; groceries 1,000;
  recreation 600; mobile 160; taxi 500; excl. visa). We showed AED 4,600/month — that was the rent line only, so
  Dubai living costs were **~33% too low**. Now AED 82,320/yr for Birmingham Dubai (labelled as its published
  estimate) and for Canadian University Dubai, Heriot-Watt Dubai and RIT Dubai (labelled "Dubai estimate
  published by University of Birmingham Dubai" — none of them publishes its own).
- Sharjah (AUS, University of Sharjah), Abu Dhabi (Khalifa) and Al Ain (UAEU): no official living-cost estimate
  found; they stay labelled "Unofficial estimate". Only housing fees are published (e.g. RIT single AED 38,000).

## 4. The 36 bot-blocked links — all opened in a real browser
- 25 fine (Oxford ×10, UCL ×4, NYU ×5, UPenn, Princeton areas, study.eu, Monash home ×2, Melbourne home).
- **11 dead or moved** → replaced, and every fact behind them re-checked:

| Fact | Result |
|---|---|
| Princeton aid (need-blind, 100% need, no loans, same for internationals, avg grant $83,000) | ✅ admission.princeton.edu/cost-aid |
| UBC 2026/27 per-credit (Sci 1,769.40; APSC 1,789.18; Com 2,222.61; Arts 1,717.68) | ✅ vancouver.calendar.ubc.ca/fees/tuition-fees/undergraduate |
| RWTH semester fee €358.34 | ✅ asta.rwth-aachen.de/en/about-us/finance (old RWTH link redirected to an unrelated MSc page) |
| Monash 2027 fees CS 58,940 / Com 59,140 / Eng 63,040 | ✅ (course pages; source note said 55,500 — data was already right) |
| Monash Leadership Scholarship | ✏️ **No application or 500-word statement** (we said there was); keep with WAM 70 |
| Monash entry | ✏️ Official 2027 scores added: CS A-level 9 / IB 28; Com 11 / 31; Eng 10 / 30 (we said "not published") |
| Melbourne fees BSc 55,556 / BCom 56,451 | ✅ lowest figure of published ranges (to 65,344 / 62,464) |
| Melbourne entry | ✏️ Official 2027 guides added: BSc A-level BBB / IB 31; BCom ABB / IB 34 (we said "estimate ABB") |
| Melbourne English | ✏️ TOEFL 81, PTE 64 (we said 79 / 58); IELTS 6.5/6.0 ✅ |
| Melbourne scholarships | ✏️ **New: Melbourne International Excellence Scholarship** — 20% for the whole degree, ≥140, from 2027, **open to UAE students**. (The other one, MIUS, is still not open to UAE.) |
| Monash Malaysia fees CS 57,600 / B&C 54,240 / ME 68,160 | ✅ |
| Monash Malaysia entry | ✏️ Scores added (CS 9 / IB 28; B&C 7 / 25; ME 10 / 30); ME needs Maths + one of Chem/Phys/**Bio** (we said Physics) |
| Monash Malaysia High Achiever Award RM10,000/yr | ✅; ✏️ "AAA / IB 38" is **not** published (Monash decides); renewal rules were the continuing-student ones — fixed |

## 5. "General International Secondary Qualification" (134 rows)
- Site: every such row written in A-level terms now carries "Shown in A-level terms. The university converts
  other qualifications using its own equivalence tables — check its international entry requirements for your
  country." (code, `universities.tsx`).
- Data: Monash, Melbourne, Monash Malaysia rows now point to those universities' per-country score tables.
- Germany (TU Berlin, RWTH, KIT, LMU, Heidelberg): rows rewritten — Germany decides per certificate whether it
  gives direct entry; check the DAAD admission database (official, based on KMK/anabin); otherwise Studienkolleg +
  Feststellungsprüfung first. Language requirement kept.
- Not done: per-country equivalence for the other ~30 universities (UK, Canada, NL, US are holistic or publish
  long country lists) — the site label covers them honestly.
