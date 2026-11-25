# Courses still to do (list kept 2026-11-19)

Everything below comes from the batch notes in `README.md` in this folder; see there for the
quotes and page details. Grouped by what has to happen before a programme can go in.

## 1. Not attempted yet (start here)

| University | What to do |
|---|---|
| Cambridge | More courses. First settle the College fee rule (README "Found on the way": Darwin vs Queens'). |
| HCT (Higher Colleges of Technology) | 12 done 2026-11-25. Held: Cybersecurity and Data Science (programme pages link to catalogue entries named Information Technology / Information Systems). Not attempted: Education, Health Information Management, Medical Laboratory, Emergency Medical Services, Pharmacy, Midwifery, Social Work, Veterinary Science, Logistics, Aviation, Marine, Tourism, HRM, Finance-adjacent, Quality, Innovation. Teaching language not stated anywhere read. |
| Khalifa University | 11 BSc done 2026-11-25 (every programme on its undergraduate list). Not attempted: Cell and Molecular Biology, Earth and Planetary Sciences, Computer Engineering (named in the admissions table, not on the programme list page). |
| Zayed University | Still held (re-checked 2026-11-25): ZU's college pages link no undergraduate programme pages with credit totals or length; the fee page gives only AED 2,500 per credit hour. |
| UAE University | Fee table read 2026-11-25 (saved `65949822798d`, 2026/2027 onwards, credits and totals per programme). Held: programme length (model study-plan PDFs; download refused by the permission system), so no yearly averages. Medicine held (UAE nationals only). |
| RIT Dubai | 7 done 2026-11-25 (engineering and Cybersecurity 5 years: sequences run to a "Fifth Year"). Held: Advertising and Public Relations (no admission-requirements PDF), Management Information Systems (not on the tuition list). |
| Canadian University Dubai | 11 done 2026-11-25 (VAT-inclusive, as the 17 Nov fixes). Held: three Communication programmes (no row on CUD's fee page). Not attempted: engineering branches, Architecture, Interior Design, Design and AI (programme list loads by script). To check: two existing "Psychology" programme records. |
| University of Birmingham Dubai | 13 done 2026-11-25. Held: Civil and Electronic/Electrical Engineering (years 2-3 in Birmingham UK). Not attempted: foundation-year, placement and MEng variants. To check: existing Birmingham Dubai records use the visible 'Fees (UK/Ireland)' box; the page data's international fee matched it on every page read. |
| German universities (e.g. TUM) | Checked 2026-11-25. TUM Management and Data Science and Information Engineering (Heilbronn): pages say "The language of instruction for this program is English", 6 semesters, 180 credits, but give no fee; TUM's tuition page says non-EU bachelor's fees from WS 2027/28 are "2,300 euros or 3,400 euros" by programme, so the band is unknown: held. Sustainable Engineering (Straubing): language not confirmed. Aerospace already in. No English-taught bachelor's leads found for KIT, RWTH, LMU, Heidelberg, TU Berlin. |

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
