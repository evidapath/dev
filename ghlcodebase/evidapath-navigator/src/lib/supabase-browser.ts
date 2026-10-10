import { createBrowserClient } from "@supabase/ssr";
import type { SupabaseClient } from "@supabase/supabase-js";

// Browser-safe (publishable) credentials. These use the VITE_ prefix and are
// intentionally shipped to the client bundle — they only carry publishable
// anon/publishable privileges, never the service role key.
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  // Fail loudly in dev so misconfiguration is obvious; guard against crashes in SSR.
  if (import.meta.env.DEV) {
    console.warn(
      "[EvidaPath] Missing VITE_SUPABASE_URL or VITE_SUPABASE_ANON_KEY. Auth will not function until these are set.",
    );
  }
}

let cached: SupabaseClient | null = null;

/**
 * Singleton Supabase browser client used by the login form and session
 * restoration on the client. Safe to import from any client component.
 */
export function getSupabaseBrowserClient(): SupabaseClient {
  if (cached) return cached;
  cached = createBrowserClient(supabaseUrl ?? "", supabaseAnonKey ?? "");
  return cached;
}
