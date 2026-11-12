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
