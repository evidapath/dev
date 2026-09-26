// ───────────────────────────────────────────────────────────────────────────
// EvidaPath Decision Model — illustrative sample analysis
//
// IMPORTANT: This file contains ILLUSTRATIVE / DEMO content only. The status
// labels, qualitative notes, and structural fields below demonstrate the shape
// of an EvidaPath decision analysis. They are NOT derived from verified data.
//
// All numeric cost, funding, gap, and score fields are null pending verified
// data. Live analysis will populate these from verified EvidaPath datasets with
// source attribution and confidence indicators.
// ───────────────────────────────────────────────────────────────────────────

export interface DecisionDimensions {
  academicReadiness: {
    status: "Strong Alignment" | "Borderline Prerequisite" | "Gap Identified";
    details: string;
    metrics: { label: string; value: string; benchmark: string }[];
  };
  admissionsEvidence: {
    evidenceStrength: string;
    acceptanceBenchmark: string;
    details: string;
    uncertaintyFactor: string;
  };
  financialFit: {
    annualTotalCost: number | null;
    fourYearCommitment: number | null;
    identifiedFunding: number | null;
    remainingFamilyGap: number | null;
    affordabilityScore: number | null;
    currency: string;
  };
  careerAlignment: {
    rating: string;
    industryConnections: string[];
    postStudyVisa: string;
  };
  pathwayFlexibility: {
    alternativeRoutesCount: number;
    options: { name: string; type: string; costDelta: string }[];
  };
  improvementLevers: {
    id: string;
    action: string;
    timeline: string;
    impact: "High" | "Medium" | "Structural";
    controllability: "High Control" | "Moderate Control";
    category: "Academic" | "Testing" | "Financial / Scholarship" | "Pathway";
  }[];
}

const PENDING = "Pending verified data";

export const SAMPLE_DECISION_ANALYSIS: Record<string, DecisionDimensions> = {
  "oxford-univ": {
    academicReadiness: {
      status: "Borderline Prerequisite",
      details:
        "Illustrative preview. Live analysis will compare the student's curriculum, predicted grades, and prerequisites against verified program requirements, and surface where alignment is strong and where gaps remain.",
      metrics: [
        { label: "Target Profile", value: PENDING, benchmark: PENDING },
        { label: "Subject Prerequisites", value: PENDING, benchmark: PENDING },
        { label: "Admissions Test", value: PENDING, benchmark: PENDING },
      ],
    },
    admissionsEvidence: {
      evidenceStrength: "Pending verified data",
      acceptanceBenchmark: PENDING,
      details:
        "Illustrative preview. Admissions evidence will compare the student's available evidence against verified requirements, historical information, and relevant applicant benchmarks.",
      uncertaintyFactor:
        "Where evidence is incomplete, EvidaPath will communicate uncertainty rather than manufacturing precision.",
    },
    financialFit: {
      annualTotalCost: null,
      fourYearCommitment: null,
      identifiedFunding: null,
      remainingFamilyGap: null,
      affordabilityScore: null,
      currency: "USD",
    },
    careerAlignment: {
      rating:
        "Illustrative preview. Career alignment will assess how the institution, program, and geography connect with the student's stated direction.",
      industryConnections: ["Pending verified data"],
      postStudyVisa: PENDING,
    },
    pathwayFlexibility: {
      alternativeRoutesCount: 3,
      options: [
        { name: "Imperial College London", type: "Alternative Direct", costDelta: PENDING },
        { name: "University of Warwick", type: "Safety Pathway", costDelta: PENDING },
        { name: "TU Delft (Netherlands)", type: "Strategic Pivot", costDelta: PENDING },
      ],
    },
    improvementLevers: [
      {
        id: "l1",
        action:
          "Illustrative lever. Live plans will recommend specific, controllable actions to improve academic readiness, affordability, or available pathways.",
        timeline: PENDING,
        impact: "High",
        controllability: "High Control",
        category: "Testing",
      },
      {
        id: "l2",
        action:
          "Illustrative lever. Live plans will recommend specific, controllable actions to improve academic readiness, affordability, or available pathways.",
        timeline: PENDING,
        impact: "High",
        controllability: "High Control",
        category: "Academic",
      },
      {
        id: "l3",
        action:
          "Illustrative lever. Live plans will recommend specific, controllable actions to improve academic readiness, affordability, or available pathways.",
        timeline: PENDING,
        impact: "Structural",
        controllability: "Moderate Control",
        category: "Financial / Scholarship",
      },
      {
        id: "l4",
        action:
          "Illustrative lever. Live plans will recommend specific, controllable actions to improve academic readiness, affordability, or available pathways.",
        timeline: PENDING,
        impact: "Structural",
        controllability: "High Control",
        category: "Pathway",
      },
    ],
  },
  "tum-germany": {
    academicReadiness: {
      status: "Strong Alignment",
      details:
        "Illustrative preview. Live analysis will compare the student's curriculum, predicted grades, and prerequisites against verified program requirements, and surface where alignment is strong and where gaps remain.",
      metrics: [
        { label: "High School GPA", value: PENDING, benchmark: PENDING },
        { label: "Math & Science Rigor", value: PENDING, benchmark: PENDING },
        { label: "Language", value: PENDING, benchmark: PENDING },
      ],
    },
    admissionsEvidence: {
      evidenceStrength: "Pending verified data",
      acceptanceBenchmark: PENDING,
      details:
        "Illustrative preview. Admissions evidence will compare the student's available evidence against verified requirements, historical information, and relevant applicant benchmarks.",
      uncertaintyFactor:
        "Diploma equivalency and selection procedures introduce variables that will be modelled and communicated explicitly.",
    },
    financialFit: {
      annualTotalCost: null,
      fourYearCommitment: null,
      identifiedFunding: null,
      remainingFamilyGap: null,
      affordabilityScore: null,
      currency: "USD",
    },
    careerAlignment: {
      rating:
        "Illustrative preview. Career alignment will assess how the institution, program, and geography connect with the student's stated direction.",
      industryConnections: ["Pending verified data"],
      postStudyVisa: PENDING,
    },
    pathwayFlexibility: {
      alternativeRoutesCount: 2,
      options: [
        { name: "RWTH Aachen University", type: "Peer Institution", costDelta: PENDING },
        { name: "KU Leuven (Belgium)", type: "Neighboring EU Hub", costDelta: PENDING },
      ],
    },
    improvementLevers: [
      {
        id: "t1",
        action:
          "Illustrative lever. Live plans will recommend specific, controllable actions to improve academic readiness, affordability, or available pathways.",
        timeline: PENDING,
        impact: "Structural",
        controllability: "High Control",
        category: "Academic",
      },
      {
        id: "t2",
        action:
          "Illustrative lever. Live plans will recommend specific, controllable actions to improve academic readiness, affordability, or available pathways.",
        timeline: PENDING,
        impact: "High",
        controllability: "Moderate Control",
        category: "Financial / Scholarship",
      },
      {
        id: "t3",
        action:
          "Illustrative lever. Live plans will recommend specific, controllable actions to improve academic readiness, affordability, or available pathways.",
        timeline: PENDING,
        impact: "Medium",
        controllability: "High Control",
        category: "Pathway",
      },
    ],
  },
};
