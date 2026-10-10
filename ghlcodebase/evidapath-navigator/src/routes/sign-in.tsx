import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import {
  ArrowRight,
  ShieldCheck,
  LogIn,
  UserPlus,
  AlertCircle,
  Loader2,
  Mail,
  KeyRound,
  ArrowLeft,
  CheckCircle2,
} from "lucide-react";
import { Button } from "../components/ui/button";
import { EvidaPathMark } from "../components/brand/EvidaPathLogo";
import { getSupabaseBrowserClient } from "../lib/supabase-browser";
import { useAuth } from "../components/AuthContext";

export const Route = createFileRoute("/sign-in")({
  validateSearch: (search: Record<string, unknown>) => ({
    redirect: typeof search.redirect === "string" ? search.redirect : undefined,
  }),
  head: () => ({
    meta: [
      { title: "Sign In — EvidaPath" },
      {
        name: "description",
        content:
          "Sign in or create your EvidaPath account to continue building your education decision-intelligence profile.",
      },
      { property: "og:title", content: "Sign In — EvidaPath" },
      {
        property: "og:description",
        content: "Access your EvidaPath decision roadmap, readiness profile, and capital plan.",
      },
    ],
  }),
  component: SignInPage,
});

type Mode = "signin" | "signup" | "magic" | "reset";

