import type { AuthSession } from "./auth.functions";

// The root beforeLoad used to ask the server for the session on every page change
// (and on every link hover, via preload): ~250–400ms before anything moved. In the
// browser we remember the last answer instead. AuthContext keeps it current from
// Supabase's sign-in/sign-out events, and it expires after a few minutes anyway.
// This only decides which pages to show; server functions and RLS still check the
// real session on every data request.
const TTL_MS = 5 * 60_000;
let cached: { session: AuthSession; at: number } | null = null;

export function cachedSession(): AuthSession | null {
  if (typeof window === "undefined" || !cached) return null;
  return Date.now() - cached.at < TTL_MS ? cached.session : null;
}

export function rememberSession(session: AuthSession) {
  if (typeof window !== "undefined") cached = { session, at: Date.now() };
}
