// Server-only helpers for the Offer Vault. Blocked from client bundles (*.server.ts).
// All access uses the user-scoped SSR client (cookie session, subject to RLS).
// The service-role key is NEVER used here.

import { getSupabaseServerClient } from "./supabase.server";
import { getUniversitiesFromSanity } from "./sanity.server";
import { UNIVERSITIES_DATA } from "./mock-data";
import type { University } from "./mock-data";
import type {
  StudentApplication,
  StudentOffer,
  StudentAward,
  StudentOfferDocument,
  StudentEnrollmentDecision,
  OfferComposite,
  OfferAnalysis,
  VerificationLevel,
  VerifiedAwardSummary,
} from "./offer-vault.types";

async function currentUserId(): Promise<string> {
  const sb = getSupabaseServerClient();
  const {
    data: { user },
  } = await sb.auth.getUser();
  if (!user) throw new Error("Not authenticated");
  return user.id;
}

/** Annual-equivalent value of an award for cost comparison. */
export function annualAwardAmount(a: StudentAward): number {
  if (a.amount == null) return 0;
  if (a.frequency === "one_time") {
    return a.duration_years && a.duration_years > 0 ? a.amount / a.duration_years : a.amount;
  }
  return a.amount;
}

export function buildAnalysis(
  application: StudentApplication,
  awards: StudentAward[],
  universities: University[],
): OfferAnalysis {
  const uni = universities.find((u) => u.id === application.sanity_university_id);
  const annualCost = uni?.costs.totalAnnual ?? null;
  const duration = uni?.durationYears ?? null;
  const totalAwardAnnual = awards.reduce((sum, a) => sum + annualAwardAmount(a), 0);
  const netAnnualFamilyCost =
    annualCost != null ? Math.max(0, annualCost - totalAwardAnnual) : null;
  const totalDegreeFamilyCost =
    netAnnualFamilyCost != null && duration ? netAnnualFamilyCost * duration : null;
  const hasDocumentVerifiedAwards = awards.some((a) => a.verification_level !== "self_reported");
  return {
    annualCost,
    totalAwardAnnual,
    netAnnualFamilyCost,
    degreeDurationYears: duration ?? null,
    totalDegreeFamilyCost,
    hasDocumentVerifiedAwards,
    costDataStatus: annualCost != null ? "illustrative" : "pending",
  };
}

// ── Applications ──────────────────────────────────────────────────────────

export async function listApplicationsSvc(): Promise<StudentApplication[]> {
  const sb = getSupabaseServerClient();
  const uid = await currentUserId();
  const { data, error } = await sb
    .from("student_applications")
    .select("*")
    .eq("user_id", uid)
    .order("created_at", { ascending: false });
  if (error) throw new Error(error.message);
  return (data ?? []) as StudentApplication[];
}

export async function upsertApplicationSvc(
  input: Partial<StudentApplication> & { sanity_university_id: string; university_name: string },
): Promise<StudentApplication> {
  const sb = getSupabaseServerClient();
  const uid = await currentUserId();
  const payload = { ...input, user_id: uid };
  const { data, error } = await sb
    .from("student_applications")
    .upsert(payload, { onConflict: "id" })
    .select()
    .single();
  if (error) throw new Error(error.message);
  return data as StudentApplication;
}

export async function deleteApplicationSvc(id: string): Promise<void> {
  const sb = getSupabaseServerClient();
  const uid = await currentUserId();
  const { error } = await sb.from("student_applications").delete().eq("id", id).eq("user_id", uid);
  if (error) throw new Error(error.message);
}

// ── Offer composites (offers + applications + awards + documents + enrollment) ─

export async function listOfferCompositesSvc(): Promise<OfferComposite[]> {
  const sb = getSupabaseServerClient();
  const uid = await currentUserId();

  const [offersRes, awardsRes, docsRes, appsRes, enrollRes] = await Promise.all([
    sb.from("student_offers").select("*").eq("user_id", uid),
    sb.from("student_awards").select("*").eq("user_id", uid),
    sb.from("student_offer_documents").select("*").eq("user_id", uid),
    sb.from("student_applications").select("*").eq("user_id", uid),
    sb.from("student_enrollment_decisions").select("*").eq("user_id", uid),
  ]);

  if (offersRes.error) throw new Error(offersRes.error.message);

  const offers = (offersRes.data ?? []) as StudentOffer[];
  const awards = (awardsRes.data ?? []) as StudentAward[];
  const docs = (docsRes.data ?? []) as StudentOfferDocument[];
  const apps = (appsRes.data ?? []) as StudentApplication[];
  const enrollments = (enrollRes.data ?? []) as StudentEnrollmentDecision[];

  // Cost inputs for the offer analysis come from verified Sanity data (keyed by
  // the application's sanity_university_id). Fall back to the illustrative mock set
  // only if Sanity is unreachable, so the vault never breaks on a data outage.
  let universities: University[];
  try {
    universities = await getUniversitiesFromSanity();
    if (universities.length === 0) universities = UNIVERSITIES_DATA;
  } catch {
    universities = UNIVERSITIES_DATA;
  }

  return offers
    .map((offer) => {
      const application = apps.find((a) => a.id === offer.application_id);
      if (!application) {
        // Orphaned offer (application deleted); skip rather than crash.
        return null;
      }
      const offerAwards = awards.filter((a) => a.offer_id === offer.id);
      const offerDocs = docs.filter((d) => d.offer_id === offer.id);
      const enrollment = enrollments.find((e) => e.offer_id === offer.id) ?? null;
      return {
        offer,
        application,
        awards: offerAwards,
        documents: offerDocs,
        enrollment,
        analysis: buildAnalysis(application, offerAwards, universities),
      } satisfies OfferComposite;
    })
    .filter((c): c is OfferComposite => c !== null);
}

