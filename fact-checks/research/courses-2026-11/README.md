# Course expansion (started 2026-11-11)

Adding Medicine, more Engineering branches, Psychology, Law, Biology/Life
Sciences and Architecture to the 53 universities, from each university's own
pages. Nothing goes to Sanity until it's built into
`fact-checks/pending/*.ndjson` and applied by hand.

What's left to do, by university: `REMAINING.md`.

## How a programme gets in

1. Read the official page with `scripts/research/fetch.sh <url>` (or
   `scripts/research/bfetch.sh` when the page only renders in a browser), which saves its
   text to `.research-cache/pages/` (local, git-ignored). Pages behind a bot check (Cloudflare "security
   verification") are not worked around; they're listed below as blocked.
2. Write one JSON file per programme, in this subject's folder (`medicine/`,
   `engineering/`, ...): values plus verbatim quotes.
3. `python3 -I scripts/programmes/build.py <subject folder> .research-cache/pages <out.ndjson>`
   stops unless every quote is on its saved page, every number we store is in
   a quote of the source it cites, every deadline's day, month and year are
   quoted, and the faculty/school named is on the programme's page. Fees that
   change by year are averaged by the script from quoted figures
   (`tuition_formula`), never by hand.
4. Dry-run against Sanity (`?dryRun=true`), then write to `fact-checks/pending/`.

US majors: students are admitted to a college (or the whole university) and the
entry requirements and fees are the college's, so a new major reuses those records
from an existing programme in the same college (`"college"` in the research file),
with a quote from the university saying so. The builder refuses if a copied
requirement names the other programme or lists required subjects.

