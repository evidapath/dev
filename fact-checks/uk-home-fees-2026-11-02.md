# UK Home fees + Nottingham international corrections — 2026-11-02

Pending file: `fact-checks/pending/2026-11-02-uk-home-fees.ndjson` (44 mutations). Backup taken before applying:
the staging export of 2026-11-02 (1,963 documents) in the session scratchpad (`export9.ndjson`).

## Why

In the 50-student run, British students in the UK were priced at overseas fees (~$50k/yr). Only Oxford had a Home
tier. The app now asks British and Irish students "I've lived in the UK for the last 3 years" and, when ticked,
applies the Home tier at UK universities (and treats international-only scholarships there as not open to them).

## Home fee: £10,050/yr for 2027 entry, all 7 universities

The government maximum for 2027/28 is £10,050 (Imperial: "2027–28 academic year: Maximum fee for standard
full-time courses will increase to £10,050 per year"). Each university's own page, read in headed Chrome:

| University | Source | Wording |
|---|---|---|
| Birmingham | birmingham.ac.uk/study/undergraduate/fees-funding/tuition | "The University will charge the maximum approved tuition fee per year. If your offer is for 2027 year of entry, we expect that the tuition fee for your first year of study will be £10,050." |
| Cambridge | trin.cam.ac.uk/undergraduate/finance/fees/ | "In 2027-28, the tuition fee for UK students studying for their first undergraduate degree is £10,050 for all courses." (Cambridge's own undergraduate site didn't load from our browser; the college page states the University fee.) |
| Imperial | imperial.ac.uk/study/courses/undergraduate/computing-meng/ | Home fee £10,050 (2027 entry); tuition-fees page: "the Home fee is the same for all of our undergraduate courses" |
| Manchester | 2027 course pages: BSc Computer Science, MEng Mechanical Engineering; Alliance MBS fees page | "Tuition fees for home students commencing their studies in September 2027 will be £10,050 per annum." AMBS: "£10,050 for the 2027/28 academic year (subject to Parliamentary approval)" |
| Nottingham | nottingham.ac.uk/fees/tuitionfees/202728/undergraduate.aspx | "The university will charge the maximum approved fee"; table lists £10,050 Home for each course |
| UCL | UCL undergraduate fees 2027 to 2028 | "UK undergraduate fees for 2027-28 entry are £10,050 and are for the first year only." |
| Warwick | warwick.ac.uk/…/ugtuitionfees2017onwards/ | 2027-28 Home column: CS G400, Engineering H100, Economics L100, Management N200 all £10,050 |

New records: 7 `applicantCategory-uk-*-residency-home` ("Home (UK fee status)", which the app reads as the Home
tier), 7 source records, and 26 Home cost profiles. Each one copies its international profile (duration, fees, living
cost) and changes only tuition, year, category and source.

Manchester's Economics and Management course pages weren't read individually; Manchester's statement is per
course, and the CS, Mechanical Engineering and Alliance MBS pages all give £10,050.

## Nottingham international fees corrected (same 2027/28 table)

| Profile | Was | Official 2027/28 |
|---|---|---|
| Economics BSc (L100) | £26,800 | £27,600 |
| Business and Management BSc (N200) | £24,700 | £26,200 |
| Engineering BEng (Mechanical H302 / Civil H201 / EEE H603) | £33,000 | £33,500 |
| Computer Science BSc (G400) | £33,500 | £33,500 (unchanged; source re-pointed) |

The old notes called these "2027/28 proxy" figures; they no longer match the published table.