function SignInPage() {
  const navigate = useNavigate();
  const { refresh, user } = useAuth();
  const { redirect } = Route.useSearch();

  const [mode, setMode] = useState<Mode>("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);

  // If an already-authenticated user lands on /sign-in (direct nav, back
  // button, or after an OAuth callback already resolved the session), bounce
  // them away to their intended destination. The safe `redirect` param wins;
  // otherwise authenticated users default to /dashboard.
  useEffect(() => {
    if (user) {
      navigate({ to: redirect ?? "/dashboard", replace: true });
    }
  }, [user, redirect, navigate]);

  function postLoginDestination(forMode: Mode): string {
    if (redirect) return redirect;
    return forMode === "signup" ? "/academic-readiness" : "/dashboard";
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setInfo(null);
    setLoading(true);

    try {
      const supabase = getSupabaseBrowserClient();

      if (mode === "signin") {
        const { error: signInError } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        if (signInError) throw signInError;
        await refresh();
        navigate({ to: postLoginDestination("signin") });
      } else if (mode === "signup") {
        const { data, error: signUpError } = await supabase.auth.signUp({
          email,
          password,
          options: {
            emailRedirectTo: `${window.location.origin}/sign-in?redirect=${encodeURIComponent(
              redirect ?? "/academic-readiness",
            )}`,
          },
        });
        if (signUpError) throw signUpError;
        // If email confirmation is required, no session is returned.
        if (!data.session) {
          setInfo(
            "Account created. Check your inbox for a verification link to confirm your email and continue.",
          );
          setLoading(false);
          return;
        }
        await refresh();
        navigate({ to: postLoginDestination("signup") });
      } else if (mode === "magic") {
        const { error: magicError } = await supabase.auth.signInWithOtp({
          email,
          options: {
            emailRedirectTo: `${window.location.origin}/sign-in?redirect=${encodeURIComponent(
              redirect ?? "/dashboard",
            )}`,
          },
        });
        if (magicError) throw magicError;
        setInfo("Magic link sent. Check your inbox to sign in — the link expires shortly.");
        setLoading(false);
      } else if (mode === "reset") {
        const { error: resetError } = await supabase.auth.resetPasswordForEmail(email, {
          redirectTo: `${window.location.origin}/sign-in?redirect=${encodeURIComponent(
            redirect ?? "/dashboard",
          )}`,
        });
        if (resetError) throw resetError;
        setInfo("Password reset link sent. Check your inbox to choose a new password.");
        setLoading(false);
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Authentication failed. Please try again.";
      setError(humanizeAuthError(message));
    } finally {
      setLoading(false);
    }
  }

  async function handleGoogle() {
    setError(null);
    setLoading(true);
    try {
      const supabase = getSupabaseBrowserClient();
      const { error: oauthError } = await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
          redirectTo: `${window.location.origin}/sign-in?redirect=${encodeURIComponent(
            redirect ?? "/dashboard",
          )}`,
          // Always show the Google account chooser instead of silently
          // reusing the last signed-in Google account.
          queryParams: {
            prompt: "select_account",
          },
        },
      });
      if (oauthError) throw oauthError;
      // Browser redirects to Google; nothing else to do here.
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Google sign-in failed. Please try again.";
      setError(humanizeAuthError(message));
      setLoading(false);
    }
  }

  const isMagicOrReset = mode === "magic" || mode === "reset";
  const showPassword = mode === "signin" || mode === "signup";

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 py-12 bg-secondary/20">
      <div className="w-full max-w-md">
        {/* Brand */}
        <div className="flex flex-col items-center text-center mb-8">
          <EvidaPathMark size={48} className="mb-3" />
          <h1 className="text-2xl font-display font-bold text-foreground">
            {mode === "signin" && "Welcome back to EvidaPath"}
            {mode === "signup" && "Create your EvidaPath account"}
            {mode === "magic" && "Sign in with a magic link"}
            {mode === "reset" && "Reset your password"}
          </h1>
          <p className="text-sm text-muted-foreground mt-1.5 max-w-xs">
            {mode === "signin" && "Sign in to continue building your decision roadmap."}
            {mode === "signup" &&
              "Start your Academic Readiness Profile and decision-intelligence journey."}
            {mode === "magic" && "We'll email a secure one-time sign-in link."}
            {mode === "reset" && "We'll email a link to choose a new password."}
          </p>
        </div>

        {/* Card */}
        <div className="bg-card border border-border rounded-2xl shadow-sm p-6 sm:p-8">
          {/* Mode toggle (only for signin/signup) */}
          {!isMagicOrReset && (
            <div className="grid grid-cols-2 gap-1 p-1 bg-secondary/60 rounded-lg mb-6">
              <button
                onClick={() => {
                  setMode("signin");
                  setError(null);
                  setInfo(null);
                }}
                className={`flex items-center justify-center gap-1.5 py-2 rounded-md text-sm font-medium transition-colors ${
                  mode === "signin"
                    ? "bg-card text-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                <LogIn className="w-4 h-4" />
                Sign In
              </button>
              <button
                onClick={() => {
                  setMode("signup");
                  setError(null);
                  setInfo(null);
                }}
                className={`flex items-center justify-center gap-1.5 py-2 rounded-md text-sm font-medium transition-colors ${
                  mode === "signup"
                    ? "bg-card text-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                <UserPlus className="w-4 h-4" />
                Sign Up
              </button>
            </div>
          )}

          {isMagicOrReset && (
            <button
              onClick={() => {
                setMode("signin");
                setError(null);
                setInfo(null);
              }}
              className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors mb-4"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              Back to sign in
            </button>
          )}

          {/* Google OAuth — shown above email form on Sign In / Sign Up tabs.
              Always visible; Supabase returns an error if the provider is misconfigured. */}
          {!isMagicOrReset && (
            <>
              <button
                onClick={handleGoogle}
                disabled={loading}
                className="w-full h-11 rounded-xl border border-input bg-background text-sm font-medium text-foreground hover:bg-secondary transition-colors flex items-center justify-center gap-2.5 disabled:opacity-60"
              >
                <GoogleIcon className="w-4 h-4" />
                Continue with Google
              </button>

              <div className="relative my-6">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t border-border" />
                </div>
                <div className="relative flex justify-center text-[11px] uppercase tracking-wider">
                  <span className="bg-card px-2 text-muted-foreground">or continue with email</span>
                </div>
              </div>
            </>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold uppercase text-muted-foreground mb-1.5">
                Email Address
              </label>
              <input
                type="email"
                required
                autoComplete="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full h-10 px-3 rounded-lg border border-input bg-background text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
              />
            </div>

            {showPassword && (
              <div>
                <label className="block text-xs font-semibold uppercase text-muted-foreground mb-1.5">
                  Password
                </label>
                <input
                  type="password"
                  required={mode !== "reset"}
                  minLength={mode === "signup" ? 6 : undefined}
                  autoComplete={mode === "signin" ? "current-password" : "new-password"}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full h-10 px-3 rounded-lg border border-input bg-background text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
                />
                {mode === "signup" && (
                  <p className="text-[11px] text-muted-foreground mt-1.5">
                    Minimum 6 characters. You may need to confirm your email before signing in.
                  </p>
                )}
              </div>
            )}

            {error && (
              <div className="flex items-start gap-2 text-xs text-destructive bg-destructive/5 border border-destructive/20 rounded-lg p-3">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            {info && (
              <div className="flex items-start gap-2 text-xs text-primary bg-primary/5 border border-primary/20 rounded-lg p-3">
                <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{info}</span>
              </div>
            )}

            <Button
              type="submit"
              disabled={loading}
              className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-semibold h-11 rounded-xl flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  {mode === "signin"
                    ? "Signing in…"
                    : mode === "signup"
                      ? "Creating account…"
                      : mode === "magic"
                        ? "Sending link…"
                        : "Sending reset email…"}
                </>
              ) : (
                <>
                  {mode === "signin" && "Sign In"}
                  {mode === "signup" && "Create Account"}
                  {mode === "magic" && (
                    <>
                      <Mail className="w-4 h-4" />
                      Send Magic Link
                    </>
                  )}
                  {mode === "reset" && (
                    <>
                      <KeyRound className="w-4 h-4" />
                      Send Reset Link
                    </>
                  )}
                  {mode !== "magic" && mode !== "reset" && <ArrowRight className="w-4 h-4" />}
                </>
              )}
            </Button>
          </form>

          {/* Secondary auth actions */}
          {mode === "signin" && (
            <div className="mt-4 flex flex-col gap-2 text-xs">
              <button
                onClick={() => {
                  setMode("magic");
                  setError(null);
                  setInfo(null);
                }}
                className="flex items-center justify-center gap-1.5 text-muted-foreground hover:text-foreground transition-colors"
              >
                <Mail className="w-3.5 h-3.5" />
                Sign in with a magic link instead
              </button>
              <button
                onClick={() => {
                  setMode("reset");
                  setError(null);
                  setInfo(null);
                }}
                className="flex items-center justify-center gap-1.5 text-muted-foreground hover:text-foreground transition-colors"
              >
                <KeyRound className="w-3.5 h-3.5" />
                Forgot password?
              </button>
            </div>
          )}

          <div className="mt-6 pt-5 border-t border-border flex items-center gap-2 text-[11px] text-muted-foreground">
            <ShieldCheck className="w-3.5 h-3.5 text-primary shrink-0" />
            <span>
              Secured by Supabase Auth. EvidaPath never sees your password and accesses your data
              only through your authenticated session.
            </span>
          </div>
        </div>

        <div className="mt-6 text-center text-sm text-muted-foreground">
          {mode === "signin" ? (
            <>
              New to EvidaPath?{" "}
              <button
                onClick={() => {
                  setMode("signup");
                  setError(null);
                  setInfo(null);
                }}
                className="font-semibold text-primary hover:underline"
              >
                Create an account
              </button>
            </>
          ) : (
            <>
              Already have an account?{" "}
              <button
                onClick={() => {
                  setMode("signin");
                  setError(null);
                  setInfo(null);
                }}
                className="font-semibold text-primary hover:underline"
              >
                Sign in
              </button>
            </>
          )}
        </div>

        <div className="mt-4 text-center">
          <Link
            to="/"
            className="text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            ← Back to EvidaPath
          </Link>
        </div>
      </div>
    </div>
  );
}

function humanizeAuthError(message: string): string {
  const lower = message.toLowerCase();
  if (lower.includes("invalid login credentials")) {
    return "Incorrect email or password. Please try again.";
  }
  if (lower.includes("email not confirmed")) {
    return "Please confirm your email address before signing in. Check your inbox for a verification link.";
  }
  if (lower.includes("user already registered")) {
    return "An account with this email already exists. Try signing in instead.";
  }
  if (lower.includes("password should be at least")) {
    return "Password must be at least 6 characters.";
  }
  if (lower.includes("rate limit")) {
    return "Too many attempts. Please wait a moment and try again.";
  }
  if (lower.includes("magic link") || lower.includes("otp")) {
    return "We couldn't send the link. Please try again in a moment.";
  }
  return message;
}

function GoogleIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" aria-hidden="true">
      <path
        fill="#4285F4"
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.27-4.74 3.27-8.1z"
      />
      <path
        fill="#34A853"
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84A11 11 0 0 0 12 23z"
      />
      <path
        fill="#FBBC05"
        d="M5.84 14.1a6.6 6.6 0 0 1 0-4.2V7.06H2.18a11 11 0 0 0 0 9.88l3.66-2.84z"
      />
      <path
        fill="#EA4335"
        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1A11 11 0 0 0 2.18 7.06l3.66 2.84C6.71 7.3 9.14 5.38 12 5.38z"
      />
    </svg>
  );
}
