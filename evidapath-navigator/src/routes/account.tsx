import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { useServerFn } from "@tanstack/react-start";
import {
  UserCircle,
  Trash2,
  AlertTriangle,
  Loader2,
  ShieldAlert,
  CheckCircle2,
  ArrowLeft,
  FileText,
  Vault,
  Award,
  ClipboardList,
} from "lucide-react";
import { Button } from "../components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "../components/ui/dialog";
import { Input } from "../components/ui/input";
import { useAuth } from "../components/AuthContext";
import { requireAuth } from "../lib/route-guard";
import { getDeletionSummary, deleteAccount } from "../lib/account-deletion.functions";
import type { DeletionSummary } from "../lib/account-deletion.server";

export const Route = createFileRoute("/account")({
  beforeLoad: ({ context, location }) => requireAuth(context, location.pathname),
  head: () => ({
    meta: [
      { title: "Account — EvidaPath" },
      {
        name: "description",
        content: "Manage your EvidaPath account, session, and data.",
      },
      { property: "og:title", content: "Account — EvidaPath" },
      {
        property: "og:description",
        content: "Manage your EvidaPath account, session, and data.",
      },
      { name: "robots", content: "noindex, nofollow" },
    ],
  }),
  component: AccountPage,
});

function AccountPage() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const fetchSummary = useServerFn(getDeletionSummary);
  const runDelete = useServerFn(deleteAccount);

  const [summary, setSummary] = useState<DeletionSummary | null>(null);
  const [summaryLoading, setSummaryLoading] = useState(true);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [typed, setTyped] = useState("");
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);

  useEffect(() => {
    let active = true;
    fetchSummary()
      .then((s) => {
        if (active) {
          setSummary(s);
          setSummaryLoading(false);
        }
      })
      .catch(() => {
        if (active) setSummaryLoading(false);
      });
    return () => {
      active = false;
    };
  }, [fetchSummary]);

  const CONFIRM_WORD = "DELETE";
  const canDelete = typed.trim() === CONFIRM_WORD && !deleting;

  async function handleDelete() {
    setError(null);
    setDeleting(true);
    try {
      await runDelete();
      // Deletion succeeded server-side. Clear local session state immediately.
      await signOut();
      setDeleting(false);
      setDone(true);
    } catch {
      setDeleting(false);
      setError(
        "Account deletion could not be completed. Your data has not been fully removed. Please try again or contact support if the problem persists.",
      );
    }
  }

  if (done) {
    return (
      <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 py-16 bg-background">
        <div className="max-w-md text-center space-y-5">
          <div className="w-14 h-14 mx-auto rounded-full bg-primary/10 flex items-center justify-center">
            <CheckCircle2 className="w-7 h-7 text-primary" />
          </div>
          <h1 className="text-2xl font-display font-bold text-foreground">
            Your EvidaPath account has been deleted.
          </h1>
          <p className="text-sm text-muted-foreground leading-relaxed">
            Your profile, applications, offers, awards, uploaded documents, enrollment decisions,
            and outcomes have been permanently removed. This action cannot be undone.
          </p>
          <Button
            onClick={() => navigate({ to: "/" })}
            className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold"
          >
            Return to EvidaPath
          </Button>
        </div>
      </div>
    );
  }

  const summaryRows = summary
    ? [
        { label: "Applications", value: summary.applications, icon: ClipboardList },
        { label: "Offers", value: summary.offers, icon: Vault },
        { label: "Awards / Aid", value: summary.awards, icon: Award },
        { label: "Uploaded documents", value: summary.documents, icon: FileText },
      ]
    : [];

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Header */}
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-secondary text-muted-foreground text-xs font-semibold">
          <UserCircle className="w-3.5 h-3.5" />
          <span>Account</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-display font-extrabold text-foreground">
          Account &amp; data
        </h1>
        <p className="text-sm text-muted-foreground leading-relaxed">
          Signed in as{" "}
          <span className="font-medium text-foreground">{user?.email ?? "EvidaPath member"}</span>.
          Manage your session and private EvidaPath data.
        </p>
      </div>

      {/* Session card */}
      <section className="rounded-2xl border border-border bg-card p-6 space-y-4">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div className="space-y-1">
            <h2 className="font-display font-bold text-foreground text-base">Session</h2>
            <p className="text-xs text-muted-foreground leading-relaxed max-w-md">
              You are authenticated through Supabase Auth. EvidaPath accesses your data only through
              your authenticated session, subject to Row Level Security.
            </p>
          </div>
          <Button
            variant="outline"
            onClick={async () => {
              await signOut();
              navigate({ to: "/" });
            }}
          >
            Sign out
          </Button>
        </div>
      </section>

      {/* Danger zone */}
      <section className="rounded-2xl border border-bronze/40 bg-bronze/[0.03] p-6 space-y-5">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-bronze" />
          <h2 className="font-display font-bold text-foreground text-base">Delete account</h2>
        </div>

        <p className="text-sm text-muted-foreground leading-relaxed">
          Deleting your EvidaPath account will{" "}
          <span className="font-semibold text-foreground">permanently remove</span>:
        </p>
        <ul className="text-sm text-muted-foreground space-y-1.5 pl-1">
          {[
            "your profile / account",
            "applications",
            "offers",
            "uploaded offer / scholarship documents",
            "awards & financial-aid records",
            "enrollment decisions",
            "outcomes",
            "other private EvidaPath data tied to your account",
          ].map((item) => (
            <li key={item} className="flex items-center gap-2">
              <span className="w-1 h-1 rounded-full bg-bronze" />
              {item}
            </li>
          ))}
        </ul>

        <div className="flex items-start gap-2 text-xs text-bronze bg-bronze/10 border border-bronze/20 rounded-lg p-3">
          <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
          <span>This action cannot be undone.</span>
        </div>

        {/* Summary */}
        <div className="rounded-xl border border-border bg-background p-4">
          <p className="text-[11px] uppercase tracking-wider text-muted-foreground font-semibold mb-3">
            Data that will be removed
          </p>
          {summaryLoading ? (
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              Counting your records…
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {summaryRows.map((row) => {
                const Icon = row.icon;
                return (
                  <div key={row.label} className="space-y-1">
                    <div className="flex items-center gap-1.5 text-muted-foreground">
                      <Icon className="w-3.5 h-3.5" />
                      <span className="text-[11px]">{row.label}</span>
                    </div>
                    <p className="text-lg font-display font-bold text-foreground">{row.value}</p>
                  </div>
                );
              })}
            </div>
          )}
          <p className="text-[11px] text-muted-foreground mt-3">
            Informational only. Deletion is not conditional on these counts.
          </p>
        </div>

        {error && (
          <div className="flex items-start gap-2 text-xs text-destructive bg-destructive/5 border border-destructive/20 rounded-lg p-3">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <Button
          variant="outline"
          onClick={() => {
            setTyped("");
            setError(null);
            setConfirmOpen(true);
          }}
          className="border-bronze/50 text-bronze hover:bg-bronze/10 font-semibold"
        >
          <Trash2 className="w-4 h-4" />
          Delete my account
        </Button>
      </section>

      <div>
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          Back to dashboard
        </Link>
      </div>

      {/* Confirmation modal */}
      <Dialog open={confirmOpen} onOpenChange={setConfirmOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-foreground">
              <ShieldAlert className="w-5 h-5 text-bronze" />
              Confirm permanent deletion
            </DialogTitle>
            <DialogDescription className="text-muted-foreground">
              This will permanently delete your account and all private EvidaPath data listed above.
              You will be signed out immediately. This action cannot be undone.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-3 py-2">
            <p className="text-sm text-foreground">
              To confirm, type{" "}
              <span className="font-mono font-bold text-bronze">{CONFIRM_WORD}</span> below:
            </p>
            <Input
              autoFocus
              value={typed}
              onChange={(e) => setTyped(e.target.value)}
              placeholder={CONFIRM_WORD}
              className="font-mono"
              disabled={deleting}
            />
          </div>

          {error && (
            <div className="flex items-start gap-2 text-xs text-destructive bg-destructive/5 border border-destructive/20 rounded-lg p-3">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <DialogFooter className="gap-2">
            <Button variant="outline" onClick={() => setConfirmOpen(false)} disabled={deleting}>
              Cancel
            </Button>
            <Button
              onClick={handleDelete}
              disabled={!canDelete}
              className="bg-bronze hover:bg-bronze/90 text-white font-semibold"
            >
              {deleting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Deleting account…
                </>
              ) : (
                <>
                  <Trash2 className="w-4 h-4" />
                  Permanently delete my account
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function AlertCircle({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="8" x2="12" y2="12" />
      <line x1="12" y1="16" x2="12.01" y2="16" />
    </svg>
  );
}
