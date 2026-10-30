// Server-only helpers for the Offer Vault. Blocked from client bundles (*.server.ts).
// All access uses the user-scoped SSR client (cookie session, subject to RLS).
// The service-role key is NEVER used here.

import { getSupabaseServerClient } from "./supabase.server";
import { getUniversitiesFromSanity } from "./sanity.server";
import { UNIVERSITIES_DATA } from "./mock-data";
import type { University } from "./mock-data";
import { convert, loadFxRates, type FxRates } from "./fx.functions";

// Turn raw Postgres errors into messages a student can act on.
function dbError(error: { message: string; code?: string }): Error {
  const m = error.message;
  if (/currency/i.test(m))
    return new Error("Currency must be a 3-letter code such as EUR, GBP or USD.");
  if (/deadline|_date/i.test(m) && /check/i.test(m))
    return new Error("One of the dates isn't valid — check the order of your dates.");
  if (/amount|>= 0|non.?negative/i.test(m) && /check/i.test(m))
    return new Error("Amounts can't be negative.");
  if (error.code === "23505")
    return new Error("That already exists — edit the existing entry instead.");
  if (/row-level security|permission/i.test(m))
    return new Error("You don't have permission to change this. Try signing in again.");
  if (/check constraint/i.test(m))
    return new Error("Some of the values aren't valid. Please check the form and try again.");
  return new Error(m);
}
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
  fx: FxRates | null,
): OfferAnalysis {
  const uni = universities.find((u) => u.id === application.sanity_university_id);
  const annualCost = uni?.costs.totalAnnual ?? null;
  const currency = uni?.costs.currency || awards[0]?.currency || "USD";
  const duration = uni?.durationYears ?? null;
  // Awards can be in a different currency from the university's published cost
  // (e.g. a EUR scholarship at a GBP university): convert before subtracting.
  let unconvertedAwards = 0;
  const totalAwardAnnual = Math.round(
    awards.reduce((sum, a) => {
      const amount = annualAwardAmount(a);
      if (!amount) return sum;
      const v = convert(amount, a.currency || currency, currency, fx);
      if (v == null) {
        unconvertedAwards++;
        return sum;
      }
      return sum + v;
    }, 0),
  );
  const netAnnualFamilyCost =
    annualCost != null ? Math.max(0, annualCost - totalAwardAnnual) : null;
  const totalDegreeFamilyCost =
    netAnnualFamilyCost != null && duration ? netAnnualFamilyCost * duration : null;
  const hasDocumentVerifiedAwards = awards.some((a) => a.verification_level !== "self_reported");
  return {
    currency,
    unconvertedAwards,
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
  if (error) throw dbError(error);
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
  if (error) throw dbError(error);
  return data as StudentApplication;
}

export async function deleteApplicationSvc(id: string): Promise<void> {
  const sb = getSupabaseServerClient();
  const uid = await currentUserId();
  const { error } = await sb.from("student_applications").delete().eq("id", id).eq("user_id", uid);
  if (error) throw dbError(error);
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

  if (offersRes.error) throw dbError(offersRes.error);

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
  const fx = await loadFxRates();

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
        analysis: buildAnalysis(application, offerAwards, universities, fx),
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
  if (error) throw dbError(error);
  return data as StudentOffer;
}

export async function deleteOfferSvc(id: string): Promise<void> {
  const sb = getSupabaseServerClient();
  const uid = await currentUserId();
  const { error } = await sb.from("student_offers").delete().eq("id", id).eq("user_id", uid);
  if (error) throw dbError(error);
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
  if (error) throw dbError(error);
  return data as StudentAward;
}

export async function deleteAwardSvc(id: string): Promise<void> {
  const sb = getSupabaseServerClient();
  const uid = await currentUserId();
  const { error } = await sb.from("student_awards").delete().eq("id", id).eq("user_id", uid);
  if (error) throw dbError(error);
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
  if (error) throw dbError(error);
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
  if (error) throw dbError(error);
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
  if (error) throw dbError(error);
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
  if (error) throw dbError(error);
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
  if (error) throw dbError(error);
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
