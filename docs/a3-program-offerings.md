# A3 — Verified program offerings for the 5 (2026-10-13)

Before creating any new programs, mapped what each university ACTUALLY offers at
bachelor's level (verified vs official sources), for EvidaPath's international audience
(English-taught where language matters). Suhail wants CS + Engineering + Business +
Economics — but **not all 5 offer all 4**, and we must never invent a program (#7).

CS/Informatics already exists for all 5. New programs to add:

| Uni | Engineering | Business | Economics | # new |
|---|---|---|---|---|
| **NYU Abu Dhabi** | General Engineering (also Computer/Civil/Electrical/Bioengineering) | Business, Organizations & Society | Economics (Quant / Finance & Markets / Applied Policy) | 3 |
| **Oxford** | Engineering Science (MEng 4yr; **ESAT** test; A*A*A) | — (combined in E&M) | Economics & Management (BA 3yr; **TARA** test; A*AA) | 2 |
| **Toronto** | Faculty of Applied Science & Eng (prereqs Calculus/Chem/Physics) | Rotman Commerce (BCom; Finance&Econ/Accounting/Management; supp app Feb 1) | Economics (BA, Major/Specialist) | 3 |
| **TU Delft** | Aerospace Engineering (English) | ❌ none (pure technical university) | ❌ none | 1 |
| **TU Munich** | Aerospace (English) | Management & Technology (Munich, English option) | — (covered by M&T) | 2 |

**Total ≈ 11 new programs** (not 15 — Delft/TUM don't offer Business/Economics bachelor's).

## Key per-program facts already surfaced (to verify fully in Step 2)
- Oxford admissions tests differ by program: CS=TMUA, **Engineering Science=ESAT**, **E&M=TARA**. Must not reuse CS's TMUA.
- TU Delft English bachelor's = only Aerospace Eng, Applied Earth Sciences, CSE, Nanobiology. No business/econ.
- TUM English: Aerospace B.Sc. (100% EN), Management & Technology (EN option). (Our existing Informatics is German-taught.)
- Toronto Rotman Commerce is competitive (73%+ prereq avg) + Supplementary Application.
- NYUAD: Engineering + Economics + Business all exist (26 majors, liberal-arts core).

## Step 2 — how to create them (proposal)
Each new program = a Sanity `program` doc + per-curriculum `admissionsRequirement` docs +
residency-tiered `costProfile` docs + `decisionPlan`(s) + language + source_refs, every
field verified against primary sources (same bar as the 5 CS programs). This is a large
write effort (Subhan runs writes with a token). Recommend **depth-first**: build ONE
university's new programs fully first (Oxford or NYUAD — rich English data) as the
template, verify end-to-end in the app, then replicate to the others. Do NOT auto-publish
(Suhail's rule); keep draft/verified/published separate.

NOTE: tuition often differs by program/faculty (e.g. Toronto Engineering vs Arts&Sci CS
have different international fees; Oxford fee band differs by subject). Must fetch
program-specific costs, not reuse CS's (Suhail: "program-specific, not university-wide").

## Step 2 progress — Oxford template (research started 2026-10-13)

**Validated the program-specific-fee rule — fees differ a LOT by program at the same uni:**
- Oxford **Engineering Science**: overseas **£66,580** (2027, confirmed — top band, same as CS);
  Home £10,050; A*A*A (A*s in Maths/Further Maths/Physics); **ESAT** test (NOT CS's TMUA);
  4-yr MEng; English; UCAS deadline 15 Oct.
- Oxford **Economics & Management**: overseas **£43,600** (2026/27; 2027 not yet published —
  record honestly as 2026/27 pending 2027); Home ~£10,050; A*AA (Maths required); **TARA**
  test; 3-yr BA; English; UCAS deadline 15 Oct.
- ⇒ Reusing CS's £66,580 for E&M would overstate by ~£23k/yr. Per-program research is mandatory.

**Remaining per-program data still to fetch before creating Oxford's records:** admissions
requirements per curriculum (IB/US/other) for each, English-language requirement, decision
dates. Same depth as the original 5 CS programs.

### Oxford template — verified data ready for record creation (2026-10-13)

**Engineering Science** (MEng, 4 years, English; specialise Y3 into Biomedical/Chemical/
Civil/Electrical/Information/Mechanical):
- A-Level: A*A*A (A*s in Maths & Further Maths/Physics; Maths+Physics required) · **ESAT** test
- IB: 40 incl core (776 at HL, 7s in HL Maths + Physics) · ESAT
- Overseas tuition **£66,580** (2027, confirmed) · Home £10,050 · no separate college fee (combined)
- English: IELTS 7.5/7.0, TOEFL 110, C1 191 · UCAS deadline 15 Oct, decision ~Jan
- Sources: eng.ox.ac.uk/study/undergraduate/applications/entry-requirements; ox.ac.uk course fees/summary table

**Economics & Management** (BA, 3 years, English):
- A-Level: A*AA (Maths at A/A*) · **TARA** test
- IB: 39 incl core (766 at HL) · TARA
- Overseas tuition **£43,600** (2026/27; 2027 not yet published — record as 2026/27, flag pending) · Home ~£10,050
- English: IELTS 7.5/7.0 · UCAS deadline 15 Oct, decision ~Jan
- Sources: economics.ox.ac.uk/undergraduate-admissions-criteria; sbs.ox.ac.uk E&M; ox.ac.uk course fees

US-HS/AP admissions thresholds for these two still to fetch before finalizing (A-Level+IB done).

## Creation mechanism (decide with Suhail before writing)
The original data came from Suhail's pipeline (normalized records → `normalized_to_sanity_ndjson_v1_2.py`),
giving schema-correct interlinked docs. Adding programs via ad-hoc API mutations risks schema
drift (programs/admissions/costs need many required fields + references). **Recommend: add new
programs through Suhail's pipeline or the Studio editor (schema-enforced), not hand-written NDJSON.**
Confirm his preferred path before creating records.

## A3 template BUILT — Oxford E&M (2026-10-13)

`sanity-studio/scripts/create_program_oxford_em.py` — generates 7 interlinked docs for
Oxford Economics & Management (2 sourceRecords + program + 2 admissionsReqs + 2
costProfiles), cloning the verified CS program's schema shape and reusing the shared
applicant-category + interview-stage records (validated to exist before write). Dry-run
clean. **Subhan runs with a write token:**
  `SANITY_TOKEN=<write> python3 scripts/create_program_oxford_em.py --execute`
Idempotent (createOrReplace). This is the proven TEMPLATE — replicate for the other ~10.

### App multi-program readiness (done + still-needed)
- DONE: adapter now features the Computer Science program as the headline per uni (stable)
  and the programs GROQ query orders by name — so adding E&M will NOT scramble Oxford's
  displayed tuition (was a real regression risk: CS GBP66,580 vs E&M GBP43,600).
- STILL NEEDED before E&M data is fully usable to a student: a **program selector** on
  Universities/Analyze so a student picks the program and sees THAT program's specific
  cost/admissions (Suhail's rule: program-specific, not university-wide). Until then the
  card shows CS as the headline and lists other program names only.

### Recommended sequence
1. (optional now) run the E&M generator → data in Sanity, CS still headline, E&M listed.
2. Build the program selector (app) → per-program cost/admissions display.
3. Replicate the generator for the other ~10 programs (research done for Oxford;
   NYUAD/Toronto/Delft/TUM still need per-program primary-source research).

## Modeling note — uniform vs tiered (verified 2026-10-14)

Programs differ in whether cost/admission are program-specific. Model each honestly:

- **NYU Abu Dhabi — UNIFORM.** The data documents it: NYUAD publishes a single
  citizenship-undifferentiated Cost of Attendance ($68,576 total), unified holistic
  admission (apply to NYUAD, declare major later). So its Engineering/Economics/Business
  majors share the SAME cost + SAME admissions as CS. Adding them = program docs that
  reference the uniform cost + holistic admissions (NOT invented per-major differences —
  that would be a subtle hallucination of program-specific admission that doesn't exist).
  Lower demonstrative value (nothing differs); do these LAST or lightly.
- **Toronto — TIERED, genuinely program-specific (HIGH value).** Verified: Faculty of
  Applied Science & Engineering international tuition **CAD 72,860** (2026-27) + 2,266.83
  incidental + 948 UHIP — DIFFERENT from Arts & Science CS's CAD 66,110. Rotman Commerce
  (BCom) is a separate competitive program (73%+ prereq avg, Supplementary App Feb 1).
  This is where the program selector earns its keep.
- **Oxford — TIERED (done):** CS £66,580 vs E&M £43,600 vs Eng £66,580.
- **TU Delft / TU Munich** — Aerospace is a distinct English program; verify its own
  fees (likely same statutory/institutional tiers as CSE but confirm, don't assume).

### Toronto Engineering — FULLY VERIFIED + spec ready (2026-10-14)
All values primary-source verified (non-leading), in `create_programs.py` as `toronto-eng`:
- Intl tuition **CAD 72,860** + 2,266.83 incidental + 948 UHIP (= 3,214.83 fees) ✓
- Domestic Ontario **CAD 14,460** + 2,266.83 incidental ✓ (2.4x Arts&Sci CS's 6,100 — program-specific!)
- Prereqs: Calculus/Physics/Chemistry (Ontario MHF4U/MCV4U/SPH4U/SCH4U/ENG4U), min 70% each ✓
- IELTS 6.5 overall, no band <6.0 ✓; living ~CAD 2,000/mo (U of T estimate) ✓
- No standardized test (OSP supplementary profile instead); no reused admission stage (Eng ≠ CS admission)
- Other-province domestic tier OMITTED (not verified — not invented; #7). Run `--only toronto-eng --execute`.
Caught + fixed a self-hallucination risk: initial spec had an unverified living range + IELTS score;
both re-verified vs utoronto.ca before finalizing (the zero-hallucination discipline working).

### Toronto Rotman Commerce (Business) — VERIFIED + spec ready (2026-10-14)
`toronto-rotman` in create_programs.py. Direct-entry BCom. All verified non-leading:
intl first-year CAD 66,110 + 2,100.29 incidental + 948 UHIP; prereqs English (ENG4U) +
Calculus & Vectors (MCV4U, weighted); mid-high 80s avg; Supplemental Application (video+
written); IELTS 6.5/6.0. ONLY the intl first-year fee included — upper-year "deregulated"
fee NOT published/verified → flagged, not invented (#7). Run `--only toronto-rotman --execute`.
First BUSINESS program in the dataset.

### 🔴 CRITICAL modeling rule — direct-entry vs post-admission (don't hallucinate admission paths)
A program card implies "you can apply to this." Only model DIRECT-ENTRY programs that way:
- **Direct-entry (OK to model):** Oxford's courses, Toronto CS/Engineering/Rotman Commerce.
- **POST-ADMISSION programs of study (do NOT model as direct-entry):**
  - **Toronto Economics** — NOT direct from high school. You enter Arts & Science, take
    ECO101/102 + first-year math, THEN apply to the Economics program on grades. Creating a
    direct-entry Economics card would hallucinate an admission path that doesn't exist.
  - **NYUAD majors (Econ/Business/Eng)** — unified holistic admission to NYUAD; major declared
    later. Same issue + uniform cost.
  Honest representation for these: a "majors available" list (not a direct-entry program with
  its own admission), or an explicit "entered after first-year/after admission" note. This is a
  small product/UX decision — flag to decide, don't silently create misleading records.

### Aerospace fees VERIFIED (2026-10-14) — specs partially ready
- **TU Delft Aerospace** (BSc, English, direct-entry, numerus fixus): non-EU institutional
  **€19,906** (= CSE; Dutch fee II is program-wide), EU statutory **€2,694** ✓. Reuses Delft
  categories (curriculum alevel/vwo/ib/us-hs-ap; residency eu-efta/non-eu/surinamese; stage
  matching-selection). STILL TO VERIFY before build: Aerospace-specific prereqs (likely Maths
  AND Physics — unlike CSE which is Maths-only; must confirm, don't assume), deadline (numerus
  fixus 15 Jan), living figure.
- **TU Munich Aerospace** (BSc, English, School of Engineering & Design): non-EU **€3,000/sem
  = €6,000/yr** (2026-27, = Informatics) ✓ + €97/sem (€194/yr) student-union fee.
  ⚠️ **VERIFIED fee-increase complication:** TUM raises non-EU bachelor tuition for **WS 2027/28
  new entrants to €3,400/sem (€6,800/yr)** for engineering-tier (grandfathered for current
  students). So a 2027-entry Aerospace/Informatics student pays €6,800/yr, not €6,000. This
  also means the EXISTING Informatics costProfile (€6,000) is correct for 2026-27 entry but
  STALE for 2027-28 entry. DECISION NEEDED: standardize TUM on 2026-27 (€6,000, current) or
  2027-28 (€6,800, announced) entry — and apply consistently to BOTH Informatics and Aerospace.
  Do not mix years silently. Living: existing Informatics uses €15,600/yr + Sperrkonto €11,904
  (German visa proof-of-funds); reuse with source, don't invent a new range.

### TU Munich Management & Technology (Business) — FULLY VERIFIED + spec ready (2026-10-20)
- **M&T B.Sc.**, Campus Munich, **TUM School of Management**, 6 semesters / 180 ECTS; ~70%
  management + a ~30% technology track (Chemistry, Mech Eng, Informatics, EE&IT, Computer Eng,
  or Medicine). **Bilingual English/German** (Computer Eng track 100% English) — NOT English-only
  like Aerospace; language field is `["en","de"]`.
- ⚠️ **Fee tier caught (did NOT assume = Aerospace):** TUM bachelor non-EU tuition is tiered
  **€2,000 OR €3,000/sem**. M&T is the **LOWER €2,000/sem (= €4,000/yr)** tier (verified on the
  official TUM School of Management program page), NOT Aerospace's €3,000/sem engineering tier.
  EU/EEA **€0**. + €97/sem (€194/yr) Munich student-union fee. WS 2027/28 increase: €2,300/sem for
  new non-EU bachelor entrants (noted; current students grandfathered).
- Admission = **two-part aptitude assessment** (final grade/GPA + half-year grades in German or
  English, Mathematics, and an advanced natural science **incl. Informatics**) — NOT Physics-specific
  like Aerospace. Reuses TUM cats a-level/ib/us-hs/abitur + residency eu-eea/non-eu + stage
  aptitude-assessment. TUMonline + uni-assist VPD; winter application 15.05–15.07.
- Living: **omitted** (no official program estimate; not fabricated — same discipline as Aerospace).
- Spec `tum-mgt` in create_programs.py; dry-run clean (9 docs). **Completes Business coverage.**

### Decisions made by Subhan's delegation (2026-10-20) — "everything is up to me"
- **TUM fee-year:** standardize on **2026-27 current/verified rates** (Aerospace/Informatics €6,000/yr,
  M&T €4,000/yr), announced WS2027/28 increases disclosed in cost notes. Verified all TUM costProfiles
  already consistent — no rework. (Hygiene follow-up: Informatics + Toronto CS each have DUPLICATE
  costProfiles — 4/6 rows instead of 2/3; identical values so display unaffected; dedupe later.)
- **Post-admission display:** model admission at the REAL entry point (Faculty/holistic), state the
  post-admission path in degree_type_local, document the major-declaration step in application_requirements,
  use the Faculty's cost; never invent a program-specific test/deadline/direct application.

### Toronto Economics (Economics) — FULLY VERIFIED + CREATED (2026-10-20)
- **BA Economics, Faculty of Arts & Science (St. George).** POST-ADMISSION: apply to A&S **Social Sciences**
  stream (OUAC code **TAX**), prereqs **ENG4U + MCV4U**; Economics Major/Specialist/Minor is a POSt enrolled
  after year 1 via ECO101H1+ECO102H1 (min **63% Major / 70% Specialist**) or ECO105Y1 (80%) + MAT.
- Cost (verified via **Tuition Explorer**, which lists "Social Sciences" explicitly in the year-1 stream):
  international **CAD 66,110** + 2,100.29 incidental + 948 UHIP; domestic Ontario **CAD 6,100** (Table B1).
  Unlike CS, Economics has **no upper-year deregulated jump**. Reuses A&S cats; spec `toronto-econ`.
- txn kcH2R0mkNwiyOfxLSPURo8.

### NYUAD majors (Engineering / Economics / Business) — FULLY VERIFIED + CREATED (2026-10-20)
- Modeled post-admission: NYUAD admission is **university-wide, holistic, test-optional** (SAT/ACT
  *recommended* through 2027-28, no minimum), single Common App decision; **major declared after entry**.
  All majors share the identical admission + the single university-wide cost (residency-uniform).
- Degrees verified vs NYUAD primary sources: **General Engineering = BS**, **Economics = BA**,
  **Business, Organizations and Society = BA**. Cost (NYU Bulletins COA 2026-27): tuition **$68,576** +
  direct non-tuition $15,838 (health/books/food/housing) = $84,414 direct; ~$90,328 total COA — same for all.
- Reuses the already-verified NYUAD CS record's categories (a-level/ib/international-other/us-hs),
  residency-uniform, and stage-university-entry. Generator extended with `std_tests` (so SAT/ACT show as
  *recommended*, not required) + per-spec `checked` date + `uni_name` source attribution.
- Specs `nyuad-eng` / `nyuad-econ` / `nyuad-bos`; txn BcdgJJSSVUTtE5oktKga9m.

### ✅ A3 coverage COMPLETE — all 5 universities now cover CS + Engineering + Business + Economics
(where the university offers them; Delft/TUM are technical unis with no Business/Economics bachelor's).
Program count now ~15 across the 5. Next phase per Suhail: mass-import the next batch of schools
using this same verified pipeline (generator + primary-source verification + dry-run + execute).

### Known data-hygiene follow-ups (non-blocking)
- Duplicate costProfiles: TUM Informatics (4 rows vs 2) and Toronto CS (6 vs 3); identical values so
  display is unaffected (selectCost picks the same figure). Dedupe when convenient.
- NYUAD CS exists as both a draft and a published doc; the new NYUAD majors are published-only. Frontend
  uses perspective=published, so all render; tidy the stray CS draft when convenient.

## Honest scope note
Step 2 (create ~11 programs, each = program + per-curriculum admissions + residency-tiered
costs + deadlines + language + sources, all verified) is a large multi-session build,
comparable in effort to the original 5-university research. Best resourced deliberately,
depth-first one university at a time. Not a single-turn task.
