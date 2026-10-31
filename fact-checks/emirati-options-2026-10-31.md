# Emirati options — 2026-10-31

From the 15-student review (Aisha and Yusuf, Emirati, were shown international prices and few UAE options).
Data: `fact-checks/pending/2026-10-31-emirati.ndjson` (51 changes).

| Item | Finding (official source) | Change |
|---|---|---|
| UAEU — UAE nationals | Policy AE-10: "Tuition is charged for all instruction to graduate students"; fee rules are set for "International students enrolled in the Bachelors' programs". UAEU's tuition-discount scholarships apply only to international students and children of staff. Our existing UAEU fee note already said nationals are government-sponsored. | New "UAE nationals (government-funded)" tier, tuition 0, on all 4 UAEU programmes |
| Khalifa — UAE nationals | ku.ac.ae/undergraduate-scholarships: "Scholarship for UAE National and Children of Emirati Mothers — Full coverage of tuition fees. Free University accommodation… free weekly transportation… textbooks." Assessed in admission; KU says meeting minimum criteria doesn't guarantee an award. | New scholarship record (not marked "guaranteed", so it's shown as one to check, not subtracted automatically) |
| Zayed University (new) | zu.ac.ae tuition page: AED 2,500/credit hour for self-funding nationals and internationals; "UAE national undergraduate students enrolled under the government scholarship scheme are entitled to full tuition funding for a maximum duration of five academic years." Admission 2026-27: no minimum overall average for UAE MoE / American; 2 A-Levels at C+; IB 24; Business & Technological Innovation need 80% Grade 12 English and Maths (or TOEFL 72 / SAT Math 530). | Added with BSc Information Technology and BSc Finance; AED 75,000/yr self-funded (30 credits/yr), 0 for nationals |
| HCT (new) | hct.ac.ae: "free education for UAE national students and sons/daughters of UAE national mothers for one credential"; International Admissions 2026-27: Bachelor AED 37,104.45/semester (15 CH), AED 2,473.63/CH, 4 years. Ministry criteria (Fall 2025): Applied Bachelor 70% Advanced / 80% General stream; English 80%. | Added with Bachelor of Software Engineering and Bachelor of Finance; AED 74,208.90/yr expatriate, 0 for nationals |
| Study-abroad scholarships | MoFA Scholarship Program (mofa.gov.ae/en/scholarship) — fully funded, fields relevant to diplomacy. MoHESR external scholarships via the u.ae portal — competitive, approved universities/majors lists. | Shown to Emirati students for every university outside the UAE (lever + tag) |

Living costs for ZU/HCT use the unofficial Abu Dhabi estimate (labelled "Unofficial estimate"), as for Khalifa.
Not done: ZU per-programme credit totals (30 credits/yr assumed, as HCT's published full-time load).

## UAE minimum averages (fact-checks/pending/2026-10-31-uae-averages.ndjson, 37 patches)
| University | Official source | Requirement |
|---|---|---|
| UAEU | uaeu.ac.ae admissions — International Students and Children of UAEU Employees (tables by college) | Computing & AI and Engineering 90% average (+ English/Maths/science 90%); Business & Economics 85% (Maths 80%, English 90%). Nationals apply via the national portal. |
| AUS | aus.edu/admissions/bachelors-degrees/application-requirements | 85% average in each of the last three years (guideline; may be higher); STEM: B in Maths and Physics; IB Diploma 24 points, 3 HL |
| CUD | cud.ac.ae/prospective-students/undergraduate | Pass in all subjects (no overall average); English 80% or IELTS 5.0; Engineering: Maths/Physics/Bio-or-Chem 80% |
| RIT Dubai | rit.edu/dubai Admission Requirements Computing / Engineering PDFs | Computing 70% (Elite/Advanced) / 75% (General/Applied), American 70%; Engineering 75/80/85%, American 80% |
Engine: overall-average % now ignores subject percentages ("80% in English") and "no minimum overall average".