export async function upsertOfferSvc(
  input: Partial<StudentOffer> & { application_id: string },
): Promise<StudentOffer> {
  const sb = getSupabaseServerClient();
  const uid = await currentUserId();
  const payload = { ...input, user_id: uid };
  const { data, error } = await sb
    .from("student_offers")
    .upsert(payload, { onConflict: "id" })
    .select()
    .single();
  if (error) throw new Error(error.message);
  return data as StudentOffer;
}

export async function deleteOfferSvc(id: string): Promise<void> {
  const sb = getSupabaseServerClient();
  const uid = await currentUserId();
  const { error } = await sb.from("student_offers").delete().eq("id", id).eq("user_id", uid);
  if (error) throw new Error(error.message);
}

// ── Awards ────────────────────────────────────────────────────────────────

export async function upsertAwardSvc(
  input: Partial<StudentAward> & {
    offer_id: string;
    award_name: string;
    award_type: StudentAward["award_type"];
  },
): Promise<StudentAward> {
  const sb = getSupabaseServerClient();
  const uid = await currentUserId();
  const payload = { ...input, user_id: uid };
  const { data, error } = await sb
    .from("student_awards")
    .upsert(payload, { onConflict: "id" })
    .select()
    .single();
  if (error) throw new Error(error.message);
  return data as StudentAward;
}

export async function deleteAwardSvc(id: string): Promise<void> {
  const sb = getSupabaseServerClient();
  const uid = await currentUserId();
  const { error } = await sb.from("student_awards").delete().eq("id", id).eq("user_id", uid);
  if (error) throw new Error(error.message);
}

/** Promote an award's verification level (e.g. after a supporting document is linked). */
export async function setAwardVerificationSvc(id: string, level: VerificationLevel): Promise<void> {
  const sb = getSupabaseServerClient();
  const uid = await currentUserId();
  const { error } = await sb
    .from("student_awards")
    .update({ verification_level: level })
    .eq("id", id)
    .eq("user_id", uid);
  if (error) throw new Error(error.message);
}

// ── Documents (metadata only; file bytes uploaded via browser Storage client) ─

export async function listDocumentsSvc(offerId: string): Promise<StudentOfferDocument[]> {
  const sb = getSupabaseServerClient();
  const uid = await currentUserId();
  const { data, error } = await sb
    .from("student_offer_documents")
    .select("*")
    .eq("offer_id", offerId)
    .eq("user_id", uid)
    .order("uploaded_at", { ascending: false });
  if (error) throw new Error(error.message);
  return (data ?? []) as StudentOfferDocument[];
}

export async function createDocumentRecordSvc(input: {
  offer_id: string;
  document_type: StudentOfferDocument["document_type"];
  storage_path: string;
  file_name: string;
  mime_type?: string | null;
  size_bytes?: number | null;
}): Promise<StudentOfferDocument> {
  const sb = getSupabaseServerClient();
  const uid = await currentUserId();
  const { data, error } = await sb
    .from("student_offer_documents")
    .insert({ ...input, user_id: uid })
    .select()
    .single();
  if (error) throw new Error(error.message);
  return data as StudentOfferDocument;
}

export async function deleteDocumentSvc(id: string): Promise<void> {
  const sb = getSupabaseServerClient();
  const uid = await currentUserId();
  const { data, error } = await sb
    .from("student_offer_documents")
    .delete()
    .eq("id", id)
    .eq("user_id", uid)
    .select("storage_path");
  if (error) throw new Error(error.message);
  // Best-effort removal of the object from private storage via the user-scoped client.
  if (data && data.length > 0) {
    const path = (data[0] as { storage_path?: string }).storage_path;
    if (path) {
      await sb.storage
        .from("student-documents")
        .remove([path])
        .catch(() => {});
    }
  }
}

// ── Enrollment decisions ──────────────────────────────────────────────────

export async function recordEnrollmentDecisionSvc(input: {
  offer_id: string;
  decision: StudentEnrollmentDecision["decision"];
  enrollment_term?: string | null;
  final_award_accepted?: number | null;
  expected_first_year_family_contribution?: number | null;
}): Promise<StudentEnrollmentDecision> {
  const sb = getSupabaseServerClient();
  const uid = await currentUserId();
  // Upsert on offer_id (one decision per offer).
  const { data: existing } = await sb
    .from("student_enrollment_decisions")
    .select("id")
    .eq("offer_id", input.offer_id)
    .eq("user_id", uid)
    .maybeSingle();
  const payload = {
    ...input,
    user_id: uid,
    ...(existing ? { id: (existing as { id: string }).id } : {}),
  };
  const { data, error } = await sb
    .from("student_enrollment_decisions")
    .upsert(payload, { onConflict: "id" })
    .select()
    .single();
  if (error) throw new Error(error.message);
  return data as StudentEnrollmentDecision;
}

// ── Capital plan integration ──────────────────────────────────────────────

export async function getVerifiedAwardsSummarySvc(): Promise<VerifiedAwardSummary> {
  const composites = await listOfferCompositesSvc();
  let totalAnnualAward = 0;
  let hasDocumentVerified = false;
  let count = 0;
  for (const c of composites) {
    for (const a of c.awards) {
      totalAnnualAward += annualAwardAmount(a);
      count += 1;
      if (a.verification_level !== "self_reported") hasDocumentVerified = true;
    }
  }
  return { totalAnnualAward, hasDocumentVerified, count };
}
