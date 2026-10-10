import { createFileRoute, Link } from "@tanstack/react-router";
import { requireAuth } from "../lib/route-guard";
import { useState } from "react";
import {
  CalendarCheck,
  CheckCircle2,
  Clock,
  ShieldCheck,
  ArrowRight,
  Target,
  Sparkles,
  Filter,
} from "lucide-react";
import { Button } from "../components/ui/button";
import { canonicalLink, ogUrlMeta } from "../lib/seo";

export const Route = createFileRoute("/plan")({
  head: () => ({
    meta: [
      { title: "EvidaPath Plan — Controllable Action Roadmap" },
      {
        name: "description",
        content:
          "Know what to do next. Organize academic interventions, test prep, prerequisites, and scholarship milestones by timing and controllability.",
      },
      { property: "og:title", content: "EvidaPath Plan — Know What To Do Next" },
      {
        property: "og:description",
        content: "Structured decision milestones prioritized by student controllability.",
      },
      ogUrlMeta("/plan"),
    ],
    links: [canonicalLink("/plan")],
  }),
  beforeLoad: ({ context, location }) => requireAuth(context, location.pathname),
  component: PlanPage,
});

interface ActionItem {
  id: string;
  title: string;
  category: "Academic Rigor" | "Testing" | "Financial / Scholarship" | "Strategic Pathway";
  timeline: string;
  gapAddressed: string;
  controllability: "High Control" | "Moderate Control";
  impact: "High" | "Structural";
  whyItMatters: string;
  completed: boolean;
}