Living costs, university-wide compulsory fees (e.g. Nottingham Malaysia's visa fee)
and (where the page says so) English levels are reused from the same university's
existing verified records, by id.

## Status

| Subject | Done | Blocked / not offered |
|---|---|---|
| Medicine | Imperial, Cambridge, Birmingham, Manchester, Nottingham, UNSW, Taylor's, Universiti Malaya → `pending/2026-11-11-medicine.ndjson` | Cloudflare bot check: UCL, Oxford, Monash (AU and Malaysia), Melbourne. Held: UAE University MD (UAE nationals and children of Emirati mothers only) and Sharjah, until programmes can be limited by nationality. Not yet: Sydney (page loads by script), Germany and the Netherlands (taught in German/Dutch) |
| Engineering branches | Civil, Electrical and Electronic, Chemical at Imperial, Manchester, Nottingham; Civil and Chemical at Birmingham; Civil, Chemical, Mechanical at Universiti Malaya; Civil, Electrical and Electronic, Chemical at Nottingham Malaysia; Electrical and Electronic, Chemical at Taylor's → `pending/2026-11-12-engineering.ndjson` | Birmingham Electrical: its own subject list links to a missing page and no course page could be found. Not yet: Waterloo, Toronto, McGill (each branch is its own admission; fees come from per-term schedules), UAE universities. Not needed: US universities, UBC, McMaster, Alberta, Cambridge, Warwick, Oxford, UNSW, Monash AU (one Engineering admission; the existing record covers every branch) |
| Psychology | Manchester, Nottingham, Warwick, Cambridge (Psychological and Behavioural Sciences), Nottingham Malaysia, Taylor's, UNSW (Psychological Science) → `pending/2026-11-12-psychology.ndjson` | Birmingham: its Psychology page has no 2027 entry requirements or fees yet. Not yet: US and Canadian universities (Psychology is a major chosen after admission to the college; needs a way to reuse the college's admission and fee records) |
| Law | Manchester (LLB), Nottingham (LLB), Warwick (LLB), Cambridge (BA, LNAT), Taylor's (LLB, Malaysian and English law) → `pending/2026-11-12-law.ndjson` | Birmingham: page has no 2027 details. Universiti Malaya: its Bachelor of Laws is "Not Offered" to international applicants. UNSW: law is a double degree for school leavers; not added |
| Biology / Life Sciences | Imperial (Biological Sciences), Manchester, Nottingham, Warwick (Biological Sciences), Cambridge (Natural Sciences, Biological stream), Taylor's and Universiti Malaya (Biotechnology) → `pending/2026-11-12-biology.ndjson` | Not yet: Birmingham, Nottingham Malaysia, UNSW (general Bachelor of Science) |
| Architecture | Nottingham (BArch), Cambridge, Taylor's → `pending/2026-11-12-architecture.ndjson` | Manchester: 2027 fees not set (and no international fee given). Universiti Malaya: 3.5-year degree; the fee averaging only handles whole years so far |
| US majors (same college) | Psychology: Harvard, Princeton, Stanford, Penn, Cornell, NYU, ASU. Biology: Harvard (Molecular and Cellular Biology), MIT, Princeton (Molecular Biology), Stanford, Penn, Cornell, NYU, USC, ASU. Architecture: MIT, Princeton, Penn. Also MIT Brain and Cognitive Sciences → `pending/2026-11-16-us-majors.ndjson` | Purdue: its fee page is behind a bot check, and fees differ by college. USC Psychology: no official degree page found. Cornell and USC Architecture: 5-year degrees with portfolio rules, not added |
| Netherlands Psychology (English track) | University of Amsterdam (270 places), Twente (250 places); both selective (numerus fixus), apply by 15 January 2027 → `pending/2026-11-16-nl-psychology.ndjson` | Delft, Eindhoven: no psychology bachelor's |
| Canada Psychology and Biology | UBC (Psychology BA, Arts; Biology BSc, Science), Toronto St. George (Psychology and Biology HBSc, Life Sciences stream), McGill (Psychology and Biology BSc, Faculty of Science), Waterloo (Psychology and Biology BSc, Life Sciences) → `pending/2026-11-16-canada-majors.ndjson` | UBC's student tuition page answers 403; fees come from the Academic Calendar's per-credit table × the degree's 120 credits. Alberta: fees only come from an interactive cost calculator that opens a browser dialog when driven automatically; not done. McMaster: not yet |
| UAE | AUS: Chemical, Civil, Electrical Engineering, Architecture (BArch, 5 years, portfolio; same tuition for all majors and the same subject rules for each major group, so admission and fees reuse AUS Computer Engineering / Computer Science). Heriot-Watt Dubai: Psychology, Civil Engineering, Mechanical Engineering, Architecture. Birmingham Dubai: Psychology → `pending/2026-11-17-uae-majors.ndjson` | AUS Mechanical Engineering and Biology: their pages don't state a length. AUS Psychology: no subject rule published for it, so the shared records can't be reused. McMaster: first-year Gateway admission and interactive requirement and cost pages; not done |
| UAE and UNSW, second batch | RIT Dubai Psychology (BS; same AED 68,000 tuition as every RIT Dubai bachelor's), Canadian University Dubai Psychology (BA and BSc), UNSW Architectural Studies → `pending/2026-11-17-uae-unsw-more.ndjson` | RIT Dubai Electrical, Mechanical, Industrial Engineering: course sequences run to a fifth year (co-op), length unclear. CUD Architecture: page didn't load its details. Khalifa: one engineering admission, the existing record covers the branches. Sharjah, Zayed: not yet |
| University of Sharjah | Civil Engineering, Electrical and Electronics Engineering (one published criteria set for all engineering programmes, so entry requirements reuse Sharjah Engineering), Law in English (75%, 70% in Maths, IELTS 5.5). Fees from Sharjah's fee table: AED 63,740 a year each → `pending/2026-11-17-sharjah.ndjson` | Zayed: Psychology and Architecture listed, but the only programme details found are a 2018 study plan and older catalogues with conflicting credit totals; not added |
| Law and Biology, 2026-11-18 | Birmingham Law LLB (AAA, IB 6,6,6 with 32 points, LNAT not required; £10,050 UK, £26,220 international for 2027 entry), Nottingham Malaysia Biotechnology BSc (RM62,000 international, RM54,000 Malaysian, fixed fee), UNSW Bachelor of Science shown as "Science (Biology majors)" (one degree with 28 majors including Biology & Biodiversity and Molecular and Cell Biology; 2026 indicative international fee A$194,000 for the degree) → `pending/2026-11-18-law-biology.ndjson` | Birmingham Biological Sciences BSc and Psychology BSc: 2027 entry requirements and UK fee are published, but the international fee says "To be confirmed"; held until it is published. Nottingham Malaysia: no Biology or Biomedical Sciences page (the Biomedical Sciences URL returns 404); Biotechnology is its life-science bachelor's found |

Built on their own (`build.py` on a folder holding only the new files) because the
local page cache is missing Taylor's pages (`c5f814882b10`, `17b45e628af2`), so the whole
Law and Biology folders can't be rebuilt on this machine until those pages are re-fetched.
The new pages aren't sources for any other research file, so no shared excerpt is affected.

### New subjects, UK, Malaysia and UNSW (2026-11-18) → `pending/2026-11-18-new-subjects.ndjson`

New subject folders: `mathematics/`, `physics/`, `chemistry/`, `pharmacy/`, `politics/`,
`accounting/`, `dentistry/`, `humanities/`. Generators: `scripts/research/gen/uk_birmingham.py`,
`uk_nottingham.py`, `uk_manchester.py`, `uk_warwick.py`, `uk_imperial.py` (quotes are lifted
line by line from the saved pages; build.py re-checks them). All fees are for 2027 entry.

| University | Added | Held / not added |
|---|---|---|
| Birmingham | Mathematics, Physics, Chemistry, Electronic and Electrical Engineering, Aerospace Engineering, Computer Engineering, Accounting and Finance, International Relations, Politics and International Relations, PPE, Dental Surgery (BDS, 5 years; international £30,180 in year 1 then £53,880 in years 2-5, shown as the 5-year average, our calculation; UCAT, interview, deadline 15 October 2026) | Mechanical Engineering: already in Sanity as `program-uk-birmingham-beng-engineering` (same page). Biological Sciences, Psychology: international fee "To be confirmed" |
| Nottingham | Mathematics, Physics, Chemistry, Pharmacy (MPharm, 4 years), Aerospace Engineering, Politics and International Relations, PPE, Finance Accounting and Management, Biochemistry, Pharmacology, English, History, Geography | Mechanical: already in Sanity (`program-uk-nottingham-beng-engineering`). Veterinary Medicine, Physics with Astronomy, Mathematics and Economics: guessed page addresses returned 404, not pursued |
| Manchester | Mathematics, Physics, Chemistry, Pharmacy (MPharm, interview), Aerospace Engineering, Politics and International Relations, PPE, Accounting and Finance, English Literature, History, Geography, Biochemistry, Pharmacology. "3 or 4 years" courses stored as 3: the fourth year is an optional year abroad or placement (quoted) | Dentistry: year 1 fee £40,200 (2027/28), but the clinical-year fee is only published for students entering Year 2 in 2027 (£63,900), not for a 2027 starter; a full-course cost would be a guess. Held |
| Warwick | Mathematics (TMUA typically required), Physics, Chemistry, Politics and International Studies, Accounting and Finance, History. Overseas fees from the 2027-28 column of Warwick's overseas fees table; English level from the course's band | English Literature: the fees table row reads "Band 0 £21,950 £27,870 £21,950" (2027-28 lower than 2026-27), which looks like an error on Warwick's page. Held. PPE and Pharmacy: guessed page addresses 404 |
| Imperial | Mathematics (TMUA), Physics (ESAT), Chemistry, Biochemistry (ESAT), Aeronautical Engineering (MEng, ESAT), Biomedical Engineering (MEng) | Mechanical: already in Sanity |
| Nottingham Malaysia (`gen/my_nottingham.py`) | Biomedical Science, Finance Accounting and Management, International Business Management, International Relations, English Language and Literature, Mathematics and Data Science, Mechatronic Engineering (MEng, 4 years). Fixed fees for a September 2027 start; 6% SST on top for non-Malaysians | Pharmacy MPharm: 2 years in Malaysia (RM75,000 a year) then 2 years in the UK (GBP £33,500 a year); one cost record holds one currency, so it can't be stored faithfully. Held |
| UNSW (`gen/au_unsw.py`) | Economics, Arts, Actuarial Studies, Data Science and Decisions, Medical Science, International Studies, Media (Communication and Journalism). 2026 indicative international fees; 2026 A-level/IB offer scores (a guide); NSW "assumed knowledge" shown in the threshold text, not as required subjects | Exercise Science: guessed page address 404 |

Not done yet (pages read, records not built):
- Cambridge (Mathematics, History, English, HSPS, Geography, Veterinary Medicine, Land Economy,
  History and Politics, Philosophy): course pages load the College list by script, and the
  College used for the fee (Queens') isn't listed for several of them; the 2027-28 fees PDF
  isn't in the local cache. Needs the lowest-fee College that offers each course.
- Taylor's (Pharmacy, Biomedical Science, Accounting and Finance, Actuarial Studies, Finance and
  Economics, PPE, International Relations, Mass Communication, Software Engineering, Mechatronics,
  Hospitality): pages are saved, but their entry blocks differ page to page (some give no A-level
  line in the usual place; several are dual awards). Each needs reading by hand.
- Universiti Malaya: course pages plus the international fee PDF; not started this pass.

### US and UBC majors, second batch (2026-11-18) → `pending/2026-11-18-us-ubc-majors.ndjson`

Same-college reuse (admission and fee records of an existing programme in the same college,
with a quote saying so). Generators: `scripts/research/gen/us_more.py`, `ca_ubc.py` (end).

| University | Added | Held / not added |
|---|---|---|
| Harvard | Mathematics, Physics, Chemistry, Government, History, English, Philosophy (each tagged "B.A." on the concentrations page) | |
| Penn (School of Arts & Sciences) | Mathematics, Physics, Chemistry, Biochemistry, Political Science, International Relations, History, English, Philosophy | |
| MIT | Mathematics (18), Physics (8), Chemistry (5), Mechanical Engineering (2), Aerospace Engineering (16), Chemical Engineering (10), Political Science (17) | |
| Stanford | Mathematics, Chemistry, Mechanical Engineering (BS) | Physics, Political Science, History, English: guessed bulletin addresses (PHYSICS-BS, POLISCI-BA, HISTORY-BA, ENGLISH-BA) returned 404 |
| Cornell (College of Arts and Sciences) | Mathematics, Physics, Chemistry, Government, History, English (each page's header names the college) | |
| NYU (College of Arts and Science) | Mathematics, Physics, Chemistry, Politics, History | English: bulletin address 404 |
| UBC Vancouver | Mathematics, Physics, Chemistry (Faculty of Science, as Biology), History, International Relations, Philosophy, Political Science (Faculty of Arts, as Psychology). Each programme page and its UK and US requirement views carry the same faculty-wide lines | English: its page (static and in the browser) doesn't show the general IB requirement line; held |
| Princeton | — | The concentrations page lists A.B. and B.S.E. concentrations together without saying which degree each leads to; not added until a department page can be quoted |

Found on the way:
- `build.py` and `q.py` passed the Sanity read token to curl as a command argument; when a
  query failed on a network error, the traceback printed it. Fixed: the token now goes to
  curl on stdin (`-H @-`) and a failed query prints only curl's exit code (negative-tested
  with a dead proxy). Builder output otherwise unchanged (Birmingham rebuilt and diffed).
- The simulator fetches live exchange rates, so USD figures move between runs; diffs above
  compare everything except the USD column.

### Toronto and McGill, more majors (2026-11-18) → `pending/2026-11-18-toronto-mcgill.ndjson`

| University | Added | Held / not added |
|---|---|---|
| Toronto, St. George, Arts & Science (`gen/ca_ut_more.py`) | Mathematics, Physics, Chemistry (HBSc, OUAC TPG), Political Science (HBA, TAX), History, English (HBA, TAH). Requirement rows read only from the St. George section of each IB, British-patterned and U.S.-patterned view (the pages also list Mississauga and Scarborough). Fee: Arts & Science international program fee 2026/27 CAD 66,110 in Year 1 (all admission streams) and in Year 2 or higher; the Honours BA Year 2 row (CAD 66,110; incidental fee CAD 2,135.97) was read from Tuition Explorer (`program=7`) | |
| McGill (Faculty of Science) | Chemistry (Physical, Earth, Math & Computer Sciences group: IB 35 to 38, A-Levels A*AA to ABB; Science prerequisites; CAD 64,785.90) | Mathematics and Physics: their pages say only "apply to the Faculty of Science" without naming the admission group, so the grade range can't be assigned. Held |

Found on the way (to check, not changed):
- `program-uk-birmingham-beng-engineering` is named Mechanical Engineering and points to the
  Mechanical page, but its summary still reads "BEng Engineering ... Disciplines: Mechanical,
  Electrical, Chemical, Civil, Materials. A-level offer not verified from primary source this pass."
- `build.py` patches a shared source excerpt without `ifRevisionID`; the guard was added to the
  patch in this pending file by hand (the live `_rev` at build time).

### USC, ASU and Waterloo majors (2026-11-19) → `pending/2026-11-19-usc-asu-waterloo.ndjson`

| University | Added | Held / not added |
|---|---|---|
| USC, Dornsife (`gen/us_more2.py`) | Mathematics (BS), Physics (BS), Chemistry (BS), Biochemistry (BS), Political Science (BA), International Relations (BA), History (BA), English (BA), Philosophy (BA), Psychology (BA). Degree names from the 2026-2027 catalogue's Programs by School page, Dornsife section (read in the browser; the page is script-loaded). Admission and fee records reused from Economics (same school) | Neuroscience: no matching subject on the site yet |
| ASU, The College of Liberal Arts and Sciences, Tempe (`gen/us_more2.py`) | Mathematics (BS), Physics (BS), Chemistry (BS), Biochemistry (BS), Political Science (BA), History (BA), Philosophy (BA). Each degree page: "All students are required to meet general university admission requirements." Plan codes from ASU's degree search. Admission and fee records reused from Economics, as for Psychology and Biological Sciences; the fee includes ASU's highest college fee (labelled; the real CLAS fee may be lower) | English: ASU's degree search lists the CLAS English BA as online only |
| Waterloo (`gen/ca_waterloo_more.py`) | Biochemistry (Life Sciences, same sources as Biology), Physics and Chemistry (Physical Sciences: same three requirement lines as Life Sciences, on the group's own pages), Political Science, History, English, Philosophy (Honours Arts: A-Levels two Bs and one C; IB total 27; US "low 80s", stored as text, so the site can't compare it), Mathematics (BMath: A-Level Maths A plus two As; IB HL Maths AA 6, total 30; US 88%; Admission Information Form). Fees: Fall 2026 international maximum tuition per term × 2 terms, Regular Year 1: Science CAD 25,296, Arts CAD 27,010, Mathematics CAD 29,259 | |
| Princeton | — | The admission page lists concentrations without saying A.B. or B.S.E. for each; the Undergraduate Announcement (ua.princeton.edu) shows a Cloudflare bot check (not bypassed); department pages tried either show the same check or don't name the degree |

### University of Sydney (2026-11-19) → `pending/2026-11-19-sydney.ndjson`

Source: the University of Sydney International Guide, applying for 2027 entry (PDF,
`usyd-international-guide.pdf`), read with `pdftotext` (no `-layout`, saved as
`usyd-intl-guide-notes`). Generator `gen/au_usyd.py`. Each record quotes the table header (column
order), the course's table row, the course's own block (ATAR, IB, duration, assumed knowledge;
its IB and duration must match the row), the A-level aggregate rule (A*=6 ... E=1) and "Tuition fees
are subject to annual increases". Two rows (B Arts, B Arts and B Laws) print without the course name
in that copy; the generator takes their CRICOS code from the `-layout` copy, where name and row are
on one line, and checks the two rows agree. Fees are the 2027 indicative Year 1 fee per 1.0 EFTSL.

| Added | IB | A-level aggregate (3 / 4 subjects) | AUD per year |
|---|---|---|---|
| Mathematical Sciences | 34 | 15 / 16 | 63,600 |
| Psychology | 29 | 13 / 13 | 63,600 |
| Science (Biology, Chemistry and Physics majors: three records, one degree) | 29 | 13 / 13 | 63,600 |
| Science (Medical Science) | 31 | 14 / 14 | 63,600 |
| Arts | 26 | 12 / 12 | 55,100 |
| International Studies | 31 | 14 / 14 | 55,100 |
| Politics, Philosophy and Economics | 32 | 14 / 15 | 55,100 |
| Commerce | 38 | 17 / 19 | 59,100 |
| Design in Architecture | 34 | 15 / 16 | 55,100 |
| Pharmacy (Honours) and Master of Pharmacy Practice (5 years) | 31 | 14 / 14 | 63,600 |
| Arts and Laws (5 years) | 38 | 16 / 18 | 59,100 |

Not added: Melbourne majors. Melbourne publishes the Bachelor of Science international fee as a
range that depends on subjects chosen (the existing record stores the lowest), so a per-major fee
would be a guess.

### Purdue majors, and Monash blocked (2026-11-19) → `pending/2026-11-19-purdue.ndjson`

| University | Added | Held / not added |
|---|---|---|
| Purdue, West Lafayette (`gen/us_purdue.py`) | Mathematics, Physics, Chemistry, Biology (BS, College of Science), History, English, Political Science, Philosophy (BA, College of Liberal Arts), Psychological Sciences (BS, College of Health and Human Sciences). Degree, college and minimum high-school coursework quoted from each admissions major page. Admission records are Purdue-wide (test scores, English) and reused from Computer Science; the fee is not copied from CS (CS pays a differential). Fee: Bursar 2026-2027 general Fall/Spring flat rate, international sub-total USD 32,104 (the generator checks this figure sits in the general block, before the first differential block). The Bursar lists differential fees only for CS/Data Science/Engineering, Daniels Business/BA Economics, Polytechnic, Veterinary Technology and Nursing | |
| Monash (Clayton) | — | Course pages show a Cloudflare security check, in the browser too (not bypassed). Blocked |
| Monash Malaysia | — | Course and fee pages show the same check. Blocked |

### NYU Abu Dhabi, Twente and Universiti Malaya (2026-11-19) → `pending/2026-11-19-nyuad-twente-um.ndjson`

| University | Added | Held / not added |
|---|---|---|
| NYU Abu Dhabi (`gen/ae_nyuad.py`) | Mathematics, Physics, Chemistry, Biology, Mechanical, Civil and Electrical Engineering (BS); Political Science, History, Philosophy (BA). Degree from each NYU Bulletin page (NYU Abu Dhabi › Programs › …), matching NYUAD's rule (BA: Arts and Humanities, Social Science, Psychology; BS: Engineering, Science). Admission and fee records reused from Economics: "Students declare a major by the end of their second year." (graduation requirements page, read with its sections opened) | Psychology: the Bulletin page says "Psychology (BS)", NYUAD's page says Psychology majors earn the BA. Conflict, held |
| Twente (`gen/nl_ut.py`) | Advanced Technology, Applied Mathematics, Applied Physics, Business Information Technology, Civil Engineering, Communication Science, Creative Technology, Electrical Engineering, Industrial Design Engineering, Industrial Engineering and Management (all BSc, 3 years, English). Required A-Level and IB subjects from the two shared "admission requirements per bachelor's programme" lists (September 2027 intake); fees from each programme's fee page: 2027-2028 non-EU €16,869 (Communication Science, an Alpha-Gamma programme, €12,652), EU €2,771 | Biomedical Engineering, Health Sciences, Technical Medicine: the lists require Dutch |
| Universiti Malaya (`gen/my_um.py`) | Chemistry, Physics, Biochemistry, Actuarial Science, Business Administration, Finance, Architecture, Biomedical Science, English, History. A-Level and IB lines from each page's International tab only (the generator checks they come after the last "Malaysian citizen" block); fee from the page and the matching row of the 2025/2026 international fee structure, spread over the stated duration (several are 3.5 years) | Law: no international fee and no international IB line on its page. Mathematics, Pharmacy, Accounting, Dentistry, International & Strategic Studies: the course addresses tried return 404 |

Builder change: a "published total ÷ years" fee formula may now divide by a decimal duration
(3.5 years). Rebuilding the earlier formula records whose pages are cached (UNSW 9,
Birmingham Dentistry) with the old and new builder gives identical output; a formula that
divides by the wrong number of years is still refused (negative-tested with 60900/3 on a
3.5-year programme).

Site code change (`decision-engine.ts`, `pickProgram`): when a search falls back to a related subject
(e.g. Economics → Business), a programme filed under that subject now comes before one that only has
the word in its name. Without it, Twente's Economics and Accounting searches showed Business
Information Technology instead of International Business Administration. Simulator: on current data
the change alters nothing; with this batch it alters only those four Twente results. To check: an
"Engineering" search at Twente now shows Advanced Technology (filed as Engineering) rather than
Mechanical Engineering, because an exact field match comes first.

Also tried, not added:
- TU Delft (Earth, Climate and Technology; Nanobiology): requirements and study load read, but
  Delft's fee page writes the BSc institutional rate as "€ 20.563" (dot as thousands separator) and
  the programme fee pages show no figure; the builder reads 20.563, so nothing is built
  (`gen/nl_delft.py` marked HELD).
- McMaster (Chemical & Physical Sciences, Life Sciences, Mathematics & Statistics Gateways,
  Humanities I): requirements (from the requirements tool, international applicant with British,
  IB and US views) and 2026/2027 international tuition estimates (cost estimator: CAD 47,535.30
  Science gateways, CAD 45,158.40 Humanities/Social Sciences; Computer Science returns the stored
  CAD 56,232.60) were read and saved as `mcm-req-*` / `mcm-cost-*`, but no page read states the
  programmes' length, so they are not built. Health Sciences also needs a supplementary
  application.
- Oxford, Melbourne: Cloudflare "Just a moment..." check. Alberta: CloudFront "Request blocked"
  (403). Blocked, not bypassed.
- Not attempted this pass: Cambridge (College fee issue above), Taylor's (pages saved, irregular),
  HCT, Khalifa, Zayed, UAEU, RIT Dubai, Canadian University Dubai, Birmingham Dubai, and the German
  universities.

Medicine not offered as a first degree (no record added): US universities (medicine is a
graduate degree there), Warwick (graduate entry only).

## Found on the way

- `selectCost` picked the highest fee number across currencies, so Taylor's
  Medicine would have shown the Malaysian MYR fee to international students.
  It now prefers the international fee group (no existing programme changed).
  The builder also refuses to add living costs in a different currency.
- Universiti Malaya: existing records say fees are SST-exempt, but UM's Medicine
  page says its fee is "Not inclusive of 6% Sales and Service Tax". To check.
- Taylor's Medicine: fee shown per year (USD 26,987) rounds to USD 134,935 over
  5 years against the published USD 134,937.

- Cambridge existing cost records use a £12,500 College fee (Darwin), but Darwin
  isn't among the colleges listed for Medicine and appears to admit graduates
  only; the note on those records says the median (£14,100) is used. To check.
- `deadlinesFor` showed a university-wide deadline next to a programme's own
  one; a programme's own deadlines now replace it (no existing programme
  changed).

