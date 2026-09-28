// Thin server-function wrappers for the student profile + saved universities.
// Safe to import anywhere. Logic lives in ./profile.server.ts (RLS-scoped).

import { createServerFn } from "@tanstack/react-start";
import { z } from "zod";
import {
  getProfileSvc,
  upsertProfileSvc,
  listSavedUniversitiesSvc,
  saveUniversitySvc,
  removeSavedUniversitySvc,
} from "./profile.server";

// ── Profile ─────────────────────────────────────────────────────────────────

export const getProfile = createServerFn({ method: "GET" }).handler(async () => {
  return getProfileSvc();
});

const ProfileInputSchema = z.object({
  curriculum: z.string().nullable().optional(),
  grade_band: z.string().nullable().optional(),
  intended_subject: z.string().nullable().optional(),
  academic_level: z.enum(["undergraduate", "postgraduate"]).nullable().optional(),
  preferred_region: z.string().nullable().optional(),
  annual_budget: z.number().nullable().optional(),
  budget_currency: z.string().optional(),
  citizenship: z.string().nullable().optional(),
  preferences: z.string().nullable().optional(),
});

export const upsertProfile = createServerFn({ method: "POST" })
  .validator((data) => ProfileInputSchema.parse(data))
  .handler(async ({ data }) => {
    return upsertProfileSvc(data as Parameters<typeof upsertProfileSvc>[0]);
  });

// ── Saved universities ──────────────────────────────────────────────────────

export const listSavedUniversities = createServerFn({ method: "GET" }).handler(async () => {
  return listSavedUniversitiesSvc();
});

const SaveUniversitySchema = z.object({
  sanity_university_id: z.string().min(1),
  university_name: z.string().nullable().optional(),
  note: z.string().nullable().optional(),
});

export const saveUniversity = createServerFn({ method: "POST" })
  .validator((data) => SaveUniversitySchema.parse(data))
  .handler(async ({ data }) => {
    return saveUniversitySvc(data as Parameters<typeof saveUniversitySvc>[0]);
  });

export const removeSavedUniversity = createServerFn({ method: "POST" })
  .validator((data) => z.object({ sanity_university_id: z.string().min(1) }).parse(data))
  .handler(async ({ data }) => {
    await removeSavedUniversitySvc(data.sanity_university_id);
    return { ok: true };
  });