function PlanPage() {
  const [filterCategory, setFilterCategory] = useState("All");

  const [actions, setActions] = useState<ActionItem[]>([
    {
      id: "a1",
      title: "Target predicted grade elevation in the most relevant advanced subject",
      category: "Academic Rigor",
      timeline: "Current term",
      gapAddressed:
        "Closes the gap between the student's current evidence and target program requirements",
      controllability: "High Control",
      impact: "High",
      whyItMatters:
        "Directly strengthens the academic evidence used to evaluate fit against target program prerequisites.",
      completed: false,
    },
    {
      id: "a2",
      title: "Complete timed practice for subject-specific admissions tests",
      category: "Testing",
      timeline: "Pre-test window",
      gapAddressed: "Addresses testing components used in shortlisting for selective programs",
      controllability: "High Control",
      impact: "High",
      whyItMatters:
        "Admissions tests are a controllable lever where preparation can materially affect outcomes for programs that use them.",
      completed: false,
    },
    {
      id: "a3",
      title: "Identify and prepare scholarship applications matched to eligibility",
      category: "Financial / Scholarship",
      timeline: "Ahead of deadlines",
      gapAddressed:
        "Reduces the family capital gap by pursuing funding the student is eligible for",
      controllability: "Moderate Control",
      impact: "Structural",
      whyItMatters:
        "Scholarships can change the financial picture meaningfully; applying to the right ones is a controllable action.",
      completed: false,
    },
    {
      id: "a4",
      title: "Verify diploma equivalency and documentation for alternative-pathway countries",
      category: "Strategic Pathway",
      timeline: "Ahead of application windows",
      gapAddressed: "Removes bureaucratic delays for credible alternative pathways",
      controllability: "High Control",
      impact: "Structural",
      whyItMatters:
        "Securing documentation early keeps alternative pathways viable as credible backups.",
      completed: true,
    },
    {
      id: "a5",
      title: "Draft and review an academic statement evidencing independent intellectual curiosity",
      category: "Academic Rigor",
      timeline: "Application window",
      gapAddressed: "Evidences qualities valued by holistic review committees",
      controllability: "High Control",
      impact: "High",
      whyItMatters:
        "Differentiates applicants with similar academic profiles during holistic review.",
      completed: false,
    },
  ]);

  const toggleAction = (id: string) => {
    setActions(actions.map((a) => (a.id === id ? { ...a, completed: !a.completed } : a)));
  };

  const filtered = actions.filter((a) => filterCategory === "All" || a.category === filterCategory);

  const completedCount = actions.filter((a) => a.completed).length;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      {/* Header */}
      <div className="max-w-3xl space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold">
          <CalendarCheck className="w-3.5 h-3.5" />
          <span>Decision Suite • Plan</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-display font-extrabold text-foreground">
          Know What to Do Next
        </h1>
        <p className="text-sm sm:text-base text-muted-foreground leading-relaxed">
          Rather than an overwhelming, generic checklist, EvidaPath organizes recommendations by
          importance, timing, and direct student controllability.
        </p>
        <div className="flex items-center gap-2 text-[11px] text-muted-foreground bg-secondary/50 border border-border rounded-lg px-3 py-2">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-bronze" />
          <span>
            Illustrative product preview. Live plans will be generated from your verified profile
            and target universities.
          </span>
        </div>
      </div>

      {/* Progress & Category Filter Bar */}
      <div className="bg-card border border-border rounded-2xl p-6 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-display font-bold text-lg text-foreground">Roadmap Progress</span>
            <span className="text-xs font-mono bg-primary/10 text-primary px-2 py-0.5 rounded font-semibold">
              {completedCount} of {actions.length} Completed
            </span>
          </div>
          <p className="text-xs text-muted-foreground mt-0.5">
            Focusing on levers with high student agency and structural impact.
          </p>
        </div>

        {/* Filter buttons */}
        <div className="flex flex-wrap gap-1.5">
          {["All", "Academic Rigor", "Testing", "Financial / Scholarship", "Strategic Pathway"].map(
            (cat) => (
              <button
                key={cat}
                onClick={() => setFilterCategory(cat)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  filterCategory === cat
                    ? "bg-primary text-primary-foreground font-semibold"
                    : "bg-secondary text-muted-foreground hover:text-foreground"
                }`}
              >
                {cat}
              </button>
            ),
          )}
        </div>
      </div>

      {/* Action Item Cards */}
      <div className="space-y-4">
        {filtered.map((item) => (
          <div
            key={item.id}
            onClick={() => toggleAction(item.id)}
            className={`cursor-pointer rounded-2xl border transition-all p-5 sm:p-6 ${
              item.completed
                ? "bg-secondary/40 border-border/60 opacity-80"
                : "bg-card border-border hover:border-primary/50 shadow-xs"
            }`}
          >
            <div className="flex flex-col sm:flex-row items-start justify-between gap-4">
              <div className="flex items-start gap-3.5">
                <div
                  className={`mt-0.5 w-6 h-6 rounded-md border flex items-center justify-center transition-colors ${
                    item.completed
                      ? "bg-primary border-primary text-primary-foreground"
                      : "border-input bg-background"
                  }`}
                >
                  {item.completed && <CheckCircle2 className="w-4 h-4" />}
                </div>

                <div className="space-y-1.5 max-w-3xl">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-secondary text-foreground">
                      {item.category}
                    </span>
                    <span className="text-[11px] font-mono text-muted-foreground flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {item.timeline}
                    </span>
                    <span className="text-[10px] font-medium text-primary bg-primary/10 px-2 py-0.5 rounded">
                      {item.controllability}
                    </span>
                  </div>

                  <h3
                    className={`font-display font-bold text-base text-foreground ${
                      item.completed ? "line-through text-muted-foreground" : ""
                    }`}
                  >
                    {item.title}
                  </h3>

                  <p className="text-xs text-muted-foreground leading-relaxed">
                    <strong className="text-foreground">Why this matters:</strong>{" "}
                    {item.whyItMatters}
                  </p>

                  <div className="text-[11px] text-bronze font-medium pt-1">
                    Addresses gap: {item.gapAddressed}
                  </div>
                </div>
              </div>

              <div className="shrink-0 flex items-center gap-2">
                <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-secondary border border-border text-foreground">
                  Impact: {item.impact}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Integration to Academic Readiness */}
      <div className="p-6 rounded-2xl bg-secondary/40 border border-border flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <h4 className="font-display font-bold text-foreground text-sm">
            Need customized levers for your specific curriculum?
          </h4>
          <p className="text-xs text-muted-foreground">
            Generate an action roadmap based on your predicted grades and target universities.
          </p>
        </div>
        <Link to="/academic-readiness">
          <Button className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold text-xs">
            Generate Custom Plan →
          </Button>
        </Link>
      </div>
    </div>
  );
}
