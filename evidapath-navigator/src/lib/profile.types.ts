// Types for the student profile + saved universities (Discover/Analyze persistence).
// Client-safe (types only). Backed by public.student_profiles and
// public.student_saved_universities (RLS-scoped to the authenticated user).

export interface StudentProfile {
  id: string;
  user_id: string;
  curriculum: string | null;
  grade_band: string | null;
  intended_subject: string | null;
  academic_level: "undergraduate" | "postgraduate" | null;
  preferred_region: string | null;
  annual_budget: number | null;
  budget_currency: string;
  citizenship: string | null;
  preferences: string | null;
  created_at: string;
  updated_at: string;
}

export interface SavedUniversity {
  id: string;
  user_id: string;
  sanity_university_id: string;
  university_name: string | null;
  note: string | null;
  saved_at: string;
}

// Fields a student may write to their profile (server sets user_id + timestamps).
export type StudentProfileInput = Partial<
  Pick<
    StudentProfile,
    | "curriculum"
    | "grade_band"
    | "intended_subject"
    | "academic_level"
    | "preferred_region"
    | "annual_budget"
    | "budget_currency"
    | "citizenship"
    | "preferences"
  >
>;
