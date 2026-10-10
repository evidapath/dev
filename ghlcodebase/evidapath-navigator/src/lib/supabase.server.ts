import { createServerClient } from "@supabase/ssr";
import { createClient } from "@supabase/supabase-js";
import type { SupabaseClient } from "@supabase/supabase-js";
import { getRequestHeader } from "@tanstack/start-server-core";

// ────────────────────────────────────────────────────────────────────────────
// Supabase server-side client architecture
//
// EvidaPath uses TWO deliberately separated Supabase clients on the server.
// They do not share configuration and are never interchangeable.
//
// 1. SSR / session client  — getSupabaseServerClient()
//    Built from the publishable/anon key + the request cookies. It operates
//    AS the authenticated user and is fully subject to Row Level Security.
//    This is the ONLY client used for ordinary SSR session validation,
//    login-state resolution, password reset, profile access, and student
//    data access. No service-role key is involved.
//
// 2. Admin client           — getSupabaseAdminClient()
//    Built from SUPABASE_SERVICE_ROLE_KEY. It bypasses RLS and may ONLY be
//    used for explicitly privileged server-side operations that genuinely
//    require it (future administrative / background jobs). It is NOT used
//    for signup, sign-in, logout, session validation, password reset,
//    profile access, or student data access.
//
// Security:
//  - This module is named *.server.ts, so it is blocked from client bundles
//    by the TanStack Start import guard.
//  - The service role key is read INSIDE getSupabaseAdminClient(), never at
//    module scope, so it is never serialized into client code, HTML, or
//    network responses.
//  - Browser auth uses only VITE_SUPABASE_URL + VITE_SUPABASE_ANON_KEY
//    (publishable credentials). The service role key never reaches the browser.
//  - If no current feature requires admin/service-role access, the admin
//    client is not instantiated at all. The key stays stored securely for
//    future backend operations.
// ────────────────────────────────────────────────────────────────────────────

const supabaseUrl = process.env.VITE_SUPABASE_URL || import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey =
  process.env.VITE_SUPABASE_ANON_KEY || import.meta.env.VITE_SUPABASE_ANON_KEY;

/**
 * Build a request-scoped Supabase SSR client that reads the auth session from
 * the incoming request cookies. Operates as the authenticated user and is
 * subject to Row Level Security. Used for SSR session validation and all
 * ordinary authenticated-user lookups. No service-role key is used.
 */
export function getSupabaseServerClient(): SupabaseClient {
  const cookieHeader = getRequestHeader("cookie") ?? "";
  const cookies = parseCookies(cookieHeader);

  return createServerClient(supabaseUrl ?? "", supabaseAnonKey ?? "", {
    cookies: {
      getAll() {
        return cookies;
      },
      setAll(cookiesToSet) {
        cookiesToSet.forEach(({ name, value }) => {
          const existing = cookies.find((c) => c.name === name);
          if (existing) existing.value = value;
          else cookies.push({ name, value });
        });
      },
    },
  });
}

/**
 * Build a Supabase admin client using the service role key. This client
 * bypasses Row Level Security and may ONLY be used for explicitly privileged
 * server-side operations that genuinely require bypassing RLS (future
 * administrative / background operations).
 *
 * NEVER use this for ordinary auth, session validation, profile access, or
 * student data access — those run through the user-scoped SSR client and RLS.
 *
 * If no current feature requires admin access, do not call this. The key stays
 * stored securely for future backend operations.
 */
export function getSupabaseAdminClient(): SupabaseClient {
  const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!serviceRoleKey) {
    throw new Error(
      "SUPABASE_SERVICE_ROLE_KEY is not configured. The admin client is reserved for future privileged backend operations and is not required for ordinary authentication.",
    );
  }
  return createClient(supabaseUrl ?? "", serviceRoleKey, {
    auth: { autoRefreshToken: false, persistSession: false },
  });
}

function parseCookies(cookieHeader: string): { name: string; value: string }[] {
  if (!cookieHeader) return [];
  return cookieHeader
    .split(";")
    .map((part) => part.trim())
    .filter(Boolean)
    .map((part) => {
      const idx = part.indexOf("=");
      if (idx === -1) return { name: part, value: "" };
      return { name: part.slice(0, idx).trim(), value: part.slice(idx + 1).trim() };
    });
}
