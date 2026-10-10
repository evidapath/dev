import type { ReactNode } from "react";
import {
  BookOpen,
  CheckCircle2,
  AlertTriangle,
  Lock,
  ShieldCheck,
  Compass,
  BarChart3,
  CalendarCheck,
  PiggyBank,
  ShieldAlert,
  FileCheck2,
  BadgeCheck,
} from "lucide-react";

export type Status = "LIVE" | "BETA" | "MOCK DATA" | "COMING LATER";

export function StatusBadge({ status }: { status: Status }) {
  const map: Record<Status, string> = {
    LIVE: "bg-primary/10 text-primary border-primary/30",
    BETA: "bg-bronze/10 text-bronze border-bronze/30",
    "MOCK DATA": "bg-secondary text-muted-foreground border-border",
    "COMING LATER": "bg-secondary/60 text-muted-foreground border-border/60",
  };
  return (
    <span
      className={`inline-flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded border ${map[status]}`}
    >
      {status}
    </span>
  );
}

export const SECTIONS = [
  { id: "welcome", label: "Welcome" },
  { id: "what-it-does", label: "What EvidaPath Does" },
  { id: "status-map", label: "Feature Status Map" },
  { id: "find-my-path", label: "Find My Path (Intake)" },
  { id: "results", label: "Results & Pathways" },
  { id: "create-account", label: "Creating an Account" },
  { id: "sign-in", label: "Signing In" },
  { id: "academic-readiness", label: "Academic Readiness" },
  { id: "dashboard", label: "Dashboard & Next Step" },
  { id: "discover", label: "Exploring Universities" },
  { id: "applications", label: "Applications" },
  { id: "offer-vault", label: "Offer Vault" },
  { id: "awards", label: "Scholarships & Aid" },
  { id: "documents", label: "Uploading Letters" },
  { id: "verification", label: "Verification Levels" },
  { id: "compare-offers", label: "Comparing Offers" },
  { id: "fund", label: "Family Capital Plan" },
  { id: "funding-gap", label: "Funding Gap" },
  { id: "sign-out", label: "Signing Out" },
  { id: "qa", label: "QA Testing Guide" },
  { id: "limitations", label: "Known Limitations" },
  { id: "report", label: "Report a Problem" },
];

export function Section({
  id,
  title,
  intro,
  children,
}: {
  id: string;
  title: string;
  intro?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section id={id} className="scroll-mt-24 space-y-4">
      <h2 className="text-2xl font-display font-bold text-foreground">{title}</h2>
      {intro && <p className="text-sm text-muted-foreground leading-relaxed">{intro}</p>}
      <div className="space-y-4">{children}</div>
    </section>
  );
}

export function FeatureBlock({
  purpose,
  why,
  steps,
  expected,
}: {
  purpose: string;
  why: string;
  steps: string[];
  expected: string;
}) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="rounded-xl border border-border bg-card p-4">
          <div className="text-[10px] font-semibold uppercase tracking-wide text-muted-foreground mb-1">
            What it does
          </div>
          <p className="text-sm text-foreground">{purpose}</p>
        </div>
        <div className="rounded-xl border border-border bg-card p-4">
          <div className="text-[10px] font-semibold uppercase tracking-wide text-muted-foreground mb-1">
            Why you'd use it
          </div>
          <p className="text-sm text-foreground">{why}</p>
        </div>
      </div>
      <div className="rounded-xl border border-border bg-secondary/30 p-4">
        <div className="text-[10px] font-semibold uppercase tracking-wide text-muted-foreground mb-2">
          How to use it
        </div>
        <ol className="list-decimal list-inside space-y-1.5 text-sm text-foreground">
          {steps.map((s, i) => (
            <li key={i}>{s}</li>
          ))}
        </ol>
      </div>
      <div className="rounded-xl border border-primary/30 bg-primary/5 p-4">
        <div className="text-[10px] font-semibold uppercase tracking-wide text-primary mb-1 flex items-center gap-1">
          <CheckCircle2 className="w-3.5 h-3.5" /> What should happen next
        </div>
        <p className="text-sm text-foreground">{expected}</p>
      </div>
    </div>
  );
}

