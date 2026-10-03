// ───────────────────────────────────────────────────────────────────────────
// EvidaPath illustrative dataset
//
// IMPORTANT: This file contains ILLUSTRATIVE / DEMO content only. None of the
// figures, thresholds, costs, scores, verification labels, or institutional
// assertions below are sourced from verified live data. They exist solely to
// demonstrate the EvidaPath product interface and decision model during the
// platform's build phase.
//
// Live analysis will replace these placeholders with verified EvidaPath data,
// source attribution, and verification dates as datasets are added.
// ───────────────────────────────────────────────────────────────────────────

export interface University {
  id: string;
  name: string;
  shortName: string;
  country: string;
  city: string;
  flag: string;
  type: string;
  programs: string[];
  durationYears: number;
  academicRequirements: {
    system: string;
    target: string;
    prerequisites: string[];
  };
  costs: {
    tuitionPerYear: number | null;
    livingPerYear: number | null;
    mandatoryFees: number | null;
    currency: string;
    totalAnnual: number | null;
    totalDegree: number | null;
  };
  affordabilityIndex: {
    score: number | null;
    category: string;
    notes: string;
  };
  scholarshipsAvailable: number | null;
  scholarshipCoverageMax: number | null;
  // When a university prices by residency (e.g. EU vs non-EU), the displayed cost is
  // the international (non-EU) rate and this note discloses the other tier. Null when
  // a single uniform cost applies. Prevents silently showing one tier as universal.
  costResidencyNote?: string;
  evidenceConfidence: string;
  lastVerified: string;
  officialSourceUrl: string;
  alternativePathways: string[];
  admissionsEvidence: {
    historicalBenchmark: string;
    admitProfileDetail: string;
    uncertaintyNote: string;
  };
}

export interface Scholarship {
  id: string;
  name: string;
  provider: string;
  universitiesCovered: string;
  citizenshipEligible: string;
  countriesOfStudy: string[];
  academicThreshold: string;
  awardValue: number | null;
  // Human-readable award as sourced (percentages, income-banded tables, text).
  // Preferred for display when present; awardValue stays null for non-numeric awards.
  awardSummary?: string;
  awardFrequency: string;
  deadline: string;
  verificationStatus: string;
  lastChecked: string;
  officialSource: string;
  eligibilitySummary: string;
  renewalCriteria: string;
}

export interface IntelligenceArticle {
  slug: string;
  title: string;
  category:
    | "Admissions Intelligence"
    | "Affordability"
    | "Scholarships & Funding"
    | "Global University Markets"
    | "Outcomes & ROI"
    | "Data Briefs";
  readTime: string;
  date: string;
  lead: string;
  keyTakeaway: string;
  dataSummary: string;
  featured?: boolean;
}

// Helper: neutral placeholder for any numeric cost field that has no verified source.
const PENDING = "Pending verified data";

