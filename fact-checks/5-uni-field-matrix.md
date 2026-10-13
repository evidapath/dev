# 5-University Field Verification Matrix

Per Suhail's Batch-2 requirement #8 ("official source URL, verification date and
confidence/status for each material data field"). Tracks, per university × per field
category, whether the DISPLAYED/stored value has been checked against a PRIMARY source
(not just the AI pipeline's self-assessed record_status). Drives Phase A of
`docs/batch2-and-verification-plan.md`.

Legend: ✅ verified vs primary source · 🟡 exists, unverified · 🔴 missing · ✏️ correction needed

## Category status (all 5 universities)

| Field category | NYUAD | Oxford | Toronto | TU Delft | TU Munich |
|---|---|---|---|---|---|
| Fees / tuition / cost (intl + domestic) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Application **deadlines** | ✅ | ✅ | ✅ | ✅ | ✅ (✏️ year) |
| Language of instruction | ✅ | ✅ | ✅ | ✅ | ✅ |
| Admissions requirements (per curriculum) | ✅ | ✅ | ✅(✏️) | ✅ | 🟡 |
| Tests (SAT/ACT/English/admissions) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Required documents | ✅ | ✅ | ✅ | 🔴 | ✅(✏️) |
| Scholarships (eligibility/award/conditions) | ✅ | ✅ | ✅ | ✏️🔴 | ✅ |
| Financial aid | ✅ | ✅(Home) | ✅(dom) | 🔴 none for BSc | ✅ |
| Programs beyond CS (Eng/Business/Econ) | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 |

## A2.1 — Application deadlines (verified 2026-10-13)

| Uni | Stored | Primary source says | Verdict |
|---|---|---|---|
| NYUAD | ED1 2026-11-01 / ED2 2027-01-01 / RD 2027-01-05; Common App | matches | ✅ (nyuad fact-check) |
| Oxford | 2026-10-15 18:00 BST; UCAS; 2027 entry | "6pm UK time on 15 October"; decision 12 Jan 2027 | ✅ EXACT |
| Toronto | 2027-01-15; OUAC (TAD); Fall 2027 | Jan 15 2027 OUAC deadline | ✅ |
| TU Delft | 2027-01-15; Studielink; numerus fixus | "until 15 January (23:59 CET)" | ✅ |
| TU Munich | 2026-07-15; WS **2026/27** | deadline July 15 (annual); but 2026/27 cycle has PASSED | ✅ date, ✏️ **cycle stale → bump to WS 2027/28 (2027-07-15) for consistency with the other 4 (all 2027 entry)** |

### Corrections / enrichments to apply (batched for one write session)
1. **TU Munich** decisionPlan: update academic_year/deadline from WS 2026/27 (2026-07-15)
   → WS 2027/28 (2027-07-15). (Date rule July 15 confirmed; year was stale.)
2. **Oxford** decisionPlan: add `decision_release_date = 2027-01-12` (published, currently null).
3. **Toronto**: consider adding the CS Supplementary Application deadline (Feb 1 2027)
   and recommended early date (Nov 7 2026) as separate requirement notes.

Sources: ox.ac.uk/admissions/undergraduate/applying/admissions-timeline + /courses/.../computer-science;
future.utoronto.ca/program/computer-science + /deadlines;
tudelft.nl/.../from-application-to-enrollment/application-procedure;
tum.de/.../application/dates-and-deadlines + /detail/informatics-bachelor-of-science-bsc.

## A2.2 — Admissions requirements + language (verified 2026-10-13)

Verified the A-Level curriculum record + language per uni (the shared international route):
| Uni | Stored A-Level req | Primary source | Verdict |
|---|---|---|---|
| Oxford | A*AA incl Maths; Further Maths rec; TMUA; IELTS 7.5/7.0 | ox.ac.uk CS admissions | ✅ EXACT |
| NYUAD | holistic, no subject reqs; test-optional; English benchmarks | nyuad entry-requirements | ✅ (prior) |
| TU Delft | Maths required; **Physics NOT required**; EN track | tudelft.nl admission-requirements | ✅ EXACT (incl. correctly NOT requiring Physics; bonus: 6 GCE A-C / 3 A-levels A-C, IB Maths AA HL, US Calculus) |
| TU Munich | 3 A-Levels grade C, nat-sci subjects (Maths/Bio/Chem/Phys/CS); German DSH-2/C1 | daad.de GCE + tum.de language | 🟡 sourced to DAAD (authoritative for German entry) — accept |
| Toronto | **A-Level record EMPTY** (no subjects/threshold); OSSD record OK (Calculus MCV4U, English ENG4U); English C | future.utoronto.ca | ✏️ **A-Level curriculum record needs Maths/Calculus-equivalent requirement added** (OSSD record is fine) |

Language of instruction confirmed all 5: Oxford/NYUAD/Toronto = English; TU Delft = Dutch+English (English track fully in English); TU Munich = German (proficiency required).

### A2.2 correction/enrichment to apply
4. **Toronto** A-Level admissionsRequirement: add required subject (Mathematics /
   Calculus equivalent) — currently empty; a CS applicant needs it. OSSD record already correct.
5. **TU Delft** enrich: IB = Maths AA HL; US = Calculus A/B or B/C (published, useful for Discover/Analyze).

## A2.3 — Tests + documents (verified 2026-10-13)

| Uni | Tests | Documents | Verdict |
|---|---|---|---|
| Oxford | TMUA required | UCAS, TMUA, Interview (≥2 colleges) | ✅ |
| NYUAD | test-optional (SAT/ACT recommended) | Common App + school report/STARS/rec/profile/essay/candidate weekend | ✅ |
| Toronto | none (correct) | OUAC (TAD) + CS Supplemental Application | ✅ |
| TU Munich | none (correct) | TUMonline + uni-assist VPD + HZB + CV | ✅ ✏️ **VPD mis-typed `financial_document` → should be credential/other** |
| TU Delft | none | **EMPTY** — no application docs/platform on the program record | 🔴 **gap: add Studielink registration + numerus-fixus selection/matching steps** |

### A2.3 corrections to apply
6. **TU Munich** VPD requirement_type: `financial_document` → correct type (credential pre-assessment / other).
7. **TU Delft** application_requirements: add Studielink registration + CSE Matching & Selection (numerus fixus) steps (currently empty).

## A2.4 — Scholarships + aid (verified 2026-10-13)

| Scholarship | Covers | Verdict |
|---|---|---|
| Sheikh MBZ (NYUAD) | NYUAD | ✅ 100% tuition+fees, guaranteed for eligible Emiratis; HUMAN_REVIEW eligibility conflict (mother vs mother-or-father) already surfaced |
| Oxford Bursary | Oxford | ✅ income-banded (£4,480→£1,120), **GUARANTEED** for Home/UK students — NOT international |
| Reach Oxford | Oxford | ✅ fees+living+airfare, competitive, for low-income-country international students |
| Lester B. Pearson | Toronto | ✅ international full-ride, highly competitive (✏️ award_amount null — should state full-ride) |
| National Scholarship | Toronto | ✅ **domestic** (Canadian/PR), competitive |
| Deutschlandstipendium | TUM | ✅ €300/mo, competitive, open to BSc international |
| Holland/NL Scholarship | TU Delft | 🟡 €5,000 one-time non-EEA; **CONFLICT** (applicability to Delft BSc) already surfaced |
| **Justus & Louise van Effen** | TU Delft | 🔴 **MASTER'S-ONLY — wrongly matched to the BSc program.** Official: "no scholarships/aid for Bachelor applicants… not eligible if you are a TU Delft bachelor's student." MUST exclude from BSc matching. |

**Key findings:**
- **van Effen is MSc-only** and must not show for the BSc applicant (critical eligibility error).
- **TU Delft has NO institutional bachelor scholarships** — honest "no guaranteed funding" signal for a student (only the uncertain NL Scholarship).
- Guaranteed-vs-competitive (Suhail's standard): GUARANTEED = Oxford Bursary (income), Sheikh MBZ (eligible Emiratis); COMPETITIVE = Pearson, Reach, National, Deutschlandstipendium. Worth surfacing this distinction in the app.

### A2.4 corrections to apply
8. **van Effen**: exclude from BSc TU Delft matching (mark postgraduate-only; app should
   filter scholarships by the program's degree level). CRITICAL.
9. **Pearson / National**: populate award_amount (full-ride description) — currently null.
10. Consider a guaranteed-vs-competitive flag surfaced in the Scholarships UI.

---
## ✅ Phase A2 (verify EXISTING data) COMPLETE for the 5 — all 4 categories done.
Zero hallucinated facts found. Issues are staleness/completeness/eligibility-match:
TUM deadline stale, Toronto A-Level subjects empty, TU Delft app-docs empty + TUM VPD
mistyped, **van Effen MSc-only wrongly matched to BSc**. 10 corrections batched.
Remaining Phase A: A3 (add Engineering/Business/Economics programs) + A4 (surface in app)
+ apply the 10 corrections (one Sanity write session).

## Next categories (archived)
- A2.4 Scholarships (eligibility/award/deadline/conditions) + aid — verify all 5.
- A3 Programs: add Engineering/Business/Economics per uni (same bar).
