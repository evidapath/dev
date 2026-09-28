// Server-only helpers for the student profile + saved universities.
// Named *.server.ts (blocked from client bundles). All access uses the
// user-scoped SSR client (cookie session, subject to RLS). No service-role key.

import { getSupabaseServerClient } from "./supabase.server";
import type { StudentProfile, StudentProfileInput, SavedUniversity } from "./profile.types";

async function currentUserId(): Promise<string> {
  const sb = getSupabaseServerClient();
  const {
    data: { user },
  } = await sb.auth.getUser();
  if (!user) throw new Error("Not authenticated");
  return user.id;
}

// ── Profile (one row per user) ──────────────────────────────────────────────

export async function getProfileSvc(): Promise<StudentProfile | null> {
  const sb = getSupabaseServerClient();
  const uid = await currentUserId();
  const { data, error } = await sb
    .from("student_profiles")
    .select("*")
    .eq("user_id", uid)
    .maybeSingle();
  if (error) throw new Error(error.message);
  return (data as StudentProfile | null) ?? null;
}

export async function upsertProfileSvc(input: StudentProfileInput): Promise<StudentProfile> {
  const sb = getSupabaseServerClient();
  const uid = await currentUserId();
  // user_id is unique -> upsert keeps a single profile row per student.
  const { data, error } = await sb
    .from("student_profiles")
    .upsert({ ...input, user_id: uid }, { onConflict: "user_id" })
    .select()
    .single();
  if (error) throw new Error(error.message);
  return data as StudentProfile;
}

// ── Saved universities (the student's "My Path" picks) ──────────────────────

export async function listSavedUniversitiesSvc(): Promise<SavedUniversity[]> {
  const sb = getSupabaseServerClient();
  const uid = await currentUserId();
  const { data, error } = await sb
    .from("student_saved_universities")
    .select("*")
    .eq("user_id", uid)
    .order("saved_at", { ascending: false });
  if (error) throw new Error(error.message);
  return (data ?? []) as SavedUniversity[];
}

export async function saveUniversitySvc(input: {
  sanity_university_id: string;
  university_name?: string | null;
  note?: string | null;
}): Promise<SavedUniversity> {
  const sb = getSupabaseServerClient();
  const uid = await currentUserId();
  // unique(user_id, sanity_university_id) -> idempotent save (no duplicates).
  const { data, error } = await sb
    .from("student_saved_universities")
    .upsert({ ...input, user_id: uid }, { onConflict: "user_id,sanity_university_id" })
    .select()
    .single();
  if (error) throw new Error(error.message);
  return data as SavedUniversity;
}

export async function removeSavedUniversitySvc(sanityUniversityId: string): Promise<void> {
  const sb = getSupabaseServerClient();
  const uid = await currentUserId();
  const { error } = await sb
    .from("student_saved_universities")
    .delete()
    .eq("user_id", uid)
    .eq("sanity_university_id", sanityUniversityId);
  if (error) throw new Error(error.message);
}