- Engineering: someone asking for one branch (e.g. Civil) could be shown another
  branch (Mechanical) because the fallback matched any "Engineering" title. The
  fallback now only offers general Engineering programmes, never another branch.
- Taylor's: course pages give 2026 programme totals in USD for international
  students, while Taylor's 2027 fee schedule (PDF) is in MYR. New records use the
  course-page USD totals (shown as tuition only). The existing Mechanical record uses
  the 2027 schedule and stores RM 46,057 a year while its own note says RM 44,048.
  To check.
- Waterloo Engineering: the existing international record stores CAD 69,539 a year
  while its note says CAD 69,884 (2 × 34,942). To check.

- Faculty names are now checked against the programme page. Six weren't on it
  and were cleared or corrected, including Birmingham Medicine ("Birmingham Medical
  School" → "Medical School", the page's wording; fix in `pending/2026-11-12-fixes.ndjson`).
- Cambridge Computer Science, Economics and Engineering: the College fee used
  Darwin (£12,500), but Darwin isn't one of the 29 undergraduate Colleges. Corrected
  to Queens' (£12,885), the lowest undergraduate College that offers each course
  (`pending/2026-11-12-fixes.ndjson`).
- Warwick Business: showed the 2026-27 overseas fee (£35,530) for 2027 entry.
  Corrected to £37,310 (2027-28, Band 2) from Warwick's overseas fees table
  (`pending/2026-11-12-fixes.ndjson`).
- A page used as a source by several subjects (e.g. Warwick's fee table, Cambridge's
  fees PDF) gets one source record with the quotes of all subjects, the same in
  every batch, so the batches can be applied in any order. A source already in
  Sanity is patched to the full set of quotes.

- 60 programmes (all US and most UAE universities) had "AUS online application" as
  their application form: the importer's default when a university had no platform
  name. Patched to each university's platform as already stored on its deadline
  records, or "Application form" where none is stored
  (`pending/2026-11-16-application-platform-fix.ndjson`); the importer no longer
  defaults to AUS. The site doesn't show this field, so no student saw it.

- The builder used to replace a shared source's excerpt with only this pass's quotes.
  Two records from the 2 November re-verification (Cambridge fees PDF, Universiti
  Malaya fee PDF) lost the quotes their older Computer Science, Economics and
  Engineering records rely on. Those quotes are recovered from Sanity's history
  (`pending/2026-11-16-source-excerpt-restore.ndjson`), and the builder now only
  appends missing quotes. Excerpts aren't shown on the site.
- UvA's fee page shows €2,694 under "Statutory tuition fees 2027-2028"; the
  government's 2027-28 fee is €2,771 (published by Twente, Erasmus, Radboud and
  Maastricht). Existing UvA records (€2,771) are right; the new Psychology record
  cites Twente's page for it. UvA's page looks out of date.
