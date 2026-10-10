// Server-only account-deletion helpers. Blocked from client bundles (*.server.ts).
//
// DELETION FLOW (all server-side, in safe order):
//   1. Resolve the authenticated user from the request session (user-scoped SSR
//      client, RLS-scoped, NO service-role key). Unauthenticated → throw.
//   2. Delete all private Storage objects under <user-id>/ in the private
//      `student-documents` bucket, using the user-scoped client (RLS permits
//      only the owner's files). Recursive list → remove.
//   3. Explicitly delete the user's private DB rows in dependency order
//      (outcomes → enrollment → awards → documents → offers → applications),
//      each scoped to user_id. (auth.users ON DELETE CASCADE would also handle
//      these, but we delete explicitly first so a failure here stops the flow
//      BEFORE the auth user is removed.)
//   4. Delete the Supabase Auth user LAST via the admin client
//      (auth.admin.deleteUser), which requires the service-role key. This is
//      the ONLY operation that needs elevated access.
//
// If any step fails, the function throws and the caller must NOT report success.
// No shadow copies of student data are retained.

import { getSupabaseServerClient, getSupabaseAdminClient } from "./supabase.server";

const PRIVATE_BUCKET = "student-documents";

export interface DeletionSummary {
  applications: number;
  offers: number;
  awards: number;
  documents: number;
  enrollmentDecisions: number;
  outcomes: number;
}

/** Resolve the authenticated user id from the request session, or throw. */
async function requireCurrentUserId(): Promise<string> {
  const sb = getSupabaseServerClient();
  const {
    data: { user },
  } = await sb.auth.getUser();
  if (!user) {
    throw new Error("Not authenticated");
  }
  return user.id;
}

/**
 * Count the user's private records for the pre-deletion summary shown to the
 * user. Informational only — deletion is never conditional on these counts.
 */
export async function getDeletionSummarySvc(): Promise<DeletionSummary> {
  const sb = getSupabaseServerClient();
  const uid = await requireCurrentUserId();

  const [apps, offers, awards, docs, enroll, outcomes] = await Promise.all([
    sb.from("student_applications").select("id", { count: "exact", head: true }).eq("user_id", uid),
    sb.from("student_offers").select("id", { count: "exact", head: true }).eq("user_id", uid),
    sb.from("student_awards").select("id", { count: "exact", head: true }).eq("user_id", uid),
    sb
      .from("student_offer_documents")
      .select("id", { count: "exact", head: true })
      .eq("user_id", uid),
    sb
      .from("student_enrollment_decisions")
      .select("id", { count: "exact", head: true })
      .eq("user_id", uid),
    sb.from("student_outcomes").select("id", { count: "exact", head: true }).eq("user_id", uid),
  ]);

  return {
    applications: apps.count ?? 0,
    offers: offers.count ?? 0,
    awards: awards.count ?? 0,
    documents: docs.count ?? 0,
    enrollmentDecisions: enroll.count ?? 0,
    outcomes: outcomes.count ?? 0,
  };
}

/**
 * Recursively collect every Storage object path under a prefix in the private
 * bucket. Folders (id === null) are recursed into; files are collected.
 */
async function collectStoragePaths(
  sb: ReturnType<typeof getSupabaseServerClient>,
  prefix: string,
  out: string[],
): Promise<void> {
  let offset = 0;
  // Paginate via offset; Supabase list supports up to 1000 per call.
  for (;;) {
    const { data, error } = await sb.storage
      .from(PRIVATE_BUCKET)
      .list(prefix, { limit: 1000, offset });
    if (error) {
      throw new Error(`Storage list failed under "${prefix}": ${error.message}`);
    }
    if (!data || data.length === 0) break;

    for (const item of data) {
      const full = prefix ? `${prefix}/${item.name}` : item.name;
      if (item.id === null) {
        // Folder — recurse.
        await collectStoragePaths(sb, full, out);
      } else {
        out.push(full);
      }
    }

    if (data.length < 1000) break;
    offset += data.length;
  }
}

/** Delete every private Storage object owned by the user (path starts with <uid>/). */
async function deleteStorageForUser(uid: string): Promise<number> {
  const sb = getSupabaseServerClient();
  const paths: string[] = [];
  // The user's folder is their auth uid (matches the <user-id>/<offer-id>/<file>
  // convention enforced by the storage-path trigger + Storage policies).
  await collectStoragePaths(sb, uid, paths);

  if (paths.length === 0) return 0;

  // remove() accepts up to 1000 paths per call.
  for (let i = 0; i < paths.length; i += 1000) {
    const batch = paths.slice(i, i + 1000);
    const { error } = await sb.storage.from(PRIVATE_BUCKET).remove(batch);
    if (error) {
      throw new Error(`Storage delete failed: ${error.message}`);
    }
  }
  return paths.length;
}

/** Explicitly delete the user's private DB rows in safe dependency order. */
async function deletePrivateRows(uid: string): Promise<void> {
  const sb = getSupabaseServerClient();
  // Order: leaf tables first.
  const tables = [
    "student_outcomes",
    "student_enrollment_decisions",
    "student_awards",
    "student_offer_documents",
    "student_offers",
    "student_applications",
  ] as const;

  for (const table of tables) {
    const { error } = await sb.from(table).delete().eq("user_id", uid);
    if (error) {
      throw new Error(`Failed to delete from ${table}: ${error.message}`);
    }
  }
}

/**
 * Permanently delete the authenticated user's account and all private data.
 *
 * Order: Storage objects → private DB rows → Auth user (LAST).
 * Throws on any failure; the caller must surface a generic failure and must
 * NOT claim success.
 *
 * Returns a result describing what was removed (for safe server-side logging;
 * no PII beyond counts is retained).
 */
export async function deleteAccountSvc(): Promise<{
  ok: true;
  storageObjectsDeleted: number;
}> {
  const uid = await requireCurrentUserId();

  // 1. Private Storage objects.
  const storageObjectsDeleted = await deleteStorageForUser(uid);

  // 2. Private DB rows (explicit, RLS-scoped to this user).
  await deletePrivateRows(uid);

  // 3. Auth user — LAST, via the admin client (service-role key).
  //    This is the only operation requiring elevated access. The key is read
  //    inside getSupabaseAdminClient() and never reaches the browser.
  const admin = getSupabaseAdminClient();
  const { error: authError } = await admin.auth.admin.deleteUser(uid);
  if (authError) {
    throw new Error(`Failed to delete auth user: ${authError.message}`);
  }

  return { ok: true, storageObjectsDeleted };
}
