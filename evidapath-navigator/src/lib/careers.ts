// Careers a degree can lead to, from the UK government's National Careers Service
// job profiles (nationalcareers.service.gov.uk), read on 2026-11-05.
//
// A job is listed under a subject only when its profile names that subject among
// the degrees that lead in ("degrees" below is the profile's own list). Salaries
// are the profile's UK "average salary" range, starter to experienced, in GBP.
// The one-line summaries are ours. These are typical paths, not promises.

export type CareerFamily = "computing" | "economics" | "business" | "engineering";

export interface Career {
  title: string;
  slug: string;
  summary: string;
  salaryGbp: readonly [number, number];
  /** Degree subjects the profile lists, as written there. */
  degrees: string;
  /** Extra condition from the profile, e.g. a master's often preferred. */
  note?: string;
  families: readonly CareerFamily[];
}

export const CAREERS_CHECKED = "2026-11-05";
export const CAREERS_SOURCE = "National Careers Service (UK government)";
export const careerUrl = (c: Career) =>
  `https://nationalcareers.service.gov.uk/job-profiles/${c.slug}`;

export const CAREERS: readonly Career[] = [
  {
    title: "Software developer",
    slug: "software-developer",
    summary: "Builds and tests the programs behind apps, services and devices.",
    salaryGbp: [30000, 75000],
    degrees:
      "computer science, information technology, software development, financial technology, software engineering, maths",
    note: "Graduate schemes at IT companies often take any degree subject.",
    families: ["computing"],
  },
  {
    title: "Data scientist",
    slug: "data-scientist",
    summary: "Uses software, AI and machine learning to make sense of large amounts of data.",
    salaryGbp: [32000, 83000],
    degrees: "maths, statistics, data science, computer science, operational research",
    families: ["computing"],
  },
  {
    title: "IT security co-ordinator",
    slug: "it-security-co-ordinator",
    summary: "Protects an organisation's systems and data from cyber attacks.",
    salaryGbp: [35000, 76000],
    degrees:
      "computer science, cyber security, software engineering, maths, business information systems",
    families: ["computing"],
  },
  {
    title: "Web developer",
    slug: "web-developer",
    summary: "Writes the code that creates and maintains websites and web apps.",
    salaryGbp: [27000, 60000],
    degrees:
      "web design and development, computer science, digital media development, software engineering",
    families: ["computing"],
  },
  {
    title: "Business analyst",
    slug: "business-analyst",
    summary: "Studies how a business works and finds ways to improve it.",
    salaryGbp: [23000, 55000],
    degrees:
      "business information systems, business management, computing and systems development, computer science",
    note: "Any degree that teaches analytical skills can be useful.",
    families: ["computing", "business"],
  },
  {
    title: "Economist",
    slug: "economist",
    summary: "Researches and advises on how money, markets and policy affect the economy.",
    salaryGbp: [28000, 60000],
    degrees:
      "economics, or a related subject like statistics, mathematics, business studies, finance and accounting",
    note: "Some employers prefer a master's in economics.",
    families: ["economics"],
  },
  {
    title: "Data analyst-statistician",
    slug: "data-analyst-statistician",
    summary: "Collects data to spot trends and build forecasts that guide decisions.",
    salaryGbp: [28000, 65000],
    degrees: "statistics, mathematics, economics, operational research, psychology",
    families: ["economics"],
  },
  {
    title: "Investment analyst",
    slug: "investment-analyst",
    summary: "Researches companies and markets to advise on where to invest.",
    salaryGbp: [28000, 75000],
    degrees: "economics, maths, business studies, accountancy, finance",
    note: "Usually a 2:1 degree or higher; most subjects are accepted.",
    families: ["economics", "business"],
  },
  {
    title: "Actuary",
    slug: "actuary",
    summary: "Uses maths and statistics to forecast long-term financial risks and costs.",
    salaryGbp: [32000, 70000],
    degrees:
      "maths and statistics, actuarial science, economics, engineering, accounting, physics or chemistry",
    note: "Most employers look for a degree with a lot of maths.",
    families: ["economics", "engineering"],
  },
  {
    title: "Management consultant",
    slug: "management-consultant",
    summary: "Advises organisations on how to solve problems and run better.",
    salaryGbp: [27000, 60000],
    degrees: "business studies, finance, maths, science, management",
    note: "An MBA may also help.",
    families: ["business"],
  },
  {
    title: "Marketing manager",
    slug: "marketing-manager",
    summary: "Plans how to promote products and brands, and runs the marketing team.",
    salaryGbp: [30000, 65000],
    degrees: "marketing, business management, digital marketing, advertising, psychology",
    note: "Graduates of any subject can become marketing managers.",
    families: ["business"],
  },
  {
    title: "Human resources officer",
    slug: "human-resources-officer",
    summary: "Hires, develops and looks after a company's employees.",
    salaryGbp: [24000, 40000],
    degrees: "any subject",
    families: ["business"],
  },
  {
    title: "Mechanical engineer",
    slug: "mechanical-engineer",
    summary: "Designs and develops machines, from engines to medical devices.",
    salaryGbp: [28000, 60000],
    degrees:
      "mechanical engineering, electromechanical engineering, mechatronics engineering, manufacturing",
    families: ["engineering"],
  },
  {
    title: "Electrical engineer",
    slug: "electrical-engineer",
    summary: "Designs and maintains electrical systems, from power networks to buildings.",
    salaryGbp: [27000, 58000],
    degrees:
      "electrical or electronic engineering; also electromechanical engineering, building services engineering, applied physics, aeronautical engineering, mechatronics",
    families: ["engineering"],
  },
  {
    title: "Electronics engineer",
    slug: "electronics-engineer",
    summary: "Designs electronic parts and systems, such as circuits and devices.",
    salaryGbp: [28000, 60000],
    degrees:
      "electronic engineering; related subjects like electronic and electrical engineering, aerospace engineering, physics, computer science",
    families: ["engineering", "computing"],
  },
  {
    title: "Aerospace engineer",
    slug: "aerospace-engineer",
    summary: "Designs, tests and maintains aircraft, spacecraft and satellites.",
    salaryGbp: [30000, 70000],
    degrees:
      "aerospace engineering, avionics, electrical or electronic engineering, mechanical engineering, physics, software engineering, mathematics",
    families: ["engineering"],
  },
  {
    title: "Robotics engineer",
    slug: "robotics-engineer",
    summary: "Builds machines that do automated jobs in factories, healthcare and more.",
    salaryGbp: [31000, 60000],
    degrees:
      "AI and robotics, mechatronics, robotics engineering, mechanical or electronics engineering, computer science, mathematics",
    families: ["engineering", "computing"],
  },
];

export const FAMILY_LABEL: Record<CareerFamily, string> = {
  computing: "Computer Science",
  economics: "Economics",
  business: "Business",
  engineering: "Engineering",
};

/** Which career family a programme belongs to, from its field and name. */
export function careerFamily(field: string, name = ""): CareerFamily | null {
  const t = `${field} ${name}`.toLowerCase();
  if (/engineer/.test(t)) return "engineering";
  // Before computing: "Economics, Finance and Data Science" is an economics degree.
  if (/econom/.test(t)) return "economics";
  if (/comput|informat|software|data/.test(t)) return "computing";
  if (/business|commerce|management|finance|accounting|marketing/.test(t)) return "business";
  return null;
}

export function careersFor(family: CareerFamily | null): Career[] {
  return family ? CAREERS.filter((c) => c.families.includes(family)) : [];
}