export const UNIVERSITIES_DATA: University[] = [
  {
    id: "oxford-univ",
    name: "University of Oxford",
    shortName: "Oxford",
    country: "United Kingdom",
    city: "Oxford",
    flag: "🇬🇧",
    type: "Collegiate Research University",
    programs: [
      "Philosophy, Politics and Economics (PPE)",
      "Computer Science",
      "Engineering Science",
      "Law",
    ],
    durationYears: 3,
    academicRequirements: {
      system: "A-Levels / IB",
      target: PENDING,
      prerequisites: [
        "Subject-specific admissions tests",
        "Written work submission",
        "Academic interviews",
      ],
    },
    costs: {
      tuitionPerYear: null,
      livingPerYear: null,
      mandatoryFees: null,
      currency: "GBP",
      totalAnnual: null,
      totalDegree: null,
    },
    affordabilityIndex: {
      score: null,
      category: "Pending verified data",
      notes:
        "Affordability index will be calculated once verified tuition, living-cost, and duration data are connected.",
    },
    scholarshipsAvailable: null,
    scholarshipCoverageMax: null,
    evidenceConfidence: "Pending verified data",
    lastVerified: "Not yet verified",
    officialSourceUrl: "https://ox.ac.uk",
    alternativePathways: [
      "Warwick University (Economics/PPE)",
      "UCL (Arts & Sciences / Philosophy)",
      "University of Edinburgh",
    ],
    admissionsEvidence: {
      historicalBenchmark: PENDING,
      admitProfileDetail:
        "Admissions evidence will be displayed here once verified institutional benchmarks are connected.",
      uncertaintyNote:
        "Subject quotas and qualitative college tutorials make single-metric prediction unfeasible. Uncertainty will be communicated explicitly.",
    },
  },
  {
    id: "uoft-canada",
    name: "University of Toronto",
    shortName: "U of T",
    country: "Canada",
    city: "Toronto",
    flag: "🇨🇦",
    type: "Public Research University",
    programs: [
      "Computer Science",
      "Rotman Commerce",
      "Life Sciences",
      "Faculty of Applied Science & Engineering",
    ],
    durationYears: 4,
    academicRequirements: {
      system: "High School / IB / A-Levels",
      target: PENDING,
      prerequisites: [
        "Calculus & Advanced Functions",
        "English Grade 12 or equivalent",
        "Online supplementary profile",
      ],
    },
    costs: {
      tuitionPerYear: null,
      livingPerYear: null,
      mandatoryFees: null,
      currency: "CAD",
      totalAnnual: null,
      totalDegree: null,
    },
    affordabilityIndex: {
      score: null,
      category: "Pending verified data",
      notes:
        "Affordability index will be calculated once verified tuition, living-cost, and duration data are connected.",
    },
    scholarshipsAvailable: null,
    scholarshipCoverageMax: null,
    evidenceConfidence: "Pending verified data",
    lastVerified: "Not yet verified",
    officialSourceUrl: "https://utoronto.ca",
    alternativePathways: [
      "University of Waterloo (Co-op CS)",
      "McGill University (Montreal)",
      "McMaster Health Sciences",
    ],
    admissionsEvidence: {
      historicalBenchmark: PENDING,
      admitProfileDetail:
        "Admissions evidence will be displayed here once verified institutional benchmarks are connected.",
      uncertaintyNote:
        "Program-specific cutoffs and post-Year-1 subject requirements introduce variability that will be modelled explicitly.",
    },
  },
  {
    id: "tum-germany",
    name: "Technical University of Munich (TUM)",
    shortName: "TUM",
    country: "Germany",
    city: "Munich",
    flag: "🇩🇪",
    type: "Excellence University",
    programs: [
      "Management & Technology (English)",
      "Informatics",
      "Aerospace Engineering",
      "Data Science",
    ],
    durationYears: 3,
    academicRequirements: {
      system: "Abitur / IB / Recognized Diploma",
      target: PENDING,
      prerequisites: [
        "Strong mathematics/science background",
        "Aptitude assessment for selected programs",
      ],
    },
    costs: {
      tuitionPerYear: null,
      livingPerYear: null,
      mandatoryFees: null,
      currency: "EUR",
      totalAnnual: null,
      totalDegree: null,
    },
    affordabilityIndex: {
      score: null,
      category: "Pending verified data",
      notes:
        "Affordability index will be calculated once verified tuition, living-cost, and duration data are connected.",
    },
    scholarshipsAvailable: null,
    scholarshipCoverageMax: null,
    evidenceConfidence: "Pending verified data",
    lastVerified: "Not yet verified",
    officialSourceUrl: "https://tum.de",
    alternativePathways: [
      "RWTH Aachen",
      "TU Delft (Netherlands)",
      "Karlsruhe Institute of Technology (KIT)",
    ],
    admissionsEvidence: {
      historicalBenchmark: PENDING,
      admitProfileDetail:
        "Admissions evidence will be displayed here once verified institutional benchmarks are connected.",
      uncertaintyNote:
        "Diploma equivalency verification (via Uni-Assist / Anabin) is a key variable that will be surfaced explicitly.",
    },
  },
  {
    id: "nus-singapore",
    name: "National University of Singapore (NUS)",
    shortName: "NUS",
    country: "Singapore",
    city: "Singapore",
    flag: "🇸🇬",
    type: "National Research University",
    programs: [
      "Computer Science",
      "Business Administration",
      "Biomedical Engineering",
      "Quantitative Finance",
    ],
    durationYears: 4,
    academicRequirements: {
      system: "A-Levels / IB / SAT / National High School",
      target: PENDING,
      prerequisites: ["Advanced mathematics", "English proficiency", "Faculty-specific interviews"],
    },
    costs: {
      tuitionPerYear: null,
      livingPerYear: null,
      mandatoryFees: null,
      currency: "SGD",
      totalAnnual: null,
      totalDegree: null,
    },
    affordabilityIndex: {
      score: null,
      category: "Pending verified data",
      notes:
        "Affordability index will be calculated once verified tuition, living-cost, and duration data are connected.",
    },
    scholarshipsAvailable: null,
    scholarshipCoverageMax: null,
    evidenceConfidence: "Pending verified data",
    lastVerified: "Not yet verified",
    officialSourceUrl: "https://nus.edu.sg",
    alternativePathways: [
      "Nanyang Technological University (NTU)",
      "SMU (Singapore Management University)",
      "HKUST (Hong Kong)",
    ],
    admissionsEvidence: {
      historicalBenchmark: PENDING,
      admitProfileDetail:
        "Admissions evidence will be displayed here once verified institutional benchmarks are connected.",
      uncertaintyNote:
        "International applicant quotas and tuition-grant conditions introduce variables that will be modelled explicitly.",
    },
  },
  {
    id: "nyu-ad",
    name: "New York University Abu Dhabi",
    shortName: "NYU Abu Dhabi",
    country: "United Arab Emirates",
    city: "Abu Dhabi",
    flag: "🇦🇪",
    type: "Liberal Arts & Science University",
    programs: ["Economics", "Computer Science", "Political Science", "Mechanical Engineering"],
    durationYears: 4,
    academicRequirements: {
      system: "Holistic / IB / AP / National",
      target: PENDING,
      prerequisites: [
        "Standardized test flexible",
        "Leadership and global curiosity evidence",
        "Candidate Weekend invitation",
      ],
    },
    costs: {
      tuitionPerYear: null,
      livingPerYear: null,
      mandatoryFees: null,
      currency: "USD",
      totalAnnual: null,
      totalDegree: null,
    },
    affordabilityIndex: {
      score: null,
      category: "Pending verified data",
      notes:
        "Affordability index will be calculated once verified tuition, living-cost, and aid data are connected.",
    },
    scholarshipsAvailable: null,
    scholarshipCoverageMax: null,
    evidenceConfidence: "Pending verified data",
    lastVerified: "Not yet verified",
    officialSourceUrl: "https://nyuad.nyu.edu",
    alternativePathways: [
      "NYU New York / Shanghai",
      "Georgetown University Qatar",
      "Carnegie Mellon University Qatar",
    ],
    admissionsEvidence: {
      historicalBenchmark: PENDING,
      admitProfileDetail:
        "Admissions evidence will be displayed here once verified institutional benchmarks are connected.",
      uncertaintyNote:
        "Holistic review and need-based aid documentation introduce variability that will be communicated explicitly.",
    },
  },
  {
    id: "delft-netherlands",
    name: "Delft University of Technology (TU Delft)",
    shortName: "TU Delft",
    country: "Netherlands",
    city: "Delft",
    flag: "🇳🇱",
    type: "Public Polytechnic University",
    programs: [
      "Aerospace Engineering (BSc English)",
      "Computer Science & Engineering (BSc English)",
      "Applied Physics",
    ],
    durationYears: 3,
    academicRequirements: {
      system: "VWO equivalent / IB / A-Levels",
      target: PENDING,
      prerequisites: ["Numerus Fixus selection procedure (selected programs)", "Calculus mastery"],
    },
    costs: {
      tuitionPerYear: null,
      livingPerYear: null,
      mandatoryFees: null,
      currency: "EUR",
      totalAnnual: null,
      totalDegree: null,
    },
    affordabilityIndex: {
      score: null,
      category: "Pending verified data",
      notes:
        "Affordability index will be calculated once verified tuition, living-cost, and duration data are connected.",
    },
    scholarshipsAvailable: null,
    scholarshipCoverageMax: null,
    evidenceConfidence: "Pending verified data",
    lastVerified: "Not yet verified",
    officialSourceUrl: "https://tudelft.nl",
    alternativePathways: [
      "Eindhoven University of Technology (TU/e)",
      "University of Twente",
      "KU Leuven (Belgium)",
    ],
    admissionsEvidence: {
      historicalBenchmark: PENDING,
      admitProfileDetail:
        "Admissions evidence will be displayed here once verified institutional benchmarks are connected.",
      uncertaintyNote:
        "Numerus Fixus selection tests and housing constraints introduce variables that will be surfaced explicitly.",
    },
  },
];