- Twente's English page (September 2027 intake) asks for TOEFL iBT 90, 21 per
  section; the existing Twente records say TOEFL iBT 80, 17 per section. To check.
- Universiti Malaya Computer Science: stores RM 22,300 a year (RM 89,200 ÷ 4)
  but its note says 3.5 years, RM 25,486 a year. To check.
- McGill: the Faculty of Science says students "are normally admitted to a four-year
  degree requiring the completion of 120 credits" (up to 30 credits of advanced
  standing can shorten it). The existing McGill BSc Computer Science and BA
  Economics records say 3 years. The new McGill records use 4. To check.
- Waterloo AFM: the existing international record stores CAD 54,020 a year, but its
  own note says CAD 55,346 (2 × 27,673, the AFM co-op rate). To check.
- AUS Computer Science cost: stores compulsory fees of AED 886 a year, but its own note
  says about AED 1,486. To check.
- Heriot-Watt Dubai "Engineering": the existing record points to the Electrical and
  Electronic Engineering page, so it is that branch, not engineering in general.
- Birmingham Dubai Psychology: the page gives no English score, so none is stored.
- Heriot-Watt Dubai Civil, Mechanical and Architecture: the course pages give the fee
  without naming the intake; stored as "intake not stated".
- RIT Dubai Computer Engineering: stored as 4 years, but RIT Dubai's engineering course
  sequences (Electrical, Mechanical, Industrial) run to a "Fifth Year". To check.
