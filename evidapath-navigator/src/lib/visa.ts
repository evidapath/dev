// Student visa money, work rules while studying, and staying to work after
// graduating, per country. Every figure was read on the government page in
// `sources` on 2026-11-05. Where a government site blocks automated reading
// (US, Australia) or doesn't publish the figure clearly (Malaysia, UAE), only
// the official links are given, never a guessed number.

export interface VisaFact {
  label: string;
  value: string;
}

export interface VisaInfo {
  country: string;
  visa: string;
  /** Money and fees, as the government states them. */
  money: VisaFact[];
  work?: string;
  after?: string;
  /** Extra caveat shown under the facts. */
  note?: string;
  sources: { label: string; url: string }[];
}

export const VISA_CHECKED = "2026-11-05";

export const VISAS: Record<string, VisaInfo> = {
  "United Kingdom": {
    country: "United Kingdom",
    visa: "Student visa",
    money: [
      { label: "Visa fee", value: "£558 (applying from outside the UK)" },
      { label: "Healthcare surcharge", value: "£776 a year of the visa" },
      {
        label: "Money to show for living costs",
        value: "£1,529 a month in London or £1,171 a month elsewhere, for up to 9 months",
      },
      { label: "Plus", value: "your first year's course fees (shown on your CAS)" },
    ],
    work: "Up to 20 hours a week in term time on a degree course at a university with a track record of compliance; full-time outside term.",
    after:
      "Graduate visa: 18 months if you apply on or after 1 January 2027 (2 years if you apply by 31 December 2026). Fee £937 plus the £1,035-a-year healthcare surcharge.",
    sources: [
      { label: "Student visa (GOV.UK)", url: "https://www.gov.uk/student-visa" },
      { label: "Money you need (GOV.UK)", url: "https://www.gov.uk/student-visa/money" },
      {
        label: "Healthcare surcharge (GOV.UK)",
        url: "https://www.gov.uk/healthcare-immigration-application/how-much-pay",
      },
      {
        label: "Work rules: Appendix Student (GOV.UK)",
        url: "https://www.gov.uk/guidance/immigration-rules/immigration-rules-appendix-student",
      },
      { label: "Graduate visa (GOV.UK)", url: "https://www.gov.uk/graduate-visa" },
    ],
  },
  Canada: {
    country: "Canada",
    visa: "Study permit",
    money: [
      { label: "Study permit fee", value: "CAD 150" },
      {
        label: "Money to show for living costs",
        value: "CAD 23,448 a year for one student (applications from 1 September 2026)",
      },
      { label: "Plus", value: "your first year's tuition and travel" },
    ],
    work: "Up to 24 hours a week off campus during term, if your study permit allows it.",
    after: "Post-graduation work permit: up to 3 years if your programme lasted 2 years or more.",
    note: "Quebec sets its own living-cost amount (this matters for McGill).",
    sources: [
      {
        label: "Proof of financial support (IRCC)",
        url: "https://www.canada.ca/en/immigration-refugees-citizenship/services/study-canada/study-permit/get-documents/financial-support.html",
      },
      { label: "Fees (IRCC)", url: "https://ircc.canada.ca/english/information/fees/fees.asp" },
      {
        label: "Work off campus (IRCC)",
        url: "https://www.canada.ca/en/immigration-refugees-citizenship/services/study-canada/work/work-off-campus.html",
      },
      {
        label: "Post-graduation work permit (IRCC)",
        url: "https://www.canada.ca/en/immigration-refugees-citizenship/services/study-canada/work/after-graduation/about.html",
      },
    ],
  },
  Germany: {
    country: "Germany",
    visa: "Visa for studying, then a residence permit",
    money: [
      { label: "Visa fee", value: "€75 (paid in local currency)" },
      { label: "Residence permit in Germany", value: "up to €100" },
      {
        label: "Money to show",
        value:
          "a blocked account with at least €11,904 (2026), a scholarship, or a declaration of commitment",
      },
    ],
    work: "Up to 140 working days a year.",
    after: "A residence permit of up to 18 months to look for a job after graduating in Germany.",
    sources: [
      {
        label: "At a glance: visa for studying (Make it in Germany, Jan 2026)",
        url: "https://www.make-it-in-germany.com/fileadmin/1_Rebrush_2022/a_Fachkraefte/PDF-Dateien/3_Visum_u_Aufenthalt/Visagrafik_EN/Visum_Studieren_EN.pdf",
      },
      {
        label: "Work rule (BAMF)",
        url: "https://www.bamf.de/SharedDocs/Anlagen/EN/MigrationAufenthalt/selbstverpflichtung-deckung-lebensunterhalt.pdf?__blob=publicationFile&v=2",
      },
      {
        label: "Job search after study: Residence Act §20",
        url: "https://www.gesetze-im-internet.de/aufenthg_2004/__20.html",
      },
    ],
  },
  Netherlands: {
    country: "Netherlands",
    visa: "Residence permit for study",
    money: [
      { label: "Residence permit fee", value: "€254" },
      { label: "Money to show", value: "€1,130.77 a month (university, 2026)" },
    ],
    work: "Up to 16 hours a week, or full-time only in the summer months, with a work permit from UWV.",
    after: "Orientation year: a 1-year permit to look for work after graduating (€254).",
    sources: [
      { label: "Fees (IND)", url: "https://ind.nl/en/fees-costs-of-an-application" },
      {
        label: "Required amounts (IND)",
        url: "https://ind.nl/en/required-amounts-income-requirements",
      },
      {
        label: "International students and the IND",
        url: "https://ind.nl/en/about-us/background-articles/international-students-and-the-ind",
      },
      {
        label: "Orientation year (IND)",
        url: "https://ind.nl/en/residence-permits/work/residence-permit-for-orientation-year",
      },
    ],
  },
  "United States": {
    country: "United States",
    visa: "F-1 student visa",
    money: [],
    note: "US government sites don't allow us to read them automatically, so we don't show figures here. Check the visa fee, SEVIS fee, work rules and OPT on the official pages.",
    sources: [
      {
        label: "Student visa (U.S. Department of State)",
        url: "https://travel.state.gov/content/travel/en/us-visas/study/student-visa.html",
      },
      { label: "Study in the States (DHS)", url: "https://studyinthestates.dhs.gov/" },
    ],
  },
  Australia: {
    country: "Australia",
    visa: "Student visa (subclass 500)",
    money: [],
    note: "The Department of Home Affairs site doesn't allow us to read it automatically, so we don't show figures here. Check the fee, money to show, work limit and the Temporary Graduate visa (subclass 485) on the official pages.",
    sources: [
      {
        label: "Student visa 500 (Home Affairs)",
        url: "https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/student-500",
      },
      {
        label: "Study Australia (Australian Government)",
        url: "https://www.studyaustralia.gov.au/en/plan-your-move/your-guide-to-visas",
      },
    ],
  },
  Malaysia: {
    country: "Malaysia",
    visa: "Student Pass (through EMGS)",
    money: [],
    note: "We haven't confirmed Malaysia's student pass fees and work rules yet. Check with EMGS and your university.",
    sources: [
      { label: "Education Malaysia Global Services", url: "https://educationmalaysia.gov.my/" },
    ],
  },
  "United Arab Emirates": {
    country: "United Arab Emirates",
    visa: "Student residence visa",
    money: [],
    note: "We haven't confirmed UAE student visa costs and work rules yet. Ask your university's admissions office, and check the UAE's official portal.",
    sources: [{ label: "UAE official portal (u.ae)", url: "https://u.ae/en" }],
  },
  Italy: {
    country: "Italy",
    visa: "Study visa, applied for through Universitaly",
    money: [],
    note: "We haven't confirmed Italy's visa fees, money to show and work rules yet. Politecnico di Milano says non-EU applicants living abroad apply for the study visa through the Universitaly portal; check the Foreign Ministry's visa site too.",
    sources: [
      {
        label: "Universitaly (Italian Ministry of University)",
        url: "https://www.universitaly.it/",
      },
      {
        label: "Il visto per l'Italia (Ministry of Foreign Affairs)",
        url: "https://vistoperitalia.esteri.it/",
      },
    ],
  },
  Türkiye: {
    country: "Türkiye",
    visa: "Student residence permit (e-ikamet)",
    money: [],
    note: "We haven't confirmed Türkiye's visa fees, money to show and work rules yet. METU says students complete the online student residence permit application at e-ikamet.goc.gov.tr and hand their documents to its International Students Office.",
    sources: [
      {
        label: "Residence permit (METU International Students Office)",
        url: "https://iso.metu.edu.tr/en/residence-permit",
      },
    ],
  },
  "South Korea": {
    country: "South Korea",
    visa: "Student visa D-2-2 (undergraduate study)",
    money: [],
    note: "We haven't confirmed Korea's visa fees and work rules yet. KAIST's 2027 guide says proof of funds of KRW 16,000,000 is generally required for the visa, but because of the KAIST Scholarship its applicants show about USD 3,200.",
    sources: [
      { label: "Korea Visa Portal (Ministry of Justice)", url: "https://www.visa.go.kr/" },
      { label: "Study in Korea (Korean Government)", url: "https://www.studyinkorea.go.kr/" },
    ],
  },
  Hungary: {
    country: "Hungary",
    visa: "Residence permit for study purposes",
    money: [],
    note: "We haven't confirmed Hungary's visa fees, money to show and work rules yet. BME says students need a residence permit after arriving, and its mentors help book the appointment.",
    sources: [
      {
        label: "National Directorate-General for Aliens Policing (OIF)",
        url: "https://oif.gov.hu/",
      },
    ],
  },
  "Hong Kong": {
    country: "Hong Kong",
    visa: "Student visa / entry permit",
    money: [],
    note: "We haven't confirmed Hong Kong's student visa fees, money to show and work rules yet. Check the Immigration Department's page for students.",
    sources: [
      {
        label: "Students (Hong Kong Immigration Department)",
        url: "https://www.immd.gov.hk/eng/services/visas/study.html",
      },
    ],
  },
};

export function visaFor(country: string): VisaInfo | null {
  return VISAS[country] ?? null;
}
