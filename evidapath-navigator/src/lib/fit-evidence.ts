// EXPERIMENTAL (AI fit). Subject-level evidence the AI may use, beyond the costs,
// entry requirements, scholarships, deadlines and visa rules the site already has.
//
// Only professional accreditation from the accreditors' own official lists, read on
// 2026-11-10. Each item applies to the named programme(s) of one university.
// "school" scope = the accreditor covers the faculty/school that teaches it, not
// this exact degree title. Where we found no list we could read (Engineers
// Australia, Malaysia's EAC, EUR-ACE for Germany and the Netherlands, AACSB, BCS),
// there is no evidence here: missing evidence must never be read as a weakness.

export interface FitEvidence {
  id: string;
  uni: string;
  /** Our programme names (ProgramView.name) this applies to. */
  programs: string[];
  body: string;
  scope: "programme" | "school";
  statement: string;
  source: string;
  checked: string;
}

const CHECKED = "2026-11-10";
const abet = (kw: string) =>
  `https://amspub.abet.org/aps/name-search?searchType=institution&keyword=${encodeURIComponent(kw)}`;
const EQUIS =
  "https://www.efmdglobal.org/accreditations/business-schools/equis/equis-accredited-schools/";
const CEAB = "https://engineerscanada.ca/accreditation/accredited-programs/institution";
const engc = (courseId: number, q: string) =>
  `https://www.engc.org.uk/education-and-skills/find-your-course/course-search?page=1&q=${encodeURIComponent(q)}&s=all&courseId=${courseId}`;

type Row = Omit<FitEvidence, "checked">;

