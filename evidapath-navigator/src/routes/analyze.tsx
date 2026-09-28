import { createFileRoute, Link } from "@tanstack/react-router";
import { requireAuth } from "../lib/route-guard";
import { useEffect, useState } from "react";
import { useServerFn } from "@tanstack/react-start";
import {
  BarChart3,
  AlertCircle,
  CheckCircle2,
  ArrowRight,
  ShieldCheck,
  TrendingUp,
  AlertTriangle,
  Layers,
  DollarSign,
} from "lucide-react";
import { Button } from "../components/ui/button";
import { getUniversities } from "../lib/universities.functions";
import type { University } from "../lib/mock-data";
import { SAMPLE_DECISION_ANALYSIS } from "../lib/decision-model";
import { isPending } from "../lib/format";
import { canonicalLink, ogUrlMeta } from "../lib/seo";

function money(value: number | null, currency = "USD"): string {
  if (isPending(value)) return "Pending verified data";
  return `$${value!.toLocaleString()} ${currency}`;
}

export const Route = createFileRoute("/analyze")({
  head: () => ({
    meta: [
      { title: "Academic & Admissions Evidence Analysis — EvidaPath" },
      {
        name: "description",
        content:
          "Analyze where you currently stand relative to institutional evidence, historical admissions benchmarks, and actionable levers.",
      },
      { property: "og:title", content: "Academic Gap Analysis & Controllable Levers — EvidaPath" },
      {
        property: "og:description",
        content:
          "Evaluate evidence, identify gaps you can still change, and model alternative pathways.",
      },
      ogUrlMeta("/analyze"),
    ],
    links: [canonicalLink("/analyze")],
  }),
  beforeLoad: ({ context, location }) => requireAuth(context, location.pathname),
  component: AnalyzePage,
});