export function ScreenshotPlaceholder({
  label,
  note,
  src,
}: {
  label: string;
  note?: string;
  src?: string;
}) {
  if (src) {
    return (
      <div className="rounded-xl border border-border bg-card overflow-hidden space-y-2">
        <img
          src={src}
          alt={label}
          className="w-full h-auto object-cover max-h-[450px] border-b border-border"
          loading="lazy"
        />
        <div className="p-3 text-center">
          <p className="text-xs font-semibold text-foreground">{label}</p>
          {note && <p className="text-[11px] text-muted-foreground mt-0.5">{note}</p>}
        </div>
      </div>
    );
  }
  return (
    <div className="rounded-xl border border-dashed border-border bg-secondary/20 p-8 text-center">
      <div className="w-10 h-10 mx-auto rounded-lg bg-secondary flex items-center justify-center mb-3">
        <BookOpen className="w-5 h-5 text-muted-foreground" />
      </div>
      <p className="text-sm font-semibold text-foreground">{label}</p>
      {note && <p className="text-xs text-muted-foreground mt-1">{note}</p>}
      <p className="text-[11px] text-muted-foreground mt-2 italic">
        Authenticated screenshot placeholder — capture manually from a logged-in session.
      </p>
    </div>
  );
}

export function GuideHeader() {
  return (
    <div className="space-y-3 border-b border-border pb-8">
      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold">
        <BookOpen className="w-3.5 h-3.5" />
        <span>Internal Documentation</span>
      </div>
      <h1 className="text-3xl sm:text-4xl font-display font-extrabold text-foreground">
        EvidaPath User &amp; QA Guide
      </h1>
      <p className="text-sm text-muted-foreground leading-relaxed max-w-2xl">
        A living guide documenting the EvidaPath application as it actually exists today. For QA
        testers, new users, and the product team. This page documents real, current behavior —
        planned functionality is labeled, not described as operational.
      </p>
      <div className="flex flex-wrap items-center gap-4 text-[11px] text-muted-foreground">
        <span>Guide last updated: September 2026</span>
        <span className="flex items-center gap-1">
          <ShieldCheck className="w-3.5 h-3.5 text-primary" /> Noindex / nofollow enabled
        </span>
      </div>
    </div>
  );
}

export function Sidebar({ active, onSelect }: { active: string; onSelect: (id: string) => void }) {
  return (
    <>
      <div className="rounded-2xl border border-border bg-card p-5 space-y-1">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-3">
          <BookOpen className="w-3.5 h-3.5" />
          Guide Contents
        </div>
        {SECTIONS.map((s) => (
          <a
            key={s.id}
            href={`#${s.id}`}
            onClick={() => onSelect(s.id)}
            className={`block rounded-lg px-3 py-2 text-sm transition-colors ${
              active === s.id
                ? "bg-primary/10 text-primary font-semibold"
                : "text-muted-foreground hover:text-foreground hover:bg-secondary/60"
            }`}
          >
            {s.label}
          </a>
        ))}
      </div>
      <div className="mt-4 flex items-center gap-2 text-[11px] text-muted-foreground bg-secondary/50 border border-border rounded-lg px-3 py-2">
        <Lock className="w-3.5 h-3.5 shrink-0" />
        <span>Unlisted internal page. Not in navigation or sitemap. Noindex / nofollow.</span>
      </div>
    </>
  );
}

export {
  Compass,
  BarChart3,
  CalendarCheck,
  PiggyBank,
  ShieldAlert,
  FileCheck2,
  BadgeCheck,
  AlertTriangle,
  Lock,
  ShieldCheck,
};
