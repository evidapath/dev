# Course expansion (started 2026-11-11)

Adding Medicine, more Engineering branches, Psychology, Law, Biology/Life
Sciences and Architecture to the 53 universities, from each university's own
pages. Nothing goes to Sanity until it's built into
`fact-checks/pending/*.ndjson` and applied by hand.

## How a programme gets in

1. Read the official page (`curl`, or the browser when a site blocks scripts),
   saving its text. Pages behind a bot check (Cloudflare "security
   verification") are not worked around; they're listed below as blocked.
2. Write one JSON file here per programme: values plus verbatim quotes.
3. `python3 -I scripts/programmes/build.py <this dir> <saved pages dir> <out.ndjson>`
   stops unless every quote is on its saved page, every number we store is in
   a quote of the source it cites, and every deadline's day, month and year are
   quoted. Fees that change by year are averaged by the script from quoted
   figures (`tuition_formula`), never by hand.
4. Dry-run against Sanity (`?dryRun=true`), then write to `fact-checks/pending/`.

Living costs and (where the page says so) English levels are reused from the
same university's existing verified records, by id.

## Status

| Subject | Done | Blocked / not offered |
|---|---|---|
| Medicine | Imperial, Cambridge, Birmingham, Manchester | UCL, Oxford: Cloudflare bot check |

Not offered as a first degree (no record added): US universities (medicine is a
graduate degree there), Warwick (graduate entry only).

## Found on the way

- Cambridge existing cost records use a £12,500 College fee (Darwin), but Darwin
  isn't among the colleges listed for Medicine and appears to admit graduates
  only; the note on those records says the median (£14,100) is used. To check.
- `deadlinesFor` showed a university-wide deadline next to a programme's own
  one; a programme's own deadlines now replace it (no existing programme
  changed).