export const SCHOLARSHIPS_DATA: Scholarship[] = [
  {
    id: "pearson-intl",
    name: "Lester B. Pearson International Scholarship",
    provider: "University of Toronto",
    universitiesCovered: "University of Toronto (All campuses)",
    citizenshipEligible: "International (Non-Canadian)",
    countriesOfStudy: ["Canada"],
    academicThreshold: "Pending verified criteria",
    awardValue: null,
    awardFrequency: "Pending verified data",
    deadline: "Pending verified data",
    verificationStatus: "Pending verification",
    lastChecked: "Not yet verified",
    officialSource: "future.utoronto.ca/pearson",
    eligibilitySummary:
      "Scholarship eligibility will be evaluated against verified program criteria once the funding record is sourced and verified.",
    renewalCriteria: "Pending verified data",
  },
  {
    id: "daad-germany",
    name: "DAAD International Undergraduate Study Grant",
    provider: "German Academic Exchange Service (DAAD)",
    universitiesCovered: "Recognized German public research universities",
    citizenshipEligible: "Global / Non-German nationals",
    countriesOfStudy: ["Germany"],
    academicThreshold: "Pending verified criteria",
    awardValue: null,
    awardFrequency: "Pending verified data",
    deadline: "Pending verified data",
    verificationStatus: "Pending verification",
    lastChecked: "Not yet verified",
    officialSource: "daad.de/scholarships",
    eligibilitySummary:
      "Scholarship eligibility will be evaluated against verified program criteria once the funding record is sourced and verified.",
    renewalCriteria: "Pending verified data",
  },
  {
    id: "reach-oxford",
    name: "Reach Oxford Scholarship",
    provider: "University of Oxford",
    universitiesCovered: "University of Oxford",
    citizenshipEligible: "Eligibility list pending verification",
    countriesOfStudy: ["United Kingdom"],
    academicThreshold: "Pending verified criteria",
    awardValue: null,
    awardFrequency: "Pending verified data",
    deadline: "Pending verified data",
    verificationStatus: "Pending verification",
    lastChecked: "Not yet verified",
    officialSource: "ox.ac.uk/fees-and-funding/reach-oxford",
    eligibilitySummary:
      "Scholarship eligibility will be evaluated against verified program criteria once the funding record is sourced and verified.",
    renewalCriteria: "Pending verified data",
  },
  {
    id: "holland-scholarship",
    name: "NL Scholarship (formerly Holland Scholarship)",
    provider: "Dutch Ministry of Education & Dutch Research Universities",
    universitiesCovered: "TU Delft, Erasmus Rotterdam, Utrecht, Amsterdam",
    citizenshipEligible: "Non-EEA citizens",
    countriesOfStudy: ["Netherlands"],
    academicThreshold: "Pending verified criteria",
    awardValue: null,
    awardFrequency: "Pending verified data",
    deadline: "Pending verified data",
    verificationStatus: "Pending verification",
    lastChecked: "Not yet verified",
    officialSource: "studyinnl.org/finances/nl-scholarship",
    eligibilitySummary:
      "Scholarship eligibility will be evaluated against verified program criteria once the funding record is sourced and verified.",
    renewalCriteria: "Pending verified data",
  },
  {
    id: "sheikh-mohammed-uae",
    name: "Global Leaders Fellowship",
    provider: "Abu Dhabi Education & Knowledge Authority (ADEK)",
    universitiesCovered: "NYU Abu Dhabi, Khalifa University, Sorbonne Abu Dhabi",
    citizenshipEligible: "Global / International & UAE residents",
    countriesOfStudy: ["United Arab Emirates"],
    academicThreshold: "Pending verified criteria",
    awardValue: null,
    awardFrequency: "Pending verified data",
    deadline: "Pending verified data",
    verificationStatus: "Pending verification",
    lastChecked: "Not yet verified",
    officialSource: "adek.gov.ae",
    eligibilitySummary:
      "Scholarship eligibility will be evaluated against verified program criteria once the funding record is sourced and verified.",
    renewalCriteria: "Pending verified data",
  },
];