- University of Sharjah: existing records store AED 63,740 a year while their note says
  about AED 60,703. Sharjah's fee table (students admitted from 2022/2023) gives AED 63,740
  for Computer Science, Business, Economics, Civil and Electrical Engineering, so the stored
  figure is right and the note is out of date.
- Canadian University Dubai: the Computer Science record uses the pre-VAT credit fee and
  the BBA record the VAT-inclusive one. New Psychology records use VAT-inclusive fees. To check.

## Data fixes, 2026-11-17 (`pending/2026-11-17-data-fixes.ndjson`)

Every item marked "To check" above was re-read from the university's own page:

- Taylor's Computer Science, Business and Mechanical Engineering (international): the
  stored figure used the Malaysian-student total plus 6%. Taylor's 2027 international fee
  schedules give the tuition: RM 127,776 / 3, RM 136,200 / 3 and RM 176,192 / 4, so
  RM 42,592, RM 45,400 and RM 44,048 a year (6% service tax extra).
- Universiti Malaya Computer Science and Economics are 3.5-year degrees on UM's course
  pages (stored as 4 and 3). Durations and yearly fees corrected for international and
  UPU students; UM's pages say fees are "Not inclusive of 6% Sales and Service Tax", so
  the "SST-exempt" notes are corrected (also on Electrical Engineering).
- Twente: English test levels updated to TOEFL iBT 90 (21 per section) or 4.5 on the
  new scale, from Twente's language requirements page.
