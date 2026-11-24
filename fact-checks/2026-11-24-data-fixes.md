# Data fixes, 2026-11-24

Found by the SEO/content review of evidapath.com. Each figure re-read from the official page.
Pending file: `fact-checks/pending/2026-11-24-data-fixes.ndjson` (75 mutations; generator
`scripts/research/gen/fixes_2026_11_24.py`). Dry-run against Sanity: HTTP 200, 73 updates, 2 new
source records. `scripts/research/sim` before/after for Computer Science, Engineering, Economics and
Business (IB and A-level students): no change in any matching line.

| Record(s) | Finding on the official page | Change |
|---|---|---|
| Imperial EFDS international | "Tuition fees Home: £10,050 International: £44,800" (October 2027 start) | Fee unchanged; note no longer quotes the 2026-27 £42,700 |
| TU/e CSE, EE international | "2026-2027 2027-2028 Institutional fee for bachelor's students € 18,600 € 22,400" | Fee unchanged; note gives the 2027-28 figure |
| UBC Economics, Engineering, Commerce, CS international | UBC Calendar: "Arts $1,717.68", "Applied Science $1,789.18", "Commerce $2,222.61", "Science $1,769.40" (commenced 2026S or later) | Fees unchanged; note cites UBC, not "secondary sources"; 30 credits a year labelled our calculation |
| NYU Abu Dhabi (13 with a note) | "Student Tuition $68,576" (2026-2027 Estimated Cost of Attendance) | Note says it is tuition, not cost of attendance |
| UNSW Media international | "2026 Indicative full fee to complete degree $156,500*", "3 Year(s)", first year "$49,000*" | Note: 52,167 a year is our calculation; first-year fee given |
| AUS (32 admission records) | "IELTS Academic TOEFL iBT TOEFL iTP 6.5 4.5 (previously 80) 550"; "Only TOEFL and IELTS are accepted"; EmSAT 1550 listed for transfer applicants | English line rewritten; EmSAT no longer offered to first-year applicants; unsourced Bridge Program range removed |
| UAEU (16 admission records) | International applicants' page (read in a normal browser; site blocks automated fetches): average 85% (Business and Economics) or 90% (Engineering; Computing and AI), English 90% or IELTS 5.5 / TOEFL ITP 525 / iBT 70, college maths and science rules | Thresholds were the UAE nationals' figures (80%, IELTS 5.0, SAT 555 for all); now the international ones per college. Unsourced EmSAT test line removed; nationals page source detached |

Not done:
- UCL Economics note (says £39,200 for 2026-27 while the record shows £40,800 for 2027-28): ucl.ac.uk returns 403 to our fetcher and the browser extension has no permission for the domain. The note is already hidden on /answers. To check.
- Melbourne note with an estimated rise ("expected ~2-4% higher"): hidden on /answers; record not re-checked.
- University of Toronto Computer Science: the English line reads "C (final or predicted)", which is not an English test score. Seen on the new university page; record not changed. To check.
