import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import type { AuthSession } from "../lib/auth.functions";

// The Supabase browser client is imported lazily so the large @supabase/ssr +
// @supabase/supabase-js SDKs stay out of the shared root bundle. Only the
// /sign-in route and an authenticated session actually need them.
type SupabaseAuth = {
  auth: {
    getUser: () => Promise<{ data: { user: { id: string; email?: string } | null } }>;
    signOut: () => Promise<unknown>;
    getSession: () => Promise<{
      data: { session: { user?: { id: string; email?: string } | null } | null };
    }>;
    onAuthStateChange: (
      cb: (
        _event: string,
        session: { user?: { id: string; email?: string } | null } | null,
      ) => void,
    ) => { data: { subscription: { unsubscribe: () => void } } };
  };
};

let clientPromise: Promise<SupabaseAuth> | null = null;
async function getAuthClient(): Promise<SupabaseAuth> {
  if (!clientPromise) {
    clientPromise = import("../lib/supabase-browser").then((m) => {
      const client = m.getSupabaseBrowserClient();
      return client as unknown as SupabaseAuth;
    });
  }
  return clientPromise;
}

interface AuthContextValue extends AuthSession {
  loading: boolean;
  signOut: () => Promise<void>;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

/**
 * Provides the authenticated session to the client tree. The initial session is
 * resolved server-side (via the root beforeLoad → getSession) and passed in to
 * avoid a flash of unauthenticated state. On the client we subscribe to
 * Supabase auth changes so login/signup/sign-out reflect immediately.
 */
export function AuthContextProvider({
  initialSession,
  children,
}: {
  initialSession: AuthSession;
  children: ReactNode;
}) {
  const [session, setSession] = useState<AuthSession>(initialSession);
  const [loading, setLoading] = useState(false);

  const refresh = useCallback(async () => {
    try {
      const supabase = await getAuthClient();
      const {
        data: { user },
      } = await supabase.auth.getUser();
      setSession({ user: user ? { id: user.id, email: user.email } : null });
    } catch {
      setSession({ user: null });
    }
  }, []);

  useEffect(() => {
    let unsub: (() => void) | null = null;
    let active = true;
    getAuthClient()
      .then((supabase) => {
        if (!active) return;
        const { data: sub } = supabase.auth.onAuthStateChange((_event, session) => {
          const user = session?.user;
          setSession({ user: user ? { id: user.id, email: user.email } : null });
          setLoading(false);
        });
        unsub = () => sub.subscription.unsubscribe();
      })
      .catch(() => {
        /* Supabase not configured — session stays null */
      });
    return () => {
      active = false;
      unsub?.();
    };
  }, []);

  // After an OAuth/magic-link/email-verification redirect, Supabase exchanges
  // the code in the URL for a session. Detect a returning session and refresh
  // so the user is logged in on landing, then the sign-in route can route
  // them to their intended destination.
  useEffect(() => {
    let active = true;
    if (typeof window === "undefined") return;
    const hasReturnCode =
      window.location.search.includes("code=") ||
      window.location.search.includes("access_token") ||
      window.location.search.includes("error_description");
    if (!hasReturnCode) return;
    getAuthClient()
      .then(async (supabase) => {
        const {
          data: { session },
        } = await supabase.auth.getSession();
        if (!active) return;
        const user = session?.user;
        setSession({ user: user ? { id: user.id, email: user.email } : null });
      })
      .catch(() => {
        /* ignore — session stays as-is */
      });
    return () => {
      active = false;
    };
  }, []);

  const signOut = useCallback(async () => {
    try {
      const supabase = await getAuthClient();
      await supabase.auth.signOut();
    } catch {
      /* ignore — clear local state regardless */
    }
    setSession({ user: null });
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({ ...session, loading, signOut, refresh }),
    [session, loading, signOut, refresh],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthContextProvider");
  }
  return ctx;
}