- McGill BSc Computer Science: 4 years (Faculty of Science, "normally admitted to a
  four-year degree requiring the completion of 120 credits"). Commerce and Economics are
  left at 3: the Commerce rules say "three- or four-year" and no Arts statement was found.
- RIT Dubai Computer Engineering: 5 years; its typical course sequence runs to a fifth
  year (with co-op).
- AUS: compulsory fees were the activities fee only (AED 886). Every student also pays a
  health plan (at least AED 300 a semester) and the clinic fee (AED 112.50 + VAT a
  semester): about AED 1,722 a year, on all eight AUS records.
- Canadian University Dubai Computer Science and Engineering: the stored amounts already
  include VAT; the notes said pre-VAT. Notes corrected.
- University of Sharjah: stored AED 63,740 is right; notes now quote the fee table.
- Waterloo Engineering and AFM: stored first-year figures are right (terms 1A + 1B);
  notes corrected.
- Heriot-Watt Dubai: the "Engineering" record is renamed Electrical and Electronic
  Engineering (the page it points to).
- Checked, no change: Taylor's Medicine shows USD 26,987 a year (USD 134,937 / 5,
  rounded).

## 2026-11-25: Taylor's, eleven more programmes

`taylors/` (generator `scripts/research/gen/my_taylors_more.py`) → `pending/2026-11-25-taylors.ndjson`
(66 records, dry-run HTTP 200, all creates). Software Engineering, Accounting and Finance,
Actuarial Studies (3-year route), Finance and Economics, Mechatronics Engineering, Pharmacy,
Biomedical Science (3.5 years), Mass Communication, International Relations, Philosophy, Politics
and Economics, International Hospitality Management (April/September intake fee; January is
USD 40,736). Fee rule as before: the course page's 2026 USD total for international students ÷
years, excluding the 6% Service Tax; Malaysian MYR total ÷ years. Each page read by hand (A-level,
IB and English lines differ page to page). Sim (IB 37-39, $60k): Economics now offers Taylor's
Finance and Economics (IB 26) instead of Business; International Relations and Pharmacy (IB 30)
added; Computer Science unchanged. Builder negative test: a changed IB score was refused.
Not added: Mechanical/Chemical/Electrical (already in), Medicine (in).

## 2026-11-25: HCT, twelve programmes

`hct/` (generator `scripts/research/gen/ae_hct.py`) → `pending/2026-11-25-hct.ndjson` (75 records:
74 creates + 1 source excerpt that only grows, 886 → 1,932 characters; dry-run HTTP 200).
Accounting, Actuarial Science, Business Analytics, International Business, Marketing, Digital
Media, Chemical / Civil / Electrical / Mechanical / Mechatronics Engineering Technology, Nursing.
Fee: International Admissions page, 2026-2027 expatriate rate AED 2,473.63 per credit hour × the
HCT Catalog's "Total Credits 120" ÷ "Minimum Duration of Study 4 years" = AED 74,208.90 a year
(our calculation; equals the existing Finance record). Entry: the division table plus HCT's own
IB SL / A-level equivalents; English TOEFL iBT 71 or 4.0, or 80% in school English. Teaching
language not stated on any HCT page read, so none stored (the site then makes no language claim).
Builder: new `credits_source` (credit total quoted on another source of the same record);
all 22 earlier folders rebuilt with old and new builder: identical output.
Sim (IB 34-36, $40k): HCT now offered for Accounting, Mechanical Engineering, Nursing; Business
shows Business Analytics (requirement published) instead of Finance (none). All "can't compare":
HCT sets subject grades, not an overall score.

## 2026-11-25: Khalifa University, eleven BSc programmes

`khalifa/` (generator `scripts/research/gen/ae_khalifa.py`) → `pending/2026-11-25-khalifa.ndjson`
(57 records: 55 creates + 2 source excerpts that only grow; dry-run HTTP 200). Aerospace,
Biomedical, Chemical, Civil, Electrical, Mechanical, Petroleum and Energy Engineering,
Engineering Systems and Management, Robotics and AI, Applied Mathematics, Statistics and Data
Science. Fee: KU fee page "Bachelor of Science (BSc) 81,250 AED 4 Years" (AED 2,500 per credit
hour); note marks the conflict with KU's partial-scholarship page (higher "Full Tuition"), so
/answers shows the conflict warning. Living cost reused from the existing Khalifa engineering
record (housing AED 20,000 a year), so new and old records compare like for like. Entry: IB
full diploma, 4 in each subject, 24 total, Maths + Physics; A-level Maths + Physics at C;
IELTS 6.0 / TOEFL iBT 79; KU admission tests; graduated no earlier than 2023. Teaching language
not stated. Sim (IB 34-36): Mechanical / Aerospace now match the named programme (was generic
"Engineering"), same cost $27,570; Mathematics adds Applied Mathematics (IB 24).

## 2026-11-25: Canadian University Dubai, eleven programmes