export const INTELLIGENCE_ARTICLES: IntelligenceArticle[] = [
  {
    slug: "what-200k-education-budget-buys",
    title: "What a Fixed Education Budget Buys Across Global Markets",
    category: "Affordability",
    readTime: "Research in development",
    date: "Publication pending",
    featured: true,
    lead: "A planned EvidaPath analysis examining how a fixed family education budget translates into different outcomes depending on geography, program duration, and living costs.",
    keyTakeaway:
      "Research publication in development. Findings will appear here once produced from verified EvidaPath data.",
    dataSummary:
      "Methodology and underlying data will be documented when this analysis is published.",
  },
  {
    slug: "predicted-grades-university-universe",
    title: "How Much Do Predicted Grades Change Your University Universe?",
    category: "Admissions Intelligence",
    readTime: "Research in development",
    date: "Publication pending",
    featured: true,
    lead: "A planned analysis of how shifts in predicted grades alter the set of programs a student can credibly consider across national systems.",
    keyTakeaway:
      "Research publication in development. Findings will appear here once produced from verified EvidaPath data.",
    dataSummary:
      "Methodology and underlying data will be documented when this analysis is published.",
  },
  {
    slug: "where-scholarships-actually-change-affordability",
    title: "Where Scholarships Actually Change University Affordability",
    category: "Scholarships & Funding",
    readTime: "Research in development",
    date: "Publication pending",
    lead: "A planned analysis of where scholarship funding meaningfully shifts net family cost versus where partial awards leave a structural gap.",
    keyTakeaway:
      "Research publication in development. Findings will appear here once produced from verified EvidaPath data.",
    dataSummary:
      "Methodology and underlying data will be documented when this analysis is published.",
  },
  {
    slug: "sticker-price-is-not-the-cost-of-university",
    title: "Sticker Price Is Not the Cost of University",
    category: "Affordability",
    readTime: "Research in development",
    date: "Publication pending",
    lead: "A planned analysis of how accommodation, travel, visas, and currency exposure change the true cost of an international degree beyond tuition.",
    keyTakeaway:
      "Research publication in development. Findings will appear here once produced from verified EvidaPath data.",
    dataSummary:
      "Methodology and underlying data will be documented when this analysis is published.",
  },
  {
    slug: "how-program-duration-changes-economics",
    title: "How Program Duration Changes the Economics of an International Degree",
    category: "Global University Markets",
    readTime: "Research in development",
    date: "Publication pending",
    lead: "A planned analysis of the compound financial difference between three-year and four-year undergraduate programs.",
    keyTakeaway:
      "Research publication in development. Findings will appear here once produced from verified EvidaPath data.",
    dataSummary:
      "Methodology and underlying data will be documented when this analysis is published.",
  },
  {
    slug: "student-with-aab-predicted-grades",
    title: "A Student With AAB Predicted Grades: How the Opportunity Set Changes Across Countries",
    category: "Admissions Intelligence",
    readTime: "Research in development",
    date: "Publication pending",
    lead: "A planned case analysis of how different national systems evaluate the same academic profile, and how the accessible opportunity set shifts accordingly.",
    keyTakeaway:
      "Research publication in development. Findings will appear here once produced from verified EvidaPath data.",
    dataSummary:
      "Methodology and underlying data will be documented when this analysis is published.",
  },
];
