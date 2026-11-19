# Courses still to do (list kept 2026-11-19)

Everything below comes from the batch notes in `README.md` in this folder; see there for the
quotes and page details. Grouped by what has to happen before a programme can go in.

## 1. Not attempted yet (start here)

| University | What to do |
|---|---|
| Cambridge | More courses. First settle the College fee rule (README "Found on the way": Darwin vs Queens'). |
| Taylor's University | Course pages saved, but layout irregular; build a generator. Its USD course totals vs MYR 2027 schedule need one rule. |
| HCT (Higher Colleges of Technology) | Find course pages, fees, entry rules for international students. |
| Khalifa University | Same. |
| Zayed University | Psychology and Architecture were tried: only a 2018 study plan and older catalogues with conflicting credit totals. Need a current page. |
| UAE University | Same as HCT. Medicine held (UAE nationals only). |
| RIT Dubai | Same as HCT. Engineering sequences run to a "Fifth Year": check length. |
| Canadian University Dubai | Same as HCT. Decide VAT-inclusive vs pre-VAT fee (records differ today). |
| University of Birmingham Dubai | Same as HCT. |
| German universities (e.g. TUM) | Most bachelor's are taught in German; find English-taught ones only. |

## 2. Blocked by bot checks (re-try later; never bypass)

- Oxford, Melbourne, Monash (Clayton), Monash Malaysia, UCL: Cloudflare check.
- Alberta: CloudFront "Request blocked" (403).
- Princeton: ua.princeton.edu shows a Cloudflare check; the admission page doesn't say A.B. or B.S.E.
  per concentration.

## 3. Read but held (need a source fact or a builder change)

| University | Programme(s) | What is missing |
|---|---|---|
| McMaster | Chemical & Physical Sciences, Life Sciences, Maths & Stats Gateways, Humanities I | Programme length not stated on any page read. Requirements and fees already saved (`mcm-req-*`, `mcm-cost-*`). Health Sciences also needs a supplementary application. |
| TU Delft | Earth, Climate and Technology; Nanobiology | Fee written "€ 20.563" (dot thousands). Needs a safe builder option for that format (`gen/nl_delft.py`). |
| McGill | Mathematics, Physics | Pages don't name the admission group, so the grade range can't be assigned. |
| NYU Abu Dhabi | Psychology | Conflict: NYU Bulletin says BS, NYUAD says BA. |
| Universiti Malaya | Law | No international fee or IB line. |
| Universiti Malaya | Mathematics, Pharmacy, Accounting, Dentistry, International & Strategic Studies | Page addresses tried return 404; find the right URLs. |
| Melbourne | Majors | Fee is a range by subjects chosen (also blocked now). |
| Manchester | Dentistry | Clinical-year fee for a 2027 starter not published. |
| Warwick | English Literature | Fee table row looks wrong (2027-28 lower than 2026-27). |
| Warwick | PPE, Pharmacy | Guessed addresses 404; find the right URLs. |
| Birmingham | Biological Sciences, Psychology | International fee "To be confirmed". |
| Nottingham Malaysia | Pharmacy | Two currencies (Malaysia + UK years); one cost record holds one currency. |
| UBC | English | General IB line not shown on its page. |
| USC | Neuroscience; Psychology | No official degree page found. |
| ASU | English | Online only. |
| Twente | Dutch-taught programmes | Not for international students in English. |
| Cornell, USC | Architecture | 5-year degrees with portfolio rules. |
| UAE University, Sharjah | Medicine | Limited by nationality; site can't filter by nationality yet. |

## 4. Existing records "to check"

See the "Found on the way" list in `README.md` (Twente TOEFL, UM Computer Science length, McGill
3 vs 4 years, Waterloo AFM and Engineering fees, AUS compulsory fees, Taylor's Mechanical fee,
Cambridge College fee, UM SST, Twente "Engineering" search result).
