# Course expansion (started 2026-11-11)

Adding Medicine, more Engineering branches, Psychology, Law, Biology/Life
Sciences and Architecture to the 53 universities, from each university's own
pages. Nothing goes to Sanity until it's built into
`fact-checks/pending/*.ndjson` and applied by hand.

## How a programme gets in

1. Read the official page (`curl`, or the browser when a site blocks scripts),
   saving its text. Pages behind a bot check (Cloudflare "security
   verification") are not worked around; they're listed below as blocked.
2. Write one JSON file per programme, in this subject's folder (`medicine/`,
   `engineering/`, ...): values plus verbatim quotes.
3. `python3 -I scripts/programmes/build.py <subject folder> <saved pages dir> <out.ndjson>`
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
