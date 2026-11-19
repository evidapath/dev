import { useEffect, useRef, useState } from "react";
import { useRouterState, Link } from "@tanstack/react-router";
import { ArrowLeft, CheckCircle2, MessageSquareHeart, X } from "lucide-react";
import { submitGhlForm } from "../lib/ghl";
import { useAuth } from "./AuthContext";
import { Button } from "./ui/button";

// Short site-improvement survey that slides in from the right. Four one-tap questions, then an
// optional comment. It waits until the student has used the site for a while (time or pages
// seen), never shows on sign-in, and doesn't come back for months once answered or closed.
// Answers go to GHL only when the student presses Send; closing part-way sends nothing.

const QUESTIONS = [
  {
    key: "visit_goal",
    label: "Visit Goal",
    q: "What did you come to EvidaPath to do?",
    options: [
      "Compare costs",
      "Check entry requirements",
      "Find scholarships",
      "Find universities that fit me",
      "Just looking around",
    ],
  },
  {
    key: "found_it",
    label: "Found What They Needed",
    q: "Did you find what you needed?",
    options: ["Yes", "Partly", "Not yet"],
  },
  {
    key: "improve_first",
    label: "Improve First",
    q: "What should we improve first?",
    options: [
      "Add more universities and courses",
      "More scholarships",
      "Clearer costs and entry requirements",
      "Deadlines and application help",
      "Make the site easier to use",
    ],
  },
  {
    key: "trust",
    label: "Trust In Figures",
    q: "How much do you trust the figures you saw?",
    options: ["Completely", "Mostly", "Not sure", "Not much"],
  },
] as const;

const KEY = "ep-feedback-prompt";
const SHOW_AFTER_MS = 45_000;
const SHOW_AFTER_PAGES = 3;
const QUIET_DAYS = { sent: 180, closed: 60 };

function readState(): { s: "sent" | "closed"; at: number } | null {
  try {
    const v = localStorage.getItem(KEY);
    return v ? JSON.parse(v) : null;
  } catch {
    return null;
  }
}
function writeState(s: "sent" | "closed") {
  try {
    localStorage.setItem(KEY, JSON.stringify({ s, at: Date.now() }));
  } catch {
    // Storage blocked (private mode): the prompt may show again next visit; harmless.
  }
}
function quiet(): boolean {
  const st = readState();
  if (!st) return false;
  return Date.now() - st.at < QUIET_DAYS[st.s] * 86_400_000;
}

