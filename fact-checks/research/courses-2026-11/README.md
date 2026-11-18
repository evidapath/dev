# Course expansion (started 2026-11-11)

Adding Medicine, more Engineering branches, Psychology, Law, Biology/Life
Sciences and Architecture to the 53 universities, from each university's own
pages. Nothing goes to Sanity until it's built into
`fact-checks/pending/*.ndjson` and applied by hand.

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
