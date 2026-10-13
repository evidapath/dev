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
| Tests (SAT/ACT/English/admissions) | ✅ | 🟡 | 🟡 | 🟡 | 🟡 |
| Required documents | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| Scholarships (eligibility/award/conditions) | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| Financial aid | 🟡 | 🔴 | 🔴 | 🔴 | 🔴 |
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

## Next categories (A2.3+)
- A2.3 Tests + required documents — verify all 5.
- A2.4 Scholarships (eligibility/award/deadline/conditions) + aid — verify all 5.
- A3 Programs: add Engineering/Business/Economics per uni (same bar).
