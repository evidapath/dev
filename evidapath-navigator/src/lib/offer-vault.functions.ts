// Thin server-function wrappers for the Offer Vault. Safe to import anywhere.
// All logic lives in ./offer-vault.server.ts (server-only, RLS-scoped).

import { createServerFn } from "@tanstack/react-start";
import { z } from "zod";
import {
  listApplicationsSvc,
  upsertApplicationSvc,
  deleteApplicationSvc,
  listOfferCompositesSvc,
  upsertOfferSvc,
  deleteOfferSvc,
  upsertAwardSvc,
  deleteAwardSvc,
  setAwardVerificationSvc,
  listDocumentsSvc,
  createDocumentRecordSvc,
  deleteDocumentSvc,
  recordEnrollmentDecisionSvc,
  getVerifiedAwardsSummarySvc,
} from "./offer-vault.server";

// ── Applications ──────────────────────────────────────────────────────────

export const listApplications = createServerFn({ method: "GET" }).handler(async () => {
  return listApplicationsSvc();
});

const ApplicationInputSchema = z.object({
  id: z.string().optional(),
  sanity_university_id: z.string().min(1),
  sanity_program_id: z.string().nullable().optional(),
  sanity_campus_id: z.string().nullable().optional(),
  university_name: z.string().min(1),
  program_name: z.string().nullable().optional(),
  application_cycle: z.string().nullable().optional(),
  decision_plan: z.string().nullable().optional(),
  application_date: z.string().nullable().optional(),
  status: z.string().optional(),
});

export const upsertApplication = createServerFn({ method: "POST" })
  .validator((data) => ApplicationInputSchema.parse(data))
  .handler(async ({ data }) => {
    return upsertApplicationSvc(data);
  });

export const deleteApplication = createServerFn({ method: "POST" })
  .validator((data) => z.object({ id: z.string() }).parse(data))
  .handler(async ({ data }) => {
    await deleteApplicationSvc(data.id);
    return { ok: true };
  });

// ── Offers ────────────────────────────────────────────────────────────────

export const listOfferComposites = createServerFn({ method: "GET" }).handler(async () => {
  return listOfferCompositesSvc();
});

const OfferInputSchema = z.object({
  id: z.string().optional(),
  application_id: z.string().min(1),
  admission_result: z.string().optional(),
  official_offer_date: z.string().nullable().optional(),
  response_deadline: z.string().nullable().optional(),
  enrollment_deposit_amount: z.number().nullable().optional(),
  deposit_deadline: z.string().nullable().optional(),
  currency: z.string().optional(),
  conditions_of_admission: z.string().nullable().optional(),
  notes: z.string().nullable().optional(),
  verification_level: z.string().optional(),
});

export const upsertOffer = createServerFn({ method: "POST" })
  .validator((data) => OfferInputSchema.parse(data))
  .handler(async ({ data }) => {
    return upsertOfferSvc(data);
  });

export const deleteOffer = createServerFn({ method: "POST" })
  .validator((data) => z.object({ id: z.string() }).parse(data))
  .handler(async ({ data }) => {
    await deleteOfferSvc(data.id);
    return { ok: true };
  });

// ── Awards ────────────────────────────────────────────────────────────────

const AwardInputSchema = z.object({
  id: z.string().optional(),
  offer_id: z.string().min(1),
  sanity_scholarship_id: z.string().nullable().optional(),
  award_name: z.string().min(1),
  award_type: z.string(),
  amount: z.number().nullable().optional(),
  currency: z.string().optional(),
  frequency: z.string().optional(),
  duration_years: z.number().nullable().optional(),
  renewal_criteria: z.string().nullable().optional(),
  min_gpa: z.number().nullable().optional(),
  need_vs_merit: z.string().nullable().optional(),
  document_id: z.string().nullable().optional(),
  verification_level: z.string().optional(),
});

export const upsertAward = createServerFn({ method: "POST" })
  .validator((data) => AwardInputSchema.parse(data))
  .handler(async ({ data }) => {
    return upsertAwardSvc(data as Parameters<typeof upsertAwardSvc>[0]);
  });

export const deleteAward = createServerFn({ method: "POST" })
  .validator((data) => z.object({ id: z.string() }).parse(data))
  .handler(async ({ data }) => {
    await deleteAwardSvc(data.id);
    return { ok: true };
  });

export const setAwardVerification = createServerFn({ method: "POST" })
  .validator((data) => z.object({ id: z.string(), level: z.string() }).parse(data))
  .handler(async ({ data }) => {
    await setAwardVerificationSvc(
      data.id,
      data.level as "self_reported" | "document_verified" | "institution_verified",
    );
    return { ok: true };
  });

// ── Documents ─────────────────────────────────────────────────────────────

export const listDocuments = createServerFn({ method: "GET" })
  .validator((data) => z.object({ offerId: z.string() }).parse(data))
  .handler(async ({ data }) => {
    return listDocumentsSvc(data.offerId);
  });

const DocumentInputSchema = z.object({
  offer_id: z.string().min(1),
  document_type: z.string(),
  storage_path: z.string().min(1),
  file_name: z.string().min(1),
  mime_type: z.string().nullable().optional(),
  size_bytes: z.number().nullable().optional(),
});

export const createDocumentRecord = createServerFn({ method: "POST" })
  .validator((data) => DocumentInputSchema.parse(data))
  .handler(async ({ data }) => {
    return createDocumentRecordSvc(data as Parameters<typeof createDocumentRecordSvc>[0]);
  });

export const deleteDocument = createServerFn({ method: "POST" })
  .validator((data) => z.object({ id: z.string() }).parse(data))
  .handler(async ({ data }) => {
    await deleteDocumentSvc(data.id);
    return { ok: true };
  });

// ── Enrollment decisions ──────────────────────────────────────────────────

const EnrollmentInputSchema = z.object({
  offer_id: z.string().min(1),
  decision: z.string(),
  enrollment_term: z.string().nullable().optional(),
  final_award_accepted: z.number().nullable().optional(),
  expected_first_year_family_contribution: z.number().nullable().optional(),
});

export const recordEnrollmentDecision = createServerFn({ method: "POST" })
  .validator((data) => EnrollmentInputSchema.parse(data))
  .handler(async ({ data }) => {
    return recordEnrollmentDecisionSvc(data as Parameters<typeof recordEnrollmentDecisionSvc>[0]);
  });

// ── Capital plan integration ──────────────────────────────────────────────

export const getVerifiedAwardsSummary = createServerFn({ method: "GET" }).handler(async () => {
  return getVerifiedAwardsSummarySvc();
});
