# Follow-ups from the staging re-run — 2026-10-31

Pending file: `fact-checks/pending/2026-10-31-followups.ndjson` (18 mutations). All figures and wording below were
read on the official pages/PDFs on 2026-10-31 (headed Chrome or the PDF itself).

## 1. Waterloo Economics — US high school diploma (2 records)

Waterloo's Economics page: "Not studying in Ontario? Search our admission requirements for Honours Arts or Honours
Arts and Business." Calculus is "strongly recommended", not required.

Honours Arts (includes 28 majors), American (US) system
(https://uwaterloo.ca/future-students/admissions/admission-requirements/honours-arts/high-school/international-system/american-system):
"Grade 12 English, minimum final grade of 75%. Minimum Grade 12 average of low 80s."

- New `sourceRecord-ca-waterloo-src-us-arts`
- New `admissionsRequirement-ca-waterloo-admreq-ba-economics-us-hs`. "Low 80s" is Waterloo's wording; the row says it
  is read as 80% so the engine can compare it.

## 2. Taylor's — 6% Service Tax added for non-Malaysian students (3 patches)

Each 2027 fee schedule (CS, Business, Mechanical Engineering), Note 1: "Effective 1 July 2025, a 6% Service Tax will
be imposed on non-Malaysian citizens, applicable to all fees and charges, except Hospitalisation & Surgical
Insurance, International Security Deposit and EMGS application fees. Fees shown in the Fee Schedule are exclusive of
the 6% Service Tax."

Tuition stays as published; the tax is added to compulsory fees (these cost profiles are the international ones).

| Programme | Taxable (tuition + enrolment + intl charge + intl annual fee) | 6% SST | Compulsory fees before → after (per yr) |
|---|---|---|---|
| Computer Science (3 yrs) | RM141,076 | RM8,464.56 | RM5,621.33 → RM8,442.85 |
| Business (3 yrs) | RM149,500 | RM8,970.00 | RM5,621.33 → RM8,611.33 |
| Mechanical Engineering (4 yrs) | RM191,992 | RM11,519.52 | RM4,921.00 → RM7,800.88 |

Discrepancy noted in each record: the schedule's own "Total Fees With SST" column (CS RM156,498, Business RM165,428,
ME RM210,809) is the grand total × 1.06, i.e. it also taxes the items Note 1 exempts. Following Note 1 gives a figure
about RM100–130/yr lower.

## 3. International-only scholarships marked in the data (13 patches)

`eligible_citizenships` set to `["all", "not:<home country>"]` and `residency_restrictions` given a readable line
(the site shows that line instead of the code list). New convention, documented in the Studio schema: `"not:xx"`
excludes one citizenship.

| Records | Official wording |
|---|---|
| UAEU full waiver, 75% waiver (`not:ae`) | "International students (enrolled from inside or outside the UAE). Children of UAEU faculty members and staff." UAE nationals pay no tuition at UAEU. |
| Khalifa partial 50% / 75% (`not:ae`) | "The partial scholarship gives international students a 75% tuition discount…" |
| RIT Dubai Global Tigers (`not:ae`) | "New international students may be eligible…" |
| McMaster ×4 (`not:ca`) | "for incoming international fee-paying students" |
| UBC IMES (`not:ca`) | stored criteria: "as an international student on a Canadian study permit" |
| Waterloo ISES (`not:ca`) | "International fee-paying students admitted to full-time, first-year degree studies will receive $10,000". Source URL updated: the old link now redirects to a page that no longer lists it. |
| Alberta ×2 (`not:ca`) | Both listed on the "International Entrance Scholarships" page (Admission Scholarship criteria: "International fee-paying students") |

Toronto's Pearson record already said non-Canadian and is unchanged. Permanent-resident status isn't modelled, so
the lines say "not open to Canadian citizens" only.
