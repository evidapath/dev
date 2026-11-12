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
   a quote of the source it cites, and every deadline's day, month and year are
   quoted. Fees that change by year are averaged by the script from quoted
   figures (`tuition_formula`), never by hand.
4. Dry-run against Sanity (`?dryRun=true`), then write to `fact-checks/pending/`.

Living costs, university-wide compulsory fees (e.g. Nottingham Malaysia's visa fee)
and (where the page says so) English levels are reused from the same university's
existing verified records, by id.

## Status

| Subject | Done | Blocked / not offered |
|---|---|---|
| Medicine | Imperial, Cambridge, Birmingham, Manchester, Nottingham, UNSW, Taylor's, Universiti Malaya → `pending/2026-11-11-medicine.ndjson` | Cloudflare bot check: UCL, Oxford, Monash (AU and Malaysia), Melbourne. Held: UAE University MD (UAE nationals and children of Emirati mothers only) and Sharjah, until programmes can be limited by nationality. Not yet: Sydney (page loads by script), Germany and the Netherlands (taught in German/Dutch) |
| Engineering branches | Civil, Electrical and Electronic, Chemical at Imperial, Manchester, Nottingham; Civil and Chemical at Birmingham; Civil, Chemical, Mechanical at Universiti Malaya; Civil, Electrical and Electronic, Chemical at Nottingham Malaysia; Electrical and Electronic, Chemical at Taylor's → `pending/2026-11-12-engineering.ndjson` | Birmingham Electrical: its own subject list links to a missing page and no course page could be found. Not yet: Waterloo, Toronto, McGill (each branch is its own admission; fees come from per-term schedules), UAE universities. Not needed: US universities, UBC, McMaster, Alberta, Cambridge, Warwick, Oxford, UNSW, Monash AU (one Engineering admission; the existing record covers every branch) |

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
