// Client-safe types for the EvidaPath Offer Vault private student workflow.
// These describe PRIVATE student data stored in Supabase (subject to RLS).
// Public university/scholarship data lives in Sanity and is referenced by ID.

export type ApplicationStatus =
  | "planning"
  | "started"
  | "submitted"
  | "in_review"
  | "waitlisted"
  | "admitted"
  | "rejected"
  | "withdrawn";

export type AwardType =
  | "scholarship"
  | "grant"
  | "need_based_aid"
  | "merit_aid"
  | "tuition_waiver"
  | "housing_award"
  | "government_sponsorship"
  | "external_scholarship"
  | "other";

export type AwardFrequency = "one_time" | "annual_renewable" | "per_term" | "other";

export type VerificationLevel = "self_reported" | "document_verified" | "institution_verified";

export type DocumentType =
  | "offer_letter"
  | "scholarship_letter"
  | "financial_aid_letter"
  | "award_notice"
  | "enrollment_confirmation"
  | "other";

export type EnrollmentDecision =
  "accepted" | "declined" | "deferred" | "waitlist_accepted" | "withdrawn";

export type NeedVsMerit = "need_based" | "merit_based" | "hybrid" | "unspecified";

export interface StudentApplication {
  id: string;
  user_id: string;
  sanity_university_id: string;
  sanity_program_id: string | null;
  sanity_campus_id: string | null;
  university_name: string;
  program_name: string | null;
  application_cycle: string | null;
  decision_plan: string | null;
  application_date: string | null;
  status: ApplicationStatus;
  created_at: string;
  updated_at: string;
}

export interface StudentOffer {
  id: string;
  user_id: string;
  application_id: string;
  admission_result: string;
  official_offer_date: string | null;
  response_deadline: string | null;
  enrollment_deposit_amount: number | null;
  deposit_deadline: string | null;
  currency: string;
  conditions_of_admission: string | null;
  notes: string | null;
  verification_level: VerificationLevel;
  created_at: string;
  updated_at: string;
}

export interface StudentAward {
  id: string;
  user_id: string;
  offer_id: string;
  sanity_scholarship_id: string | null;
  award_name: string;
  award_type: AwardType;
  amount: number | null;
  currency: string;
  frequency: AwardFrequency;
  duration_years: number | null;
  renewal_criteria: string | null;
  min_gpa: number | null;
  need_vs_merit: NeedVsMerit | null;
  document_id: string | null;
  verification_level: VerificationLevel;
  created_at: string;
  updated_at: string;
}

export interface StudentOfferDocument {
  id: string;
  user_id: string;
  offer_id: string;
  document_type: DocumentType;
  storage_path: string;
  file_name: string;
  mime_type: string | null;
  size_bytes: number | null;
  uploaded_at: string;
}

export interface StudentEnrollmentDecision {
  id: string;
  user_id: string;
  offer_id: string;
  decision: EnrollmentDecision;
  enrollment_term: string | null;
  final_award_accepted: number | null;
  expected_first_year_family_contribution: number | null;
  recorded_at: string;
}

export interface OfferAnalysis {
  /** Published/estimated annual cost from public (Sanity) data, null when pending. */
  annualCost: number | null;
  /** Sum of annual-equivalent verified + self-reported awards. */
  totalAwardAnnual: number;
  /** annualCost - totalAwardAnnual, null when annualCost is pending. */
  netAnnualFamilyCost: number | null;
  degreeDurationYears: number | null;
  totalDegreeFamilyCost: number | null;
  hasDocumentVerifiedAwards: boolean;
  costDataStatus: "pending" | "illustrative";
}

export interface OfferComposite {
  offer: StudentOffer;
  application: StudentApplication;
  awards: StudentAward[];
  documents: StudentOfferDocument[];
  enrollment: StudentEnrollmentDecision | null;
  analysis: OfferAnalysis;
}

export interface VerifiedAwardSummary {
  totalAnnualAward: number;
  hasDocumentVerified: boolean;
  count: number;
}

export const APPLICATION_STATUSES: ApplicationStatus[] = [
  "planning",
  "started",
  "submitted",
  "in_review",
  "waitlisted",
  "admitted",
  "rejected",
  "withdrawn",
];

export const AWARD_TYPES: AwardType[] = [
  "scholarship",
  "grant",
  "need_based_aid",
  "merit_aid",
  "tuition_waiver",
  "housing_award",
  "government_sponsorship",
  "external_scholarship",
  "other",
];

export const AWARD_FREQUENCIES: AwardFrequency[] = [
  "one_time",
  "annual_renewable",
  "per_term",
  "other",
];

export const DOCUMENT_TYPES: DocumentType[] = [
  "offer_letter",
  "scholarship_letter",
  "financial_aid_letter",
  "award_notice",
  "enrollment_confirmation",
  "other",
];

export const ENROLLMENT_DECISIONS: EnrollmentDecision[] = [
  "accepted",
  "declined",
  "deferred",
  "waitlist_accepted",
  "withdrawn",
];