function AnalyzePage() {
  const [selectedUnivId, setSelectedUnivId] = useState("");
  const [studentGrades, setStudentGrades] = useState("A*AA");
  const [targetSubject, setTargetSubject] = useState("Computer Science");
  const [universities, setUniversities] = useState<University[]>([]);
  const [source, setSource] = useState<"sanity" | "mock" | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchUniversities = useServerFn(getUniversities);
  useEffect(() => {
    let active = true;
    fetchUniversities()
      .then((res) => {
        if (!active) return;
        setUniversities(res.universities);
        setSource(res.source);
        const first = res.universities[0];
        if (first) setSelectedUnivId((cur) => cur || first.id);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [fetchUniversities]);

  const univ = universities.find((u) => u.id === selectedUnivId) || universities[0];
  // SAMPLE_DECISION_ANALYSIS is an ILLUSTRATIVE analytical framework, NOT computed
  // from verified inputs. Real Sanity ids don't key into it, so it always resolves
  // to the sample — shown clearly labeled as illustrative, never as real analysis.
  const analysis = SAMPLE_DECISION_ANALYSIS["oxford-univ"]!;

  if (loading || !univ) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <p className="text-sm text-muted-foreground">Loading verified university data…</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      {/* Header */}
      <div className="max-w-3xl space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold">
          <BarChart3 className="w-3.5 h-3.5" />
          <span>Decision Suite • Analyze</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-display font-extrabold text-foreground">
          Analyze Where You Stand Relative to Evidence
        </h1>
        <p className="text-sm sm:text-base text-muted-foreground leading-relaxed">
          EvidaPath avoids arbitrary admissions chances. We analyze your academic prerequisites,
          available evidence, and financial reality, highlighting the exact levers you can still
          control. Where evidence is incomplete, uncertainty is communicated explicitly.
        </p>
        <div className="flex items-center gap-2 text-[11px] text-muted-foreground bg-secondary/50 border border-border rounded-lg px-3 py-2">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-bronze" />
          <span>
            {source === "sanity"
              ? "University identity and cost data below are live from EvidaPath (NYU Abu Dhabi verified against official sources). The fit scoring, readiness metrics and improvement levers are an ILLUSTRATIVE framework — not yet computed from your verified inputs — and are labeled as such."
              : "Illustrative product preview. Live analysis will use verified EvidaPath data with source attribution and confidence indicators."}
          </span>
        </div>
      </div>

      {/* Target Selector Bar */}
      <div className="bg-card border border-border rounded-2xl p-6 shadow-xs">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-semibold uppercase text-muted-foreground mb-1.5">
              Target University
            </label>
            <select
              value={selectedUnivId}
              onChange={(e) => setSelectedUnivId(e.target.value)}
              className="w-full h-10 px-3 rounded-lg border border-input bg-background text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
            >
              {universities.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.flag} {u.name} ({u.country})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase text-muted-foreground mb-1.5">
              Your Current Academic Baseline
            </label>
            <select
              value={studentGrades}
              onChange={(e) => setStudentGrades(e.target.value)}
              className="w-full h-10 px-3 rounded-lg border border-input bg-background text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
            >
              <option value="A*A*A">A*A*A (or IB 40+ / GPA 4.0)</option>
              <option value="A*AA">A*AA (or IB 38-39 / GPA 3.9)</option>
              <option value="AAA">AAA (or IB 36-37 / GPA 3.8)</option>
              <option value="AAB">AAB (or IB 34-35 / GPA 3.7)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase text-muted-foreground mb-1.5">
              Intended Degree Subject
            </label>
            <select
              value={targetSubject}
              onChange={(e) => setTargetSubject(e.target.value)}
              className="w-full h-10 px-3 rounded-lg border border-input bg-background text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
            >
              <option value="Computer Science">Computer Science / Software</option>
              <option value="Economics">Economics & Management</option>
              <option value="Engineering">Mechanical / Aerospace Engineering</option>
              <option value="Law">Law & Jurisprudence</option>
            </select>
          </div>
        </div>
      </div>

      {/* Analysis Output Container */}
      <div className="space-y-8">
        {/* Status banner */}
        <div className="bg-secondary/40 border border-border rounded-2xl p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="text-3xl">{univ.flag}</span>
            <div>
              <h2 className="font-display font-bold text-xl text-foreground">
                Analysis for {univ.name}
              </h2>
              <p className="text-xs text-muted-foreground">
                Benchmark: {univ.admissionsEvidence.historicalBenchmark}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 text-xs">
            <span className="font-semibold text-foreground">Fit scoring:</span>
            <span className="px-2.5 py-1 rounded-full bg-secondary text-muted-foreground font-mono font-medium border border-border">
              Illustrative framework
            </span>
          </div>
        </div>

        {/* 2-Column: Left Academic & Gaps | Right Financials & Pathways */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column: Academic Standing & Controllable Levers */}
          <div className="space-y-6">
            {/* Academic Standing */}
            <div className="rounded-2xl border border-border bg-card p-6 shadow-xs space-y-4">
              <div className="flex items-center justify-between border-b border-border pb-3">
                <h3 className="font-display font-bold text-base text-foreground">
                  Current Position & Prerequisites
                </h3>
                <span className="text-xs font-semibold px-2 py-0.5 rounded bg-secondary text-muted-foreground">
                  Illustrative example
                </span>
              </div>
              <p className="text-xs sm:text-sm text-muted-foreground leading-relaxed">
                {analysis.academicReadiness.details}
              </p>

              <div className="space-y-2 pt-2">
                {analysis.academicReadiness.metrics.map((m, idx) => (
                  <div
                    key={idx}
                    className="flex justify-between items-center text-xs p-2.5 rounded-lg bg-secondary/50 border border-border/60"
                  >
                    <span className="text-muted-foreground font-medium">{m.label}</span>
                    <div className="text-right">
                      <span className="font-mono font-bold text-muted-foreground block">
                        {m.value}
                      </span>
                      <span className="text-[10px] text-muted-foreground">
                        Benchmark: {m.benchmark}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Controllable Improvement Levers */}
            <div className="rounded-2xl border border-border bg-card p-6 shadow-xs space-y-4">
              <div className="flex items-center justify-between border-b border-border pb-3">
                <h3 className="font-display font-bold text-base text-foreground flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-primary" />
                  <span>Controllable Levers ({analysis.improvementLevers.length})</span>
                </h3>
                <span className="text-[11px] text-muted-foreground font-semibold">
                  Illustrative framework
                </span>
              </div>

              <div className="space-y-3">
                {analysis.improvementLevers.map((lever) => (
                  <div
                    key={lever.id}
                    className="p-3.5 rounded-xl border border-border bg-background space-y-2"
                  >
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="font-semibold text-primary uppercase tracking-wider">
                        {lever.category}
                      </span>
                      <span className="font-mono text-muted-foreground">{lever.timeline}</span>
                    </div>
                    <p className="text-xs font-medium text-foreground leading-snug">
                      {lever.action}
                    </p>
                    <div className="flex items-center justify-between text-[10px] text-muted-foreground pt-1">
                      <span>
                        Impact: <strong>{lever.impact}</strong>
                      </span>
                      <span className="text-primary font-medium">{lever.controllability}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column: Financial Commitment & Strategic Alternatives */}
          <div className="space-y-6">
            {/* Financial Reality Breakdown */}
            <div className="rounded-2xl border border-border bg-card p-6 shadow-xs space-y-4">
              <div className="flex items-center justify-between border-b border-border pb-3">
                <h3 className="font-display font-bold text-base text-foreground flex items-center gap-2">
                  <DollarSign className="w-4 h-4 text-bronze" />
                  <span>Financial Fit & Real Capital Outlay</span>
                </h3>
                <span className="text-xs font-mono font-semibold text-muted-foreground">
                  {univ.durationYears}-Year Total
                </span>
              </div>

              {/* The pivotal 3-number visual */}
              <div className="bg-secondary/40 rounded-xl p-4 border border-border space-y-3">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-muted-foreground">
                    Cost of Attendance ({univ.durationYears}-yr):
                  </span>
                  <span className="font-mono font-bold text-sm text-muted-foreground">
                    {money(univ.costs.totalDegree, univ.costs.currency)}
                  </span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-primary font-medium">Expected / Identified Funding:</span>
                  <span className="font-mono font-bold text-sm text-primary">
                    Pending verified data
                  </span>
                </div>
                <div className="pt-2 border-t border-border flex justify-between items-center text-xs">
                  <span className="text-bronze font-bold uppercase tracking-wider">
                    Remaining Family Gap:
                  </span>
                  <span className="font-mono font-extrabold text-base text-bronze">
                    Pending verified data
                  </span>
                </div>
              </div>

              <div className="text-xs text-muted-foreground space-y-1">
                <p>• Tuition per year: {formatTuition(univ)}</p>
                <p>• Estimated living/housing: {formatLiving(univ)}/yr</p>
                <p>• Affordability index: {univ.affordabilityIndex.category}</p>
              </div>

              <div className="pt-2">
                <Link to="/fund">
                  <Button
                    variant="outline"
                    className="w-full text-xs border-border hover:bg-secondary"
                  >
                    Open in Family Education Capital Plan →
                  </Button>
                </Link>
              </div>
            </div>

            {/* Strategic Pathway Pivots */}
            <div className="rounded-2xl border border-border bg-card p-6 shadow-xs space-y-4">
              <div className="flex items-center justify-between border-b border-border pb-3">
                <h3 className="font-display font-bold text-base text-foreground flex items-center gap-2">
                  <Layers className="w-4 h-4 text-primary" />
                  <span>Strategic Alternative Pathways</span>
                </h3>
                <span className="text-xs text-muted-foreground">Illustrative options</span>
              </div>

              <p className="text-xs text-muted-foreground">
                Institutions and programs that may offer comparable academic objectives, often with
                different tuition structures or admission predictability:
              </p>

              {source === "sanity" ? (
                <p className="text-xs text-muted-foreground italic">
                  EvidaPath will surface verified alternative pathways once they are sourced for
                  this university. We do not suggest specific alternatives until they are verified
                  against real data.
                </p>
              ) : (
                <div className="space-y-2.5">
                  {analysis.pathwayFlexibility.options.map((opt, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-lg border border-border bg-secondary/30 flex items-center justify-between text-xs"
                    >
                      <div>
                        <span className="font-semibold text-foreground block">{opt.name}</span>
                        <span className="text-[10px] text-muted-foreground">{opt.type}</span>
                      </div>
                      <span className="font-mono font-bold text-muted-foreground">
                        {opt.costDelta}
                      </span>
                    </div>
                  ))}
                </div>
              )}

              <div className="pt-2 border-t border-border flex justify-between items-center text-xs">
                <span className="text-muted-foreground">
                  Official source: {univ.officialSourceUrl}
                </span>
                <span className="text-muted-foreground">{univ.lastVerified}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function formatTuition(univ: University): string {
  if (isPending(univ.costs.tuitionPerYear)) return "Pending verified data";
  return `$${univ.costs.tuitionPerYear!.toLocaleString()} ${univ.costs.currency}`;
}

function formatLiving(univ: University): string {
  if (isPending(univ.costs.livingPerYear)) return "Pending verified data";
  return `$${univ.costs.livingPerYear!.toLocaleString()} ${univ.costs.currency}`;
}