`cud/` (generator `scripts/research/gen/ae_cud_more.py`) → `pending/2026-11-25-cud.ndjson` (78 records:
77 creates + 1 fee-page excerpt that only grows; dry-run HTTP 200). Computer and Networking
Engineering Technology, Artificial Intelligence (published AED 79,712.33 a year), Cyber Security,
Software Design (AED 72,465.90), seven BBA concentrations (AED 2,359.35 × 30 credit hours =
AED 70,780.50, our calculation: CUD's "Tuition per Year" column shows AED 0.00 for BBA rows).
Length "4 Years (8 Semesters)" and credit hours from each programme page. Teaching language
not stated on pages read. Held: Communication (no fee row).

## 2026-11-25: University of Birmingham Dubai, thirteen courses

`bham-dubai/` (generator `scripts/research/gen/ae_bham_dubai.py`) → `pending/2026-11-25-bham-dubai.ndjson`
(78 creates, dry-run HTTP 200). Biomedical Science, Accounting and Finance, Business Management
with Economics / Finance / Marketing / Psychology, Money Banking and Finance, AI and Computer
Science, Mechanical Engineering, Mechanical Engineering (Biomedical), Robotics and AI, Commercial
Law, Digital Media and Communications. Fee: the page data's "Fees (international)" September
2027 figure (raw.py → <id>-raw), equal to the visible UK/Ireland box on every page. Entry lines
taken from each page. Held: Civil and Electronic/Electrical Engineering (years 2-3 in the UK).
Sim (IB 37-39): Accounting and Finance now shows the named course (IB 32); Law adds Commercial Law.

## 2026-11-25: RIT Dubai, seven programmes; builder length rules

`rit/` (generator `scripts/research/gen/ae_rit_more.py`) → `pending/2026-11-25-rit.ndjson` (40 records:
36 creates + 4 excerpts that only grow; dry-run HTTP 200). Cybersecurity, Electrical, Mechanical,
Industrial Engineering (5 years: typical sequence runs to a "Fifth Year"), Finance, Marketing,
New Media Design (4 years). Fee AED 68,000 a year (RIT tuition page; copied from the Global
Business Management record with its AED 20,000 living estimate). Entry from the group PDFs
(Business, Computing, Engineering: IB 28 with Maths/Physics/Chem-or-Bio at 4; New Media Design).
build.py: (1) the last year of a published typical sequence ("Fifth Year") now counts as the
length when no later year is named; (2) a record fails if its own quotes name a later year than
its length (closes a gap where a college major could inherit a shorter length). Negative tests:
4-year claimed as 5 refused; 5-year claimed as 4 refused. All 26 other folders rebuild identically.

## 2026-11-25: Politecnico di Milano (new country: Italy); new-university tooling

Why: a strong student with a low budget was only shown Malaysia and a few UAE options. First of
the low-cost countries Subhan chose (Italy; Japan and Korea; Turkey and Central Europe; Hong Kong,
Singapore, Taiwan and China).

`it-polimi/` (generator `scripts/research/gen/it_polimi.py`) → `pending/2026-11-25-polimi.ndjson`
(48 lines: 6 base records first, then 42 programme records; dry-run HTTP 200). Four BSc taught in
English, 3 years each (programme pages): Engineering Science (Milan), Process Engineering (Cremona),
Industrial Engineering (Piacenza), Civil Engineering (Milan, Italian or English).
- Fee 2026/2027: one income-based scale for every bachelor's student; EUR 3,943.04 is the maximum
  (charged without an ISEE; all-inclusive contribution), EUR 157.04 with an ISEE up to EUR 22,000;
  income abroad needs an ISEEU parificato. The maximum is stored (overstating is the safe error).
- Entry: no school-grade cut-off; ranking on an entrance test (TOL, or CEnT-S / SAT in English),
  2026/2027 call (the next isn't published). English: TOEFL iBT 59, IELTS 5, Cambridge B2 First C.
- Living: top of each monthly range on PoliMi's cost-of-living page (700 + 200 + 200 + 30 + 30) × 12
  = EUR 13,920 a year, our calculation.
- Visa: links only (Universitaly; Il visto per l'Italia), no figures yet.
Sim (IB 40+, $20,000, Mechanical / Civil Engineering): PoliMi now appears at about $19,533 a year,
"Requirement published, but not as a grade we can compare" (correct: entry is by test ranking).

Tooling: `scripts/research/new_university.py <spec> <pages> <out>` creates country (if new), city,
university, fee groups and source records from a spec in `fact-checks/research/universities-2026-11/`,
with the same quote checks; it never overwrites an existing university. `build.py` gained
`costs[].living` (monthly amounts quoted from the university's page × months, our calculation;
negative tests: an unquoted EUR 750 refused, a wrong yearly total refused) and an optional 4th
argument naming a pending base file whose fee groups count as existing (that file is applied first).

## 2026-11-25: low-budget batch 2: Bologna, Padua, METU, KAIST, BME (new countries: Türkiye, South Korea, Hungary)

Pending files (base records first, then programmes; all dry-run HTTP 200):
- `2026-11-25-unibo.ndjson` (`gen/it_unibo.py`): Economics and Finance, Business and Economics (3 years,
  English, SAT ranking, no minimum). Fees 2026/2027: maximum EUR 2,040 + EUR 157.04 (international);
  reduced fixed fee EUR 1,000 + 157.04 (nationals of non-OECD countries on Unibo's list) and EUR 500 + 157.04
  (particularly poor or developing countries), family income only outside Italy. Living EUR 8,944 (our calc).
  The engine shows the maximum by default; the reduced tiers show as tabs (matching citizenship to Unibo's
  Italian-language country lists is not automated yet). No English test stated on the pages read.
- `2026-11-25-unipd.ndjson` (`gen/it_unipd.py`): Information Engineering, Biology of Human and Environmental
  Health, Economics Governance and Decision-Making, Earth and Climate Dynamics: EUR 2,950 a year (course
  pages) + EUR 208 first-year instalment (not stated whether included, so added); CEnT-S; English B2.
  Living EUR 10,834 (our calc).
- `2026-11-25-metu.ndjson` (`gen/tr_metu.py`): nine 4-year B.S. programmes (7 Engineering at USD 1,200 a
  semester, Economics and Business Administration at USD 800), 2026-2027, two semesters (calendar). Entry:
  IB 33 / A-level ABB / SAT 1200 (Math 700 Engineering) minimums, list dated 05/01/2024. Living not stored:
  METU prices it in Turkish lira, tuition is in USD.
- `2026-11-25-kaist.ndjson` (`gen/kr_kaist.py`): eleven majors (undeclared entry, major chosen in year two),
  cost of attendance: tuition KRW 6,866,000, NHI KRW 916,680, living KRW 7,103,000; plus a KAIST Scholarship
  record (guaranteed, full tuition for 8 semesters, KRW 350,000 a month) so the site subtracts tuition.
- `2026-11-25-bme.ndjson` (`gen/hu_bme.py`): Computer Science Engineering, Electrical, Civil, Engineering
  Management, Mathematics: EUR 3,200 a semester (non-EU, 2026/27); 6-8 semesters; English B2. Living EUR 3,720
  (BME's own EUR equivalents; our calc).

build.py: European number format in quotes ("2.040,00 €", "€ 400,00"); living `weekly` (× 52) and `yearly`
items; lengths stated in semesters ("7 semesters" = 3.5 years). Negative tests: a 3.5-year length against
"6 semesters" refused; earlier checks unchanged.

Held: Politecnico di Torino (fee set per country of origin through a long table); University of Tokyo PEAK
(site unreachable from this machine and the browser, SSL error); Waseda SILS (about JPY 1.5-1.7 million a year,
mid-budget); Tsinghua (no undergraduate fee on the English programme pages read); Warsaw University of
Technology (English-taught fees EUR 3,000-5,700 a semester, credit-based); NUS and Hong Kong (about S$30,000+
a year, not low-budget); Taiwan (TWD isn't in the ECB rates the site uses).

## 2026-11-25: 10 per cheaper country (request in progress): Hungary done, Türkiye 2, Italy 2

Subhan: "10 per country, only the cheaper countries" (Italy, Türkiye, Hungary, South Korea, Germany, Malaysia).
New pending files (base records first; all dry-run HTTP 200): Türkiye: `boun` (6 engineering, USD 10,000),
`bilkent` (10, USD 18,400 for 2026 admits). Hungary: `elte` (4), `unideb` (6), `szeged` (3), `pecs` (6), `mate` (4),
`obuda` (6), `corvinus` (2), `sze` (4), `miskolc` (8), `pannon` (1). Italy: `sapienza` (2; band A/B/C fees EUR
300/700/1500 by country of income), `unipi` (1; max EUR 2,900 + EUR 140). Generators `scripts/research/gen/*` use
the shared `gen/newuni.py`. Several course pages don't state the fee's academic year; the records say so.
build.py: `tuition_per_semester` + `semesters_quote` ("N semesters (Y years)" or bare "N semesters"); "four
academic years"; space-separated thousands read in quotes only. 27 earlier folders rebuild identically.
Held: ITU (fee currency not stated), Hacettepe (2024 fee decision), Sabancı (USD 36,500), Trento (official
pages conflict: EUR 6,000 vs 3,000 max), University of Milan (Cloudflare bot check), Milano-Bicocca (course
list behind sign-in), Pisa IPH (own fee), several programmes whose pages lack length/language (see generators).

## 2026-11-26: order by international students; Malaysia APU, Sunway

Subhan: prioritise universities with the most international students (search estimates used only to choose
the order; nothing from them is stored). Pending: `2026-11-26-apu.ndjson` (3 computing BSc, RM108,500 over
3 years + 6% SST, IELTS 5.0), `2026-11-26-sunway.ndjson` (4 computing degrees, estimated 2026 fee USD
9,779-10,058, A-Level 12 points / IB 28, IELTS 6.0). Held: UCSI (fee layout on its pages can't be matched to
programmes), INTI ("Approx. RM 89,708" doesn't say whether per year or for the whole degree), APU Information
Technology (entry wording differs).

## Batch 2026-11-26 (THE most-international list, 10 universities)

Done (pending files `fact-checks/pending/2026-11-26-<name>.ndjson`, each dry-run HTTP 200):
edinburgh (3 BSc, £40,900/yr, living £1,546/month), leeds (2 BSc, £33,700), durham (2 BSc, £35,000),
bristol (3 BSc, £34,700 / £32,500), sheffield (2 BSc, £34,670), lse (3 BSc, £41,900 / £37,500 / £39,300),
anu (Bachelor of Computing, A$57,640), uq (Bachelor of Computer Science, A$60,952), cuhk (Computer Science and
Engineering, HK$230,000), caltech (Computer Science B.S., $68,574; housing + food $21,996 for nine months,
our calculation). Thresholds lead with the lowest published offer so the engine compares on it.

Held: Glasgow (grades and fees in tabs not readable), St Andrews (subject page and 2027 prospectus disagree,
fee not found), Trinity College Dublin (subject minimums only; no per-course non-EU fee line), UCL
(Cloudflare check).

Found on the way (fixed): the app only attached `programDetails` to universities with 2+ programmes, and
subject matching reads only that list, so single-programme universities never appeared (affected
University of Pannonia and University of Pisa already on staging). `sanity.server.ts` now always sets it.

To check: Leeds' IB requirement is "18 points at Higher level" (the site shows "can't compare"); Caltech
publishes no grade threshold; Bristol and LSE English requirements not stored (band not in saved text).

## Batch 2026-11-26 (THE list, second 10)

Done (pending `fact-checks/pending/2026-11-26-<name>.ndjson`, each dry-run HTTP 200; new countries ch, se, nz,
sg, fr, fi): eth (Computer Science, taught in German; CHF 4,380/yr threefold fee; living CHF 22,100; IB 38),
epfl (Computer Science, taught in French B2; CHF 2190/semester; living CHF 25,219; IB 38 within 3000 places),
nus (Computer Science; S$39,700 without MOE Tuition Grant, S$21,400 / S$18,050 with it; no entry rule stored),
wageningen (Data Science for Global Challenges; €18,300 2026-27, the two pages differ for 2027-28),
kth (ICT, SEK 453,000 for the programme = 151,000/yr our calculation; IB 24 is eligibility only, worded so the
site doesn't call it a match), polytechnique (École Polytechnique Bachelor of Science, €19,600 non-EU; no
minimum grades), auckland (BCom NZ$51,020, IB 28; BE(Hons) NZ$60,910, IB 33), groningen (Computing Science,
€19,800), leiden (Data Science & AI, €19,200; Computer Science is Dutch-taught), aalto (Data Science BSc(Tech),
€12,000).

Held: NTU (CS pages 404; no-grant fee lab/non-lab unclear). Blocked on the way: NUS grade-profile page
(Incapsula), Leiden science diploma PDF ("Access Blocked"), Aalto admission-criteria page (403).

Builder: `build.py` now reads Swiss thousands in quotes ("4’380" = 4380). Rebuilt hk-cuhk, gb-edinburgh,
gb-lse, au-uq: every rebuilt record identical; negative test refuses 4381 against "4’380".

## Batch 2026-11-26 (THE list, third 10)

Done (pending `fact-checks/pending/2026-11-26-<name>.ndjson`, each dry-run HTTP 200; new country at):
berkeley (EECS B.S.; $18,214 + nonresident $39,270 = $57,484 our calculation; housing + meals $23,640),
yale (CS B.S.; $72,500; housing + food $21,600), cmu (CS B.S.; $69,702; $19,650), jhu (CS B.S.; $68,670;
$21,967), gatech (CS B.S.; out-of-country $35,610 + fees $1,716; $14,628), vienna (Computer Science, entrance
exam, 415 places; €726.72 + €26.20 a semester), tuwien (Informatics, selection procedure; €726.72 a semester),
fu-berlin (Informatik, no tuition, €376.80 a semester), freiburg (€1,500 + €190 a semester), tuebingen
(€1,500 + €194.80 a semester; open admission). US admission is holistic: no admission rows stored.

Held: Geneva (403), KU Leuven (no 2026-27 bachelor fee), Aarhus (fee range only), Humboldt (no current fee
page), Cape Town (2027 fees not published).

To check: Georgia Tech's page estimates 2027-2028 out-of-country tuition lower ($34,572) than 2026-2027.

Builder: reads "6 semester" (singular) as a length; a per-term fee of 0 is allowed only with a quote saying no
tuition is charged; the fee-note check no longer strips every "0" when the fee is 0. Rebuilt hk-cuhk,
gb-edinburgh, ch-eth, ch-epfl, se-kth, nl-rug, fr-polytechnique (records identical) and hu-bme, hu-szeged with
old vs new builder (identical). Negative tests refuse a 0 fee without the quote and 4 years against "6 semester".