const ROWS: Row[] = [
  // ── ABET (US and UAE) ────────────────────────────────────────────────────
  {
    id: "abet-us-asu-cs",
    uni: "us-asu",
    programs: ["Computer Science"],
    body: "ABET",
    scope: "programme",
    statement: "ABET-accredited: Computer Science (BS), accredited since Oct 1992.",
    source: abet("Arizona State"),
  },
  {
    id: "abet-us-asu-eng",
    uni: "us-asu",
    programs: ["Engineering"],
    body: "ABET",
    scope: "programme",
    statement:
      "ABET-accredited: Engineering (BSE), plus Mechanical, Electrical, Civil, Aerospace and Chemical Engineering (BSE).",
    source: abet("Arizona State"),
  },
  {
    id: "abet-us-cornell-eng",
    uni: "us-cornell",
    programs: ["Engineering"],
    body: "ABET",
    scope: "school",
    statement:
      "ABET-accredited engineering programmes at Cornell include Mechanical, Electrical and Computer, Civil, Chemical and Biomedical Engineering (B.S.).",
    source: abet("Cornell"),
  },
  {
    id: "abet-us-harvard-eng",
    uni: "us-harvard",
    programs: ["Engineering"],
    body: "ABET",
    scope: "school",
    statement:
      "ABET-accredited at Harvard: Engineering Sciences, Mechanical Engineering and Electrical Engineering (Bachelor of Science).",
    source: abet("Harvard"),
  },
  {
    id: "abet-us-mit-eng",
    uni: "us-mit",
    programs: ["Engineering"],
    body: "ABET",
    scope: "school",
    statement:
      "ABET-accredited at MIT include Mechanical (Course 2), Aerospace (16), Chemical (10), Electrical Science and Engineering (6-1), Materials (3) and Nuclear (22) Engineering.",
    source: abet("Massachusetts Institute"),
  },
  {
    id: "abet-us-nyu-eng",
    uni: "us-nyu",
    programs: ["Engineering"],
    body: "ABET",
    scope: "school",
    statement:
      "ABET-accredited at NYU Tandon School of Engineering include Mechanical, Electrical, Civil, Computer and Chemical and Biomolecular Engineering (Bachelor of Science).",
    source: abet("New York University"),
  },
  {
    id: "abet-us-princeton-eng",
    uni: "us-princeton",
    programs: ["Engineering"],
    body: "ABET",
    scope: "school",
    statement:
      "ABET-accredited at Princeton: Mechanical, Electrical, Civil, Chemical and Aerospace Engineering (BSE).",
    source: abet("Princeton"),
  },
  {
    id: "abet-us-purdue-eng",
    uni: "us-purdue",
    programs: ["Engineering"],
    body: "ABET",
    scope: "school",
    statement:
      "ABET-accredited at Purdue (West Lafayette) include Mechanical, Electrical, Civil, Chemical, Computer, Industrial, Nuclear and Aeronautical and Astronautical Engineering.",
    source: abet("Purdue"),
  },
  {
    id: "abet-us-stanford-eng",
    uni: "us-stanford",
    programs: ["Engineering"],
    body: "ABET",
    scope: "school",
    statement:
      "ABET-accredited at Stanford: Civil Engineering (BS) and Mechanical Engineering (BS).",
    source: abet("Stanford"),
  },
  {
    id: "abet-us-upenn-cs",
    uni: "us-upenn",
    programs: ["Computer Science"],
    body: "ABET",
    scope: "programme",
    statement: "ABET-accredited: Computer Science (BSE), accredited since Oct 2004.",
    source: abet("Pennsylvania"),
  },
  {
    id: "abet-us-upenn-eng",
    uni: "us-upenn",
    programs: ["Engineering"],
    body: "ABET",
    scope: "school",
    statement:
      "ABET-accredited at Penn include Mechanical Engineering and Applied Mechanics, Electrical, Computer, and Chemical and Biomolecular Engineering (BSE).",
    source: abet("Pennsylvania"),
  },
  {
    id: "abet-us-usc-cs",
    uni: "us-usc",
    programs: ["Computer Science"],
    body: "ABET",
    scope: "programme",
    statement:
      "ABET-accredited: Computer Science (BS), and Computer Engineering and Computer Science (BS).",
    source: abet("Southern California"),
  },
  {
    id: "abet-us-usc-eng",
    uni: "us-usc",
    programs: ["Engineering"],
    body: "ABET",
    scope: "school",
    statement:
      "ABET-accredited at USC include Mechanical, Aerospace, Civil, Chemical, Electrical and Computer, and Industrial and Systems Engineering (BS).",
    source: abet("Southern California"),
  },
  {
    id: "abet-ae-aus-cs",
    uni: "ae-aus",
    programs: ["Computer Science"],
    body: "ABET",
    scope: "programme",
    statement:
      "ABET-accredited: Computer Science (Bachelor of Science), accredited since Oct 2004.",
    source: abet("Sharjah"),
  },
  {
    id: "abet-ae-aus-coe",
    uni: "ae-aus",
    programs: ["Computer Engineering"],
    body: "ABET",
    scope: "programme",
    statement:
      "ABET-accredited: Computer Engineering (Bachelor of Science), accredited since Oct 2004.",
    source: abet("Sharjah"),
  },
  {
    id: "abet-ae-sharjah-cs",
    uni: "ae-university-of-sharjah",
    programs: ["Computer Science"],
    body: "ABET",
    scope: "programme",
    statement:
      "ABET-accredited: Computer Science (Bachelor of Science), accredited since Oct 2014.",
    source: abet("Sharjah"),
  },
  {
    id: "abet-ae-sharjah-eng",
    uni: "ae-university-of-sharjah",
    programs: ["Engineering"],
    body: "ABET",
    scope: "school",
    statement:
      "ABET-accredited at the University of Sharjah include Mechanical, Electrical and Electronics, Civil, Computer, and Industrial Engineering and Engineering Management (Bachelor of Science).",
    source: abet("Sharjah"),
  },
  {
    id: "abet-ae-uaeu-cs",
    uni: "ae-uaeu",
    programs: ["Computer Science"],
    body: "ABET",
    scope: "programme",
    statement:
      "ABET-accredited: Computer Science (Bachelor of Science), accredited since Oct 2020.",
    source: abet("United Arab Emirates"),
  },
  {
    id: "abet-ae-uaeu-eng",
    uni: "ae-uaeu",
    programs: ["Engineering"],
    body: "ABET",
    scope: "school",
    statement:
      "ABET-accredited at UAEU include Mechanical, Electrical, Civil, Chemical, Computer, Communication and Petroleum Engineering (Bachelor of Science).",
    source: abet("United Arab Emirates"),
  },
  {
    id: "abet-ae-khalifa-eng",
    uni: "ae-khalifa",
    programs: ["Engineering"],
    body: "ABET",
    scope: "school",
    statement:
      "ABET-accredited at Khalifa University include Mechanical, Electrical, Civil, Chemical, Aerospace, Biomedical and Computer Engineering (Bachelor of Science).",
    source: abet("Khalifa"),
  },
  {
    id: "abet-ae-nyuad-eng",
    uni: "ae-nyu-abu-dhabi",
    programs: ["General Engineering"],
    body: "ABET",
    scope: "school",
    statement:
      "ABET lists Civil, Computer, Electrical and Mechanical Engineering (Abu Dhabi) (Bachelor of Science), accredited since May 2014 (listed under NYU Tandon School of Engineering).",
    source: abet("New York University"),
  },
  {
    id: "abet-ae-cud-cs",
    uni: "ae-canadian-university-dubai",
    programs: ["Computer Science"],
    body: "ABET",
    scope: "programme",
    statement:
      "ABET-accredited: Computer Science (Bachelor of Science), accredited since Oct 2024.",
    source: abet("Canadian University"),
  },
  {
    id: "abet-ae-zayed-it",
    uni: "ae-zayed",
    programs: ["Information Technology"],
    body: "ABET",
    scope: "programme",
    statement: "ABET-accredited: Information Technology (B.Sc.), accredited since Oct 2023.",
    source: abet("Zayed"),
  },

  // ── Engineers Canada (CEAB), list last updated 21 Oct 2025 ───────────────
  {
    id: "ceab-ca-mcgill-me",
    uni: "ca-mcgill",
    programs: ["Mechanical Engineering"],
    body: "Engineers Canada (CEAB)",
    scope: "programme",
    statement: "CEAB-accredited: Mechanical Engineering at McGill, accredited 1965 to present.",
    source: CEAB,
  },
  {
    id: "ceab-ca-mcmaster-eng",
    uni: "ca-mcmaster",
    programs: ["Engineering"],
    body: "Engineers Canada (CEAB)",
    scope: "school",
    statement:
      "CEAB-accredited at McMaster include Mechanical, Electrical, Civil, Chemical, Computer, Software and Mechatronics Engineering.",
    source: CEAB,
  },
  {
    id: "ceab-ca-ubc-eng",
    uni: "ca-ubc",
    programs: ["Engineering"],
    body: "Engineers Canada (CEAB)",
    scope: "school",
    statement:
      "CEAB-accredited at UBC include Mechanical, Electrical, Civil, Chemical, Computer, Engineering Physics and Manufacturing Engineering.",
    source: CEAB,
  },
  {
    id: "ceab-ca-waterloo-me",
    uni: "ca-waterloo",
    programs: ["Mechanical Engineering"],
    body: "Engineers Canada (CEAB)",
    scope: "programme",
    statement:
      "CEAB-accredited: Mechanical Engineering at the University of Waterloo (currently accredited).",
    source: CEAB,
  },
  {
    id: "ceab-ca-alberta-eng",
    uni: "ca-alberta",
    programs: ["Engineering"],
    body: "Engineers Canada (CEAB)",
    scope: "school",
    statement:
      "CEAB-accredited at the University of Alberta include Mechanical, Electrical, Civil, Chemical, Computer and Engineering Physics.",
    source: CEAB,
  },
  {
    id: "ceab-ca-toronto-eng",
    uni: "ca-university-of-toronto",
    programs: ["Engineering (Applied Science)"],
    body: "Engineers Canada (CEAB)",
    scope: "school",
    statement:
      "CEAB-accredited at the University of Toronto include Mechanical, Electrical, Civil, Chemical, Computer, Industrial and Engineering Science.",
    source: CEAB,
  },

  // ── Engineering Council (UK) course search ───────────────────────────────
  {
    id: "engc-uk-imperial-me",
    uni: "uk-imperial",
    programs: ["Mechanical Engineering"],
    body: "Engineering Council (UK)",
    scope: "programme",
    statement:
      "Mechanical Engineering MEng: CEng (Full), accredited by IMechE, Washington Accord, for intakes 09/1980 to 08/2027 (later intakes not yet listed).",
    source: engc(783, "Imperial College London Mechanical Engineering"),
  },
  {
    id: "engc-uk-ucl-me",
    uni: "uk-ucl",
    programs: ["Mechanical Engineering"],
    body: "Engineering Council (UK)",
    scope: "programme",
    statement:
      "Mechanical Engineering BEng(Hons): CEng (Requires Further Learning), accredited by IMechE, for intakes 09/2014 to 08/2028.",
    source: engc(8820, "UCL Mechanical Engineering"),
  },
  {
    id: "engc-uk-birmingham-me",
    uni: "uk-birmingham",
    programs: ["Mechanical Engineering"],
    body: "Engineering Council (UK)",
    scope: "programme",
    statement:
      "Mechanical Engineering BEng(Hons): CEng (Requires Further Learning), accredited by IMechE, Washington Accord, for intakes 09/1999 to 08/2029.",
    source: engc(119, "University of Birmingham Mechanical Engineering"),
  },
  {
    id: "engc-uk-nottingham-me",
    uni: "uk-nottingham",
    programs: ["Mechanical Engineering"],
    body: "Engineering Council (UK)",
    scope: "programme",
    statement:
      "Mechanical Engineering BEng(Hons): CEng (Requires Further Learning), accredited by IMechE, Washington Accord, for intakes 09/1999 to 08/2028.",
    source: engc(2084, "University of Nottingham Mechanical Engineering"),
  },
  {
    id: "engc-uk-manchester-me",
    uni: "uk-manchester",
    programs: ["Engineering (Mechanical)"],
    body: "Engineering Council (UK)",
    scope: "programme",
    statement:
      "Mechanical Engineering BEng(Hons): CEng (Requires Further Learning), accredited by IMechE, for intakes 09/2026 to 08/2030.",
    source: engc(4579, "University of Manchester Mechanical Engineering"),
  },
  {
    id: "engc-uk-warwick-eng",
    uni: "uk-warwick",
    programs: ["Engineering"],
    body: "Engineering Council (UK)",
    scope: "programme",
    statement:
      "Engineering BEng(Hons): CEng (Requires Further Learning), accredited by IET (intakes 09/2009 to 08/2029) and IMechE (09/2023 to 08/2028).",
    source: engc(2278, "University of Warwick Engineering"),
  },
  {
    id: "engc-uk-cambridge-eng",
    uni: "uk-cambridge",
    programs: ["Engineering"],
    body: "Engineering Council (UK)",
    scope: "programme",
    statement:
      "Engineering MEng(Hons): CEng (Full), accredited by IET and the civil engineering institutions, Washington Accord, for intakes up to 08/2032.",
    source: engc(2957, "Cambridge Engineering"),
  },
  {
    id: "engc-uk-oxford-eng",
    uni: "gb-university-of-oxford",
    programs: ["Engineering Science"],
    body: "Engineering Council (UK)",
    scope: "programme",
    statement:
      "Engineering Science MEng: CEng (Full), accredited by the civil engineering institutions and IChemE, Washington Accord, for intakes 09/2023 to 08/2028.",
    source: engc(1309, "University of Oxford Engineering Science"),
  },

  // ── EQUIS (business schools) ─────────────────────────────────────────────
  {
    id: "equis-au-unimelb",
    uni: "au-unimelb",
    programs: ["Commerce"],
    body: "EQUIS",
    scope: "school",
    statement:
      "EQUIS-accredited (5 years): Melbourne Business School and the Faculty of Business and Economics, University of Melbourne.",
    source: EQUIS,
  },
  {
    id: "equis-au-monash",
    uni: "au-monash",
    programs: ["Commerce"],
    body: "EQUIS",
    scope: "school",
    statement: "EQUIS-accredited (5 years): Monash Business School, Monash University.",
    source: EQUIS,
  },
  {
    id: "equis-au-unsw",
    uni: "au-unsw",
    programs: ["Commerce"],
    body: "EQUIS",
    scope: "school",
    statement: "EQUIS-accredited (5 years): UNSW Business School.",
    source: EQUIS,
  },
  {
    id: "equis-ca-mcgill",
    uni: "ca-mcgill",
    programs: ["Commerce (Desautels)"],
    body: "EQUIS",
    scope: "school",
    statement: "EQUIS-accredited (5 years): Desautels Faculty of Management, McGill University.",
    source: EQUIS,
  },
  {
    id: "equis-de-tum",
    uni: "de-tu-munich",
    programs: ["Management and Technology"],
    body: "EQUIS",
    scope: "school",
    statement:
      "EQUIS-accredited (5 years): TUM School of Management, Technische Universität München.",
    source: EQUIS,
  },
  {
    id: "equis-nl-uva",
    uni: "nl-uva",
    programs: ["Economics and Business Economics"],
    body: "EQUIS",
    scope: "school",
    statement:
      "EQUIS-accredited (5 years): Faculty of Economics and Business, University of Amsterdam.",
    source: EQUIS,
  },
  {
    id: "equis-ae-uaeu",
    uni: "ae-uaeu",
    programs: ["Business Administration", "Economics"],
    body: "EQUIS",
    scope: "school",
    statement:
      "EQUIS-accredited (3 years): College of Business and Economics, United Arab Emirates University.",
    source: EQUIS,
  },
  {
    id: "equis-uk-manchester",
    uni: "uk-manchester",
    programs: ["Management"],
    body: "EQUIS",
    scope: "school",
    statement: "EQUIS-accredited (5 years): Alliance Manchester Business School.",
    source: EQUIS,
  },
  {
    id: "equis-uk-birmingham",
    uni: "uk-birmingham",
    programs: ["Business Management"],
    body: "EQUIS",
    scope: "school",
    statement: "EQUIS-accredited (5 years): Birmingham Business School.",
    source: EQUIS,
  },
  {
    id: "equis-uk-nottingham",
    uni: "uk-nottingham",
    programs: ["Business"],
    body: "EQUIS",
    scope: "school",
    statement: "EQUIS-accredited (5 years): Nottingham University Business School.",
    source: EQUIS,
  },
  {
    id: "equis-uk-warwick",
    uni: "uk-warwick",
    programs: ["Business"],
    body: "EQUIS",
    scope: "school",
    statement: "EQUIS-accredited (5 years): Warwick Business School.",
    source: EQUIS,
  },
];

export const FIT_EVIDENCE: FitEvidence[] = ROWS.map((r) => ({ ...r, checked: CHECKED }));

export function evidenceFor(uniId: string, programName: string | undefined): FitEvidence[] {
  return FIT_EVIDENCE.filter(
    (e) => e.uni === uniId && (!programName || e.programs.includes(programName)),
  );
}
