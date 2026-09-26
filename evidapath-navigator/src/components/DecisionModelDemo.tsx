import { useState } from "react";
import { Link } from "@tanstack/react-router";
import {
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  TrendingUp,
  ShieldCheck,
  DollarSign,
  BookOpen,
  Sparkles,
  Scale,
  RefreshCw,
} from "lucide-react";
import { SAMPLE_DECISION_ANALYSIS } from "../lib/decision-model";
import { UNIVERSITIES_DATA } from "../lib/mock-data";
import { formatCost, isPending } from "../lib/format";

function money(value: number | null, currency = "USD"): string {
  if (isPending(value)) return "Pending verified data";
  return `$${value!.toLocaleString()} ${currency}`;
}

export function DecisionModelDemo() {
  const [selectedUnivId, setSelectedUnivId] = useState<string>("oxford-univ");
  const univ = UNIVERSITIES_DATA.find((u) => u.id === selectedUnivId) || UNIVERSITIES_DATA[0];
  const analysis =
    SAMPLE_DECISION_ANALYSIS[selectedUnivId] || SAMPLE_DECISION_ANALYSIS["oxford-univ"];

  return (
    <div className="rounded-2xl border border-border bg-card p-6 md:p-8 shadow-sm">
      {/* Top selector */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-border">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-primary">
            Interactive Decision Intelligence Demo
          </span>
          <h3 className="text-xl md:text-2xl font-display font-bold text-foreground mt-0.5">
            The EvidaPath Decision Model in Action
          </h3>
          <p className="text-xs sm:text-sm text-muted-foreground mt-1">
            Toggle a sample student analysis across distinct university archetypes:
          </p>
        </div>

        <div className="flex items-center gap-2 bg-secondary/80 p-1 rounded-lg border border-border">
          <button
            onClick={() => setSelectedUnivId("oxford-univ")}
            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              selectedUnivId === "oxford-univ"
                ? "bg-card text-foreground shadow-xs font-semibold"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            🇬🇧 Oxford (UK Collegiate)
          </button>
          <button
            onClick={() => setSelectedUnivId("tum-germany")}
            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              selectedUnivId === "tum-germany"
                ? "bg-card text-foreground shadow-xs font-semibold"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            🇩🇪 TUM Munich (European Excellence)
          </button>
        </div>
      </div>

      {/* Illustrative preview label */}
      <div className="mt-4 flex items-center gap-2 text-[11px] text-muted-foreground">
        <span className="inline-block w-1.5 h-1.5 rounded-full bg-bronze" />
        <span>
          Illustrative product preview. Live analysis will use verified EvidaPath data with source
          attribution and confidence indicators.
        </span>
      </div>

      {/* University summary header strip */}
      <div className="my-6 bg-secondary/40 rounded-xl p-4 border border-border/70 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{univ.flag}</span>
          <div>
            <h4 className="font-display font-bold text-foreground text-base">{univ.name}</h4>
            <p className="text-xs text-muted-foreground">
              {univ.city}, {univ.country} • {univ.durationYears}-Year Degree • {univ.programs[0]}
            </p>
          </div>
        </div>

        {/* The pivotal financial comparison visual */}
        <div className="flex items-center gap-4 text-xs font-medium bg-card px-3.5 py-2 rounded-lg border border-border">
          <div className="text-right">
            <span className="text-muted-foreground block text-[10px] uppercase font-semibold">
              Total Cost of Attendance
            </span>
            <span className="text-foreground font-mono font-bold text-sm">
              {money(analysis.financialFit.fourYearCommitment)}
            </span>
          </div>
          <span className="text-muted-foreground">→</span>
          <div className="text-right">
            <span className="text-primary block text-[10px] uppercase font-semibold">
              Identified Funding
            </span>
            <span className="text-primary font-mono font-bold text-sm">
              {isPending(analysis.financialFit.identifiedFunding)
                ? "Pending verified data"
                : `-${money(analysis.financialFit.identifiedFunding)}`}
            </span>
          </div>
          <span className="text-muted-foreground">=</span>
          <div className="text-right">
            <span className="text-bronze block text-[10px] uppercase font-semibold">
              Remaining Family Gap
            </span>
            <span className="text-bronze font-mono font-bold text-sm">
              {money(analysis.financialFit.remainingFamilyGap)}
            </span>
          </div>
        </div>
      </div>

      {/* The 6 Dimensions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Dim 1: Academic Readiness */}
        <div className="p-4 rounded-xl border border-border bg-card/60 flex flex-col justify-between space-y-3">
          <div>
            <div className="flex items-center justify-between gap-2">
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Dimension 1
              </span>
              <span
                className={`text-[11px] font-medium px-2 py-0.5 rounded-full border ${
                  analysis.academicReadiness.status === "Strong Alignment"
                    ? "text-primary bg-primary/10 border-primary/20"
                    : "text-bronze bg-bronze/10 border-bronze/20"
                }`}
              >
                {analysis.academicReadiness.status}
              </span>
            </div>
            <h5 className="font-display font-semibold text-sm text-foreground mt-1">
              Academic Readiness
            </h5>
            <p className="text-xs text-muted-foreground mt-1.5 leading-relaxed">
              {analysis.academicReadiness.details}
            </p>
          </div>

          <div className="space-y-1.5 pt-2 border-t border-border/60">
            {analysis.academicReadiness.metrics.map((m, idx) => (
              <div key={idx} className="flex justify-between text-[11px]">
                <span className="text-muted-foreground">{m.label}:</span>
                <span className="font-mono text-muted-foreground font-medium">{m.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Dim 2: Admissions Evidence */}
        <div className="p-4 rounded-xl border border-border bg-card/60 flex flex-col justify-between space-y-3">
          <div>
            <div className="flex items-center justify-between gap-2">
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Dimension 2
              </span>
              <span className="text-[11px] font-medium px-2 py-0.5 rounded-full border text-muted-foreground bg-secondary border-border">
                {analysis.admissionsEvidence.evidenceStrength}
              </span>
            </div>
            <h5 className="font-display font-semibold text-sm text-foreground mt-1">
              Admissions Evidence
            </h5>
            <p className="text-xs text-muted-foreground mt-1.5 leading-relaxed">
              {analysis.admissionsEvidence.details}
            </p>
          </div>

          <div className="space-y-1.5 pt-2 border-t border-border/60">
            <div className="text-[11px] text-muted-foreground">
              <span className="font-semibold text-foreground">Benchmark:</span>{" "}
              {analysis.admissionsEvidence.acceptanceBenchmark}
            </div>
            <div className="text-[11px] text-bronze font-medium flex items-center gap-1">
              <AlertTriangle className="w-3 h-3 shrink-0" />
              <span>Uncertainty communicated explicitly, not hidden</span>
            </div>
          </div>
        </div>

        {/* Dim 3: Financial Fit */}
        <div className="p-4 rounded-xl border border-border bg-card/60 flex flex-col justify-between space-y-3">
          <div>
            <div className="flex items-center justify-between gap-2">
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Dimension 3
              </span>
              <span className="text-[11px] font-medium px-2 py-0.5 rounded-full border text-muted-foreground bg-secondary border-border">
                {univ.affordabilityIndex.category}
              </span>
            </div>
            <h5 className="font-display font-semibold text-sm text-foreground mt-1">
              Financial Fit & Real Net Cost
            </h5>
            <p className="text-xs text-muted-foreground mt-1.5 leading-relaxed">
              {univ.affordabilityIndex.notes}
            </p>
          </div>

          <div className="bg-secondary/50 p-2.5 rounded-lg border border-border/80 space-y-1 text-xs">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Annual Budget:</span>
              <span className="font-mono font-medium text-muted-foreground">
                {money(analysis.financialFit.annualTotalCost)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Degree Net Total:</span>
              <span className="font-mono font-bold text-muted-foreground">
                {money(analysis.financialFit.remainingFamilyGap)}
              </span>
            </div>
          </div>
        </div>

        {/* Dim 4: Career Alignment */}
        <div className="p-4 rounded-xl border border-border bg-card/60 flex flex-col justify-between space-y-3">
          <div>
            <div className="flex items-center justify-between gap-2">
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Dimension 4
              </span>
              <span className="text-[11px] font-medium px-2 py-0.5 rounded-full border text-muted-foreground bg-secondary border-border">
                Career Fit
              </span>
            </div>
            <h5 className="font-display font-semibold text-sm text-foreground mt-1">
              Career Alignment & Mobility
            </h5>
            <p className="text-xs text-muted-foreground mt-1.5 leading-relaxed">
              {analysis.careerAlignment.rating}
            </p>
          </div>

          <div className="space-y-1.5 pt-2 border-t border-border/60">
            <span className="text-[11px] font-semibold text-foreground block">
              Key Industry Pipelines:
            </span>
            <div className="flex flex-wrap gap-1">
              {analysis.careerAlignment.industryConnections.slice(0, 3).map((conn, idx) => (
                <span
                  key={idx}
                  className="text-[10px] bg-secondary px-1.5 py-0.5 rounded text-muted-foreground"
                >
                  {conn}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Dim 5: Pathway Flexibility */}
        <div className="p-4 rounded-xl border border-border bg-card/60 flex flex-col justify-between space-y-3">
          <div>
            <div className="flex items-center justify-between gap-2">
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Dimension 5
              </span>
              <span className="text-[11px] font-medium px-2 py-0.5 rounded-full border text-muted-foreground bg-secondary border-border">
                {analysis.pathwayFlexibility.alternativeRoutesCount} Strategic Pivots
              </span>
            </div>
            <h5 className="font-display font-semibold text-sm text-foreground mt-1">
              Pathway Flexibility
            </h5>
            <p className="text-xs text-muted-foreground mt-1.5 leading-relaxed">
              Alternative programs and international universities that achieve equivalent academic
              objectives.
            </p>
          </div>

          <div className="space-y-1 pt-2 border-t border-border/60">
            {analysis.pathwayFlexibility.options.map((opt, idx) => (
              <div key={idx} className="flex items-center justify-between text-[11px]">
                <span className="text-foreground truncate max-w-[170px]">{opt.name}</span>
                <span className="font-mono text-xs font-medium text-muted-foreground">
                  {opt.costDelta}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Dim 6: Improvement Levers */}
        <div className="p-4 rounded-xl border border-border bg-card/60 flex flex-col justify-between space-y-3 bg-gradient-to-br from-card to-secondary/30">
          <div>
            <div className="flex items-center justify-between gap-2">
              <span className="text-xs font-semibold text-primary uppercase tracking-wider">
                Dimension 6
              </span>
              <span className="text-[11px] font-medium px-2 py-0.5 rounded-full border text-primary bg-primary/10 border-primary/20">
                Actionable Levers
              </span>
            </div>
            <h5 className="font-display font-semibold text-sm text-foreground mt-1">
              Controllable Student Levers
            </h5>
            <p className="text-xs text-muted-foreground mt-1.5 leading-relaxed">
              Specific interventions that can improve academic readiness, affordability, or
              available pathways.
            </p>
          </div>

          <div className="space-y-1.5 pt-2 border-t border-border/60">
            {analysis.improvementLevers.slice(0, 2).map((l, idx) => (
              <div key={idx} className="text-[11px] flex items-start gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-primary shrink-0 mt-0.5" />
                <span className="text-foreground leading-snug line-clamp-2">{l.action}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom CTA bar */}
      <div className="mt-6 pt-5 border-t border-border flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <ShieldCheck className="w-4 h-4 text-muted-foreground" />
          <span>
            Evidence Confidence: <strong>{univ.evidenceConfidence}</strong> • Verified:{" "}
            {univ.lastVerified}
          </span>
        </div>

        <Link to="/analyze">
          <button className="inline-flex items-center gap-2 text-xs sm:text-sm font-semibold text-primary hover:text-primary/80 transition-colors">
            <span>Analyze Your Own Academic Profile Against {univ.shortName}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </Link>
      </div>
    </div>
  );
}
