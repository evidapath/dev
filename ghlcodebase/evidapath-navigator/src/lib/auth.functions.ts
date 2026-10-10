import { createServerFn } from "@tanstack/react-start";
import type { User } from "@supabase/supabase-js";
import { getSupabaseServerClient } from "./supabase.server";

export interface AuthSession {
  user: {
    id: string;
    email: string | undefined;
  } | null;
}

/**
 * Returns the current authenticated user from the request session, or null.
 * Safe to call from loaders and components. Runs during SSR using the
 * request-scoped server client (cookie-based session validation).
 */
export const getSession = createServerFn({ method: "GET" }).handler(async () => {
  try {
    const supabase = getSupabaseServerClient();
    const {
      data: { user },
    } = await supabase.auth.getUser();
    return { user: mapUser(user) } satisfies AuthSession;
  } catch {
    return { user: null } satisfies AuthSession;
  }
});

function mapUser(user: User | null): AuthSession["user"] {
  if (!user) return null;
  return { id: user.id, email: user.email };
}
