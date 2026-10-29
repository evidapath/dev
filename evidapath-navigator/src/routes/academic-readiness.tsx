import { createFileRoute, Link } from "@tanstack/react-router";
import { requireAuth } from "../lib/route-guard";
import { useState } from "react";
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
    predictedGrade: "38-40 points",
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
      .then(() => setSubmitted(true))
      .catch((err: Error) => {
        console.error("[academic-readiness] GHL submit failed:", err);
        toast.error("Could not submit — please check your connection and try again.");
      })
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
        <div className="flex items-center gap-2 text-[11px] text-muted-foreground bg-secondary/50 border border-border rounded-lg px-3 py-2 max-w-xl mx-auto">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-bronze" />
          <span>
            Illustrative product preview. Live analysis will use verified EvidaPath data as datasets
            are built and verified.
          </span>
        </div>
      </div>

      {submitted ? (
        <div className="bg-card border border-border rounded-3xl p-8 sm:p-12 text-center space-y-6 shadow-sm">
          <div className="w-14 h-14 bg-primary/10 text-primary rounded-full flex items-center justify-center mx-auto">
            <CheckCircle2 className="w-7 h-7" />
          </div>
          <div className="space-y-2">
            <h2 className="text-2xl font-display font-bold text-foreground">
              Readiness Profile Diagnostic Initialized
            </h2>
            <p className="text-sm text-muted-foreground max-w-md mx-auto">
              Your profile ({formData.curriculum}, {formData.predictedGrade},{" "}
              {formData.targetSubject}) has been recorded. Live readiness analysis will map your
              evidence against verified institutional data as datasets are added.
            </p>
          </div>

          <div className="bg-secondary/50 rounded-2xl p-6 border border-border max-w-lg mx-auto text-left space-y-3 text-xs">
            <div className="flex justify-between">
              <span className="text-muted-foreground">High-Alignment Institutions:</span>
              <span className="font-mono font-medium text-muted-foreground">
                Pending verified data
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Actionable Prerequisite Gaps:</span>
              <span className="font-mono font-medium text-muted-foreground">
                Pending verified data
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Budget Envelope:</span>
              <span className="font-mono font-bold text-foreground">
                ${Number(formData.annualBudget).toLocaleString()}/yr
              </span>
            </div>
          </div>

          <div className="pt-4 flex flex-col sm:flex-row justify-center gap-3">
            <Link to="/discover">
              <Button className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold px-6">
                Explore Matching Pathways →
              </Button>
            </Link>
            <Link to="/plan">
              <Button
                variant="outline"
                className="border-border text-foreground hover:bg-secondary"
              >
                View My Action Roadmap
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
