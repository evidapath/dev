import { createFileRoute, Link } from "@tanstack/react-router";
import { requireAuth } from "../lib/route-guard";
import { useMemo, useState } from "react";
import {
  Sparkles,
  ArrowRight,
  CheckCircle2,
  ShieldCheck,
  User,
  Mail,
  Globe,
  BookOpen,
  DollarSign,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "../components/ui/button";
import { submitGhlForm } from "../lib/ghl";
import { useLiveData } from "../lib/use-live-data";
import { analyze, type DecisionAnalysis, type StudentInput } from "../lib/decision-engine";
import { BUDGET_MAX } from "../lib/budget";
import type { University } from "../lib/mock-data";
import { canonicalLink, ogUrlMeta } from "../lib/seo";

export const Route = createFileRoute("/academic-readiness")({
  head: () => ({
    meta: [
      { title: "Academic Readiness Profile — EvidaPath" },
      {
        name: "description",
        content:
          "Turn your academic record into a decision map. Diagnostic starting point for grades, curriculum, geographic ambitions, and financial fit.",
      },
      { property: "og:title", content: "Academic Readiness Profile — EvidaPath" },
      {
        property: "og:description",
        content: "Diagnostic engine mapping current evidence to viable university pathways.",
      },
      ogUrlMeta("/academic-readiness"),
    ],
    links: [canonicalLink("/academic-readiness")],
  }),
  beforeLoad: ({ context, location }) => requireAuth(context, location.pathname),
  component: AcademicReadinessPage,
});

function AcademicReadinessPage() {
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    curriculum: "IB Diploma",
    predictedGrade: "Strong: IB 37-39 / A*AA / GPA 3.8-3.9",
    targetSubject: "Computer Science",
    preferredRegion: "Global / Flexible",
    annualBudget: "40000",
  });

  const [submitted, setSubmitted] = useState(false);
  const [sending, setSending] = useState(false);

  // Only confirm once GHL acknowledges receipt; previously the fetch error was
  // swallowed and "has been recorded" showed even when nothing was recorded.
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSending(true);
    submitGhlForm("academic-readiness-profile", "Academic Readiness Profile", {
      first_name: { label: "First Name", value: formData.firstName },
      last_name: { label: "Last Name", value: formData.lastName },
      email: { label: "Email Address", value: formData.email },
      curriculum: { label: "Curriculum", value: formData.curriculum },
      predicted_grade: { label: "Predicted Grade", value: formData.predictedGrade },
      target_subject: { label: "Target Subject", value: formData.targetSubject },
      preferred_region: { label: "Preferred Region", value: formData.preferredRegion },
      annual_budget: { label: "Annual Budget (USD)", value: formData.annualBudget },
    })
      .catch((err: Error) => {
        // The readiness map is computed locally, so show it even if the copy
        // sent to the EvidaPath team didn't go through.
        console.error("[academic-readiness] GHL submit failed:", err);
        toast.error("Your map is below, but we couldn't send a copy to the EvidaPath team.");
      })
      .then(() => setSubmitted(true))
      .finally(() => setSending(false));
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-10">
      {/* Header */}
      <div className="text-center space-y-3 max-w-2xl mx-auto">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Diagnostic Engine</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-display font-extrabold text-foreground">
          Turn your academic record into a decision map.
        </h1>
        <p className="text-sm sm:text-base text-muted-foreground leading-relaxed">
          Enter your current academic metrics, intended subject, and financial boundary. The
          diagnostic engine maps where your evidence creates opportunity and which levers you can
          still change.
        </p>
      </div>

      {submitted ? (
        <div className="bg-card border border-border rounded-3xl p-6 sm:p-10 space-y-6 shadow-sm">
          <div className="text-center space-y-2">
            <div className="w-12 h-12 bg-primary/10 text-primary rounded-full flex items-center justify-center mx-auto">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <h2 className="text-2xl font-display font-bold text-foreground">Your readiness map</h2>
            <p className="text-sm text-muted-foreground max-w-xl mx-auto">
              {formData.curriculum} · {formData.predictedGrade.replace(/^[^:]+:\s*/, "")} ·{" "}
              {formData.targetSubject} · up to ${Number(formData.annualBudget).toLocaleString()}/yr,
              compared with every university's published requirements and costs.
            </p>
          </div>
          <ReadinessResults
            input={{
              curriculum: formData.curriculum,
              gradeBand: formData.predictedGrade,
              subject: formData.targetSubject,
              budgetUsd:
                Number(formData.annualBudget) >= 80000
                  ? BUDGET_MAX
                  : Number(formData.annualBudget) + 5000,
              citizenship: "",
            }}
          />
          <div className="pt-4 flex flex-col sm:flex-row justify-center gap-3">
            <Link to="/find-my-path">
              <Button className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold px-6">
                Save universities to your path →
              </Button>
            </Link>
            <Link to="/plan">
              <Button
                variant="outline"
                className="border-border text-foreground hover:bg-secondary"
              >
                View my plan
              </Button>
            </Link>
          </div>
        </div>
      ) : (
        <div className="bg-card border border-border rounded-3xl p-6 sm:p-10 shadow-sm">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="border-b border-border pb-4">
              <h3 className="font-display font-bold text-lg text-foreground">
                1. Candidate Profile & Contact
              </h3>
              <p className="text-xs text-muted-foreground">
                Your data is held strictly private and used solely to build your analytical profile.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase text-muted-foreground mb-1.5">
                  First Name
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Alex"
                  value={formData.firstName}
                  onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
                  className="w-full h-10 px-3 rounded-lg border border-input bg-background text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase text-muted-foreground mb-1.5">
                  Last Name
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Mercer"
                  value={formData.lastName}
                  onChange={(e) => setFormData({ ...formData, lastName: e.target.value })}
                  className="w-full h-10 px-3 rounded-lg border border-input bg-background text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase text-muted-foreground mb-1.5">
                  Email Address
                </label>
                <input
                  type="email"
                  required
                  placeholder="alex@example.com"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full h-10 px-3 rounded-lg border border-input bg-background text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
                />
              </div>
            </div>

            <div className="border-b border-border pt-4 pb-4">
              <h3 className="font-display font-bold text-lg text-foreground">
                2. Academic Evidence & Focus
              </h3>
              <p className="text-xs text-muted-foreground">
                Provide your secondary curriculum and estimated grade bands.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase text-muted-foreground mb-1.5">
                  Curriculum
                </label>
                <select
                  value={formData.curriculum}
                  onChange={(e) => setFormData({ ...formData, curriculum: e.target.value })}
                  className="w-full h-10 px-3 rounded-lg border border-input bg-background text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
                >
                  <option>IB Diploma</option>
                  <option>Cambridge A-Levels</option>
                  <option>US High School Diploma + APs</option>
                  <option>German Abitur</option>
                  <option>National Curriculum / Other</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase text-muted-foreground mb-1.5">
                  Predicted / Current Grade Band
                </label>
                <select
                  value={formData.predictedGrade}
                  onChange={(e) => setFormData({ ...formData, predictedGrade: e.target.value })}
                  className="w-full h-10 px-3 rounded-lg border border-input bg-background text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
                >
                  <option>Top Tier: IB 40+ / A*A*A / GPA 4.0</option>
                  <option>Strong: IB 37-39 / A*AA / GPA 3.8-3.9</option>
                  <option>Competitive: IB 34-36 / AAA-AAB / GPA 3.6-3.7</option>
                  <option>Foundation: IB 30-33 / ABB-BBB / GPA 3.3-3.5</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase text-muted-foreground mb-1.5">
                  Intended Degree Field
                </label>
                <input
                  type="text"
                  placeholder="e.g. Computer Science, Economics, Aerospace"
                  value={formData.targetSubject}
                  onChange={(e) => setFormData({ ...formData, targetSubject: e.target.value })}
                  className="w-full h-10 px-3 rounded-lg border border-input bg-background text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase text-muted-foreground mb-1.5">
                  Target Annual Family Budget (USD)
                </label>
                <select
                  value={formData.annualBudget}
                  onChange={(e) => setFormData({ ...formData, annualBudget: e.target.value })}
                  className="w-full h-10 px-3 rounded-lg border border-input bg-background text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
                >
                  <option value="20000">Under $25,000 / yr (European Public)</option>
                  <option value="40000">$25,000 - $45,000 / yr (Value Global)</option>
                  <option value="60000">$45,000 - $65,000 / yr (UK / Canada Tier-1)</option>
                  <option value="80000">$65,000+ / yr (Comprehensive Global)</option>
                </select>
              </div>
            </div>

            <div className="pt-6 border-t border-border flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <ShieldCheck className="w-4 h-4 text-primary" />
                <span>
                  Zero spam guarantee. Results delivered directly in interactive decision suite.
                </span>
              </div>

              <Button
                type="submit"
                disabled={sending}
                className="w-full sm:w-auto bg-primary hover:bg-primary/90 text-primary-foreground font-semibold px-8 h-11 rounded-xl text-sm"
              >
                {sending ? "Submitting…" : "Create My Readiness Profile"}
              </Button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

function ReadinessResults({ input }: { input: StudentInput }) {
  const { data } = useLiveData();
  const groups = useMemo(() => {
    if (!data) return null;
    const runs = data.universities
      .map((u) => ({ u, a: analyze(u, input, data.scholarships, [], data.fx) }))
      .filter((r) => r.a.offersSubject);
    const by = (pred: (r: (typeof runs)[number]) => boolean) => runs.filter(pred);
    return {
      total: runs.length,
      meets: by((r) => r.a.academic.level === "strong"),
      edge: by((r) => r.a.academic.level === "edge" || r.a.academic.level === "gap"),
      other: by((r) => r.a.academic.level === "unknown"),
      subjects: by((r) => r.a.academic.subjects.length > 0),
    };
  }, [data, input]);

  if (!groups)
    return (
      <div className="space-y-2" aria-busy="true">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-14 rounded-xl bg-secondary/60 animate-pulse" />
        ))}
      </div>
    );

  const List = ({
    title,
    tone,
    rows,
    note,
  }: {
    title: string;
    tone: string;
    rows: { u: University; a: DecisionAnalysis }[];
    note: string;
  }) => (
    <details
      className="rounded-xl border border-border bg-background group"
      open={rows.length > 0 && rows.length <= 8}
    >
      <summary className="flex items-center justify-between gap-3 cursor-pointer list-none p-4">
        <span className="font-semibold text-sm text-foreground">{title}</span>
        <span className={`text-xs font-mono font-bold px-2 py-0.5 rounded-full ${tone}`}>
          {rows.length}
        </span>
      </summary>
      <div className="px-4 pb-4 space-y-2">
        <p className="text-xs text-muted-foreground">{note}</p>
        <ul className="divide-y divide-border">
          {rows.map(({ u, a }) => (
            <li key={u.id} className="py-2 flex items-start justify-between gap-3 text-xs">
              <div className="min-w-0">
                <p className="font-medium text-foreground">
                  {u.flag} {u.name}
                </p>
                <p className="text-muted-foreground">
                  {a.programName} — {a.academic.headline}
                </p>
              </div>
              <Link
                to="/analyze"
                search={{ uni: u.id }}
                className="shrink-0 text-primary font-semibold hover:underline"
              >
                Analyze
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </details>
  );

  return (
    <div className="space-y-3 text-left">
      <p className="text-xs text-muted-foreground">
        {groups.total} universities in EvidaPath offer {input.subject || "your subject"} or a close
        match.
      </p>
      <List
        title="Your grades meet the published requirement"
        tone="bg-primary/10 text-primary"
        rows={groups.meets}
        note="Meeting a published minimum doesn't guarantee an offer — competitive courses often admit above it."
      />
      <List
        title="Borderline or below the published requirement"
        tone="bg-bronze/10 text-bronze"
        rows={groups.edge}
        note="Your predicted grades are the main lever here, or keep these as reach options."
      />
      <List
        title="Holistic or no grade we can compare"
        tone="bg-secondary text-muted-foreground"
        rows={groups.other}
        note="These review applications as a whole, or publish requirements only in another curriculum's terms."
      />
      <List
        title="Prerequisite subjects to check"
        tone="bg-secondary text-muted-foreground"
        rows={groups.subjects}
        note="These name specific subjects you must take — open Analyze to see which."
      />
    </div>
  );
}