export function FeedbackPrompt() {
  const { user } = useAuth();
  const path = useRouterState({ select: (s) => s.location.pathname });
  const [open, setOpen] = useState(false);
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [comment, setComment] = useState("");
  const [email, setEmail] = useState("");
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState(false);
  const pages = useRef(new Set<string>());

  const blocked = path.startsWith("/sign-in");

  // Show after enough time on the site, or after a few different pages.
  useEffect(() => {
    if (quiet()) return;
    const t = setTimeout(() => !blocked && setOpen(true), SHOW_AFTER_MS);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  useEffect(() => {
    pages.current.add(path);
    if (!blocked && pages.current.size >= SHOW_AFTER_PAGES && !quiet()) setOpen(true);
  }, [path, blocked]);
  useEffect(() => {
    if (user?.email && !email) setEmail(user.email);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  const close = () => {
    if (!sent) writeState("closed");
    setOpen(false);
  };
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && close();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, sent]);

  if (!open || blocked) return null;

  const choose = (key: string, value: string) => {
    setAnswers((a) => ({ ...a, [key]: value }));
    setTimeout(() => setStep((s) => s + 1), 180);
  };

  const send = () => {
    setSending(true);
    setError(false);
    const fields: Record<string, { label: string; value: string }> = {
      email: { label: "Email Address", value: email },
      comment: { label: "Comment", value: comment },
      feedback_page: { label: "Page", value: path },
    };
    for (const q of QUESTIONS) fields[q.key] = { label: q.label, value: answers[q.key] ?? "" };
    submitGhlForm("site-feedback", "Site Feedback", fields)
      .then(() => {
        writeState("sent");
        setSent(true);
        setTimeout(() => setOpen(false), 6000);
      })
      .catch((err: Error) => {
        console.error("[site-feedback] GHL submit failed:", err);
        setError(true);
      })
      .finally(() => setSending(false));
  };

  const total = QUESTIONS.length + 1;
  const current = QUESTIONS[step];
  const wantsMoreUnis = answers["improve_first"] === "Add more universities and courses";

  return (
    <div
      role="dialog"
      aria-labelledby="fb-title"
      className="fixed z-50 bottom-4 right-4 left-4 sm:left-auto sm:w-[360px] rounded-2xl border border-border bg-card shadow-2xl motion-safe:animate-in motion-safe:slide-in-from-right-full motion-safe:fade-in duration-500"
    >
      <div className="flex items-center justify-between gap-2 px-5 pt-4">
        <p
          id="fb-title"
          className="flex items-center gap-2 text-xs font-semibold text-primary uppercase tracking-wide"
        >
          <MessageSquareHeart className="w-4 h-4" />
          {sent ? "Thank you" : "Help us improve EvidaPath"}
        </p>
        <button
          type="button"
          onClick={close}
          aria-label="Close"
          className="rounded-full p-1 text-muted-foreground hover:bg-muted hover:text-foreground"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="px-5 pb-5 pt-3">
        {sent ? (
          <div className="flex items-start gap-2">
            <CheckCircle2 className="w-5 h-5 text-primary shrink-0 mt-0.5" />
            <p className="text-sm text-foreground">
              Got it. Your answers go straight to the team deciding what we build next.
            </p>
          </div>
        ) : current ? (
          <>
            <p className="font-display font-bold text-base text-foreground leading-snug">
              {current.q}
            </p>
            <div className="mt-3 flex flex-col gap-2">
              {current.options.map((o) => {
                const on = answers[current.key] === o;
                return (
                  <button
                    key={o}
                    type="button"
                    onClick={() => choose(current.key, o)}
                    aria-pressed={on}
                    className={`text-left text-sm rounded-xl border px-3.5 py-2.5 transition-colors ${
                      on
                        ? "border-primary bg-primary/10 text-foreground font-semibold"
                        : "border-border hover:border-primary/50 hover:bg-muted/50 text-foreground"
                    }`}
                  >
                    {o}
                  </button>
                );
              })}
            </div>
          </>
        ) : (
          <>
            <p className="font-display font-bold text-base text-foreground leading-snug">
              Anything else? (optional)
            </p>
            {wantsMoreUnis && (
              <p className="mt-1 text-xs text-muted-foreground">
                Tell us which ones:{" "}
                <Link
                  to="/universities"
                  hash="request-university"
                  onClick={send}
                  className="font-semibold text-primary hover:underline"
                >
                  request a university or course
                </Link>
                .
              </p>
            )}
            <textarea
              rows={3}
              maxLength={1000}
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="What was missing, confusing or wrong?"
              className="mt-3 w-full rounded-xl border border-input bg-background px-3 py-2 text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
            />
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email, if you'd like a reply (optional)"
              aria-label="Email (optional)"
              className="mt-2 w-full h-9 rounded-xl border border-input bg-background px-3 text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
            />
            {error && (
              <p className="mt-2 text-xs text-destructive">
                Couldn't send. Check your connection and try again.
              </p>
            )}
            <Button onClick={send} disabled={sending} className="mt-3 w-full text-sm">
              {sending ? "Sending…" : "Send"}
            </Button>
          </>
        )}

        {!sent && (
          <div className="mt-4 flex items-center justify-between">
            <button
              type="button"
              onClick={() => setStep((s) => Math.max(0, s - 1))}
              disabled={step === 0}
              className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground disabled:invisible"
            >
              <ArrowLeft className="w-3 h-3" /> Back
            </button>
            <div className="flex gap-1.5" aria-label={`Question ${step + 1} of ${total}`}>
              {Array.from({ length: total }).map((_, i) => (
                <span
                  key={i}
                  className={`h-1.5 rounded-full transition-all ${
                    i === step
                      ? "w-5 bg-primary"
                      : i < step
                        ? "w-1.5 bg-primary/60"
                        : "w-1.5 bg-border"
                  }`}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
