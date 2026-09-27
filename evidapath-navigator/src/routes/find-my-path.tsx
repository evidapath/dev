import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { useServerFn } from "@tanstack/react-start";
import {
  ArrowRight,
  ArrowLeft,
  Compass,
  Check,
  MapPin,
  GraduationCap,
  DollarSign,
  Globe,
  Sparkles,
  Save,
  Scale,
  ChevronDown,
} from "lucide-react";
import { Button } from "../components/ui/button";
import { getUniversities } from "../lib/universities.functions";
import type { University } from "../lib/mock-data";
import { formatCost } from "../lib/format";
import { DataStatus, StatusChip, PendingValue } from "../components/DataStatus";
import { canonicalLink, ogUrlMeta } from "../lib/seo";

export const Route = createFileRoute("/find-my-path")({
  head: () => ({
    meta: [
      { title: "Find My Path — EvidaPath" },
      {
        name: "description",
        content:
          "Tell us a few things about yourself and see realistic university pathways. A simple guided intake — complexity only when you ask for it.",
      },
      { property: "og:title", content: "Find My Path — EvidaPath" },
      {
        property: "og:description",
        content:
          "Tell us a little about yourself. We'll show you where you stand and what looks realistic.",
      },
      ogUrlMeta("/find-my-path"),
    ],
    links: [canonicalLink("/find-my-path")],
  }),
  component: FindMyPathPage,
});

interface IntakeAnswers {
  curriculum: string;
  gradeBand: string;
  subject: string;
  region: string;
  budget: string;
  citizenship: string;
  preferences: string;
}

const STEPS = [
  { key: "curriculum", title: "Where are you studying now?", icon: Globe },
  { key: "gradeBand", title: "How are you doing academically?", icon: GraduationCap },
  { key: "subject", title: "What do you want to study?", icon: Sparkles },
  { key: "region", title: "Where would you consider studying?", icon: MapPin },
  { key: "budget", title: "What can your family realistically spend?", icon: DollarSign },
  { key: "citizenship", title: "Citizenship / residency", icon: Compass },
  { key: "preferences", title: "Anything else? (optional)", icon: Check },
] as const;

const DEFAULTS: IntakeAnswers = {
  curriculum: "IB Diploma",
  gradeBand: "Strong: IB 37-39 / A*AA / GPA 3.8-3.9",
  subject: "Computer Science",
  region: "Open to anywhere",
  budget: "40000",
  citizenship: "",
  preferences: "",
};

function FindMyPathPage() {
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState<IntakeAnswers>(DEFAULTS);
  const [showResults, setShowResults] = useState(false);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [universities, setUniversities] = useState<University[]>([]);
  const [source, setSource] = useState<"sanity" | "mock" | null>(null);
  const navigate = useNavigate();

  const fetchUniversities = useServerFn(getUniversities);
  useEffect(() => {
    let active = true;
    fetchUniversities().then((res) => {
      if (!active) return;
      setUniversities(res.universities);
      setSource(res.source);
    });
    return () => {
      active = false;
    };
  }, [fetchUniversities]);

  const set = (k: keyof IntakeAnswers, v: string) => setAnswers((a) => ({ ...a, [k]: v }));

  const next = () => {
    if (step < STEPS.length - 1) setStep(step + 1);
    else setShowResults(true);
  };
  const back = () => (step > 0 ? setStep(step - 1) : null);

  // Simple, transparent pathway selection from the illustrative dataset.
  // No admissions probabilities. Filters by region + subject match where
  // possible; otherwise shows the full illustrative set.
  const pathways = universities
    .filter((u) => {
      const regionOk =
        answers.region === "Open to anywhere" ||
        answers.region === "All" ||
        u.country === answers.region;
      const subjectOk =
        answers.subject.trim() === "" ||
        u.programs.some((p) => p.toLowerCase().includes(answers.subject.toLowerCase())) ||
        answers.subject.toLowerCase().includes("computer") ||
        answers.subject.toLowerCase().includes("any");
      return regionOk && subjectOk;
    })
    .slice(0, 8);

  if (showResults) {
    return (
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
        <div className="space-y-3 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold">
            <Compass className="w-3.5 h-3.5" />
            <span>Your pathways</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-display font-extrabold text-foreground">
            Here's what looks realistic for you.
          </h1>
          <p className="text-sm text-muted-foreground leading-relaxed">
            Based on what you told us, these pathways are worth exploring. Costs and admissions
            evidence are illustrative until verified data is connected — tap any option to go
            deeper.
          </p>
          <DataStatus level={source === "sanity" ? "live" : "illustrative"}>
            {source === "sanity"
              ? "Live data connected. NYU Abu Dhabi is verified against official sources; other institutions are marked verification in progress. These are pathways to explore, not admissions predictions — no probabilities are invented."
              : "Illustrative product preview. Live analysis will use verified EvidaPath data as datasets are built and verified."}
          </DataStatus>
        </div>

        <div className="space-y-4">
          {pathways.length === 0 && (
            <div className="rounded-2xl border border-border bg-card p-8 text-center text-sm text-muted-foreground">
              No illustrative pathways matched your filters yet. Try broadening your region or
              subject, or{" "}
              <Link to="/universities" className="text-primary font-semibold">
                browse all universities
              </Link>
              .
            </div>
          )}
          {pathways.map((u) => {
            const isOpen = expanded === u.id;
            return (
              <div
                key={u.id}
                className="rounded-2xl border border-border bg-card shadow-xs overflow-hidden"
              >
                {/* Summary row — progressive disclosure */}
                <button
                  onClick={() => setExpanded(isOpen ? null : u.id)}
                  className="w-full flex items-center justify-between gap-4 p-5 text-left hover:bg-secondary/30 transition-colors"
                >
                  <div className="flex items-center gap-4 min-w-0">
                    <span className="text-2xl shrink-0">{u.flag}</span>
                    <div className="min-w-0">
                      <h3 className="font-display font-bold text-base text-foreground truncate">
                        {u.name}
                      </h3>
                      <p className="text-xs text-muted-foreground flex items-center gap-1">
                        <MapPin className="w-3 h-3" />
                        {u.city}, {u.country} · {u.durationYears}-year
                      </p>
                    </div>
                  </div>
                  <div className="hidden sm:flex items-center gap-4 shrink-0">
                    <StatusChip
                      level={u.evidenceConfidence.startsWith("Verified") ? "live" : "pending"}
                    />
                    <ChevronDown
                      className={`w-4 h-4 text-muted-foreground transition-transform ${
                        isOpen ? "rotate-180" : ""
                      }`}
                    />
                  </div>
                </button>

                {/* Quick facts */}
                <div className="px-5 pb-5 grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs border-t border-border pt-4">
                  <div>
                    <p className="text-muted-foreground">Academic fit</p>
                    <PendingValue />
                  </div>
                  <div>
                    <p className="text-muted-foreground">Est. annual cost</p>
                    <p className="font-mono text-foreground">
                      {formatCost(u.costs.totalAnnual, u.costs.currency)}
                    </p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Funding potential</p>
                    <PendingValue />
                  </div>
                  <div>
                    <p className="text-muted-foreground">Main gap / risk</p>
                    <PendingValue />
                  </div>
                </div>

                {/* Progressive disclosure — deeper analysis only when opened */}
                {isOpen && (
                  <div className="px-5 pb-5 space-y-4 border-t border-border pt-4">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                      <div className="rounded-lg border border-border bg-secondary/30 p-3 space-y-1.5">
                        <p className="font-semibold text-foreground">Admissions</p>
                        <p className="text-muted-foreground">
                          System: {u.academicRequirements.system}
                        </p>
                        <p className="text-muted-foreground">
                          Target: <PendingValue />
                        </p>
                        <ul className="text-muted-foreground list-disc list-inside">
                          {u.academicRequirements.prerequisites.map((p) => (
                            <li key={p}>{p}</li>
                          ))}
                        </ul>
                      </div>
                      <div className="rounded-lg border border-border bg-secondary/30 p-3 space-y-1.5">
                        <p className="font-semibold text-foreground">Cost & funding</p>
                        <p className="text-muted-foreground">
                          Tuition/yr: {formatCost(u.costs.tuitionPerYear, u.costs.currency)}
                        </p>
                        <p className="text-muted-foreground">
                          Living/yr: {formatCost(u.costs.livingPerYear, u.costs.currency)}
                        </p>
                        <p className="text-muted-foreground">
                          Total degree: {formatCost(u.costs.totalDegree, u.costs.currency)}
                        </p>
                        <p className="text-muted-foreground">
                          Affordability: {u.affordabilityIndex.category}
                        </p>
                      </div>
                    </div>
                    <div className="rounded-lg border border-border bg-secondary/30 p-3 text-xs space-y-1">
                      <p className="font-semibold text-foreground">Why this made your list</p>
                      <p className="text-muted-foreground">
                        Matches your subject interest and region preference. Full evidence-based fit
                        analysis will appear here once verified data is connected.
                      </p>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <Link to="/analyze">
                        <Button
                          size="sm"
                          className="bg-primary hover:bg-primary/90 text-primary-foreground text-xs"
                        >
                          Explore this option <ArrowRight className="w-3 h-3" />
                        </Button>
                      </Link>
                      <Link to="/sign-in">
                        <Button size="sm" variant="outline" className="border-border text-xs">
                          <Save className="w-3 h-3" /> Save
                        </Button>
                      </Link>
                      <Link to="/compare-offers">
                        <Button size="sm" variant="outline" className="border-border text-xs">
                          <Scale className="w-3 h-3" /> Compare
                        </Button>
                      </Link>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-border">
          <Button
            variant="outline"
            className="border-border text-foreground"
            onClick={() => {
              setShowResults(false);
              setStep(0);
            }}
          >
            <ArrowLeft className="w-4 h-4" /> Start over
          </Button>
          <div className="flex gap-2">
            <Link to="/universities">
              <Button variant="outline" className="border-border text-foreground text-sm">
                Browse all universities
              </Button>
            </Link>
            <Link to="/sign-in">
              <Button className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold text-sm">
                Save my path & sign in <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const Step = STEPS[step];
  const Icon = Step.icon;

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <div className="text-center space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold">
          <Compass className="w-3.5 h-3.5" />
          <span>Find My Path</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-display font-extrabold text-foreground">
          Tell us a little about yourself.
        </h1>
        <p className="text-sm text-muted-foreground">
          We'll show you where you stand and what looks realistic. Takes about 3 minutes.
        </p>
      </div>

      {/* Step indicator */}
      <div className="flex items-center justify-center gap-1.5">
        {STEPS.map((s, i) => (
          <button
            key={s.key}
            onClick={() => setStep(i)}
            className={`h-1.5 rounded-full transition-all ${
              i === step ? "w-8 bg-primary" : i < step ? "w-4 bg-primary/50" : "w-4 bg-border"
            }`}
            aria-label={`Step ${i + 1}`}
          />
        ))}
      </div>

      <div className="bg-card border border-border rounded-2xl p-6 sm:p-8 shadow-sm space-y-6">
        <div className="flex items-center gap-3 border-b border-border pb-4">
          <div className="w-9 h-9 rounded-lg bg-primary/10 text-primary flex items-center justify-center shrink-0">
            <Icon className="w-4.5 h-4.5" />
          </div>
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
              Step {step + 1} of {STEPS.length}
            </p>
            <h2 className="font-display font-bold text-lg text-foreground">{Step.title}</h2>
          </div>
        </div>

        <StepField stepKey={Step.key} answers={answers} set={set} />

        <div className="flex items-center justify-between pt-2 border-t border-border">
          <Button
            variant="ghost"
            onClick={back}
            disabled={step === 0}
            className="text-muted-foreground"
          >
            <ArrowLeft className="w-4 h-4" /> Back
          </Button>
          <Button
            onClick={next}
            className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold"
          >
            {step === STEPS.length - 1 ? (
              <>
                Show My Options <ArrowRight className="w-4 h-4" />
              </>
            ) : (
              <>
                Continue <ArrowRight className="w-4 h-4" />
              </>
            )}
          </Button>
        </div>
      </div>

      <p className="text-center text-[11px] text-muted-foreground">
        Your answers stay on your device for this session. Sign in to save your path permanently.
      </p>
    </div>
  );
}

function StepField({
  stepKey,
  answers,
  set,
}: {
  stepKey: string;
  answers: IntakeAnswers;
  set: (k: keyof IntakeAnswers, v: string) => void;
}) {
  const inputCls =
    "w-full h-10 px-3 rounded-lg border border-input bg-background text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary";

  switch (stepKey) {
    case "curriculum":
      return (
        <select
          value={answers.curriculum}
          onChange={(e) => set("curriculum", e.target.value)}
          className={inputCls}
        >
          <option>IB Diploma</option>
          <option>Cambridge A-Levels</option>
          <option>US High School Diploma + APs</option>
          <option>German Abitur</option>
          <option>National Curriculum / Other</option>
        </select>
      );
    case "gradeBand":
      return (
        <select
          value={answers.gradeBand}
          onChange={(e) => set("gradeBand", e.target.value)}
          className={inputCls}
        >
          <option>Top Tier: IB 40+ / A*A*A / GPA 4.0</option>
          <option>Strong: IB 37-39 / A*AA / GPA 3.8-3.9</option>
          <option>Competitive: IB 34-36 / AAA-AAB / GPA 3.6-3.7</option>
          <option>Foundation: IB 30-33 / ABB-BBB / GPA 3.3-3.5</option>
        </select>
      );
    case "subject":
      return (
        <input
          type="text"
          placeholder="e.g. Computer Science, Economics, Aerospace"
          value={answers.subject}
          onChange={(e) => set("subject", e.target.value)}
          className={inputCls}
        />
      );
    case "region":
      return (
        <select
          value={answers.region}
          onChange={(e) => set("region", e.target.value)}
          className={inputCls}
        >
          <option>Open to anywhere</option>
          <option>United Kingdom</option>
          <option>Canada</option>
          <option>Germany</option>
          <option>Netherlands</option>
          <option>Singapore</option>
          <option>United Arab Emirates</option>
        </select>
      );
    case "budget":
      return (
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <label className="text-xs font-semibold uppercase text-muted-foreground">
              Annual education budget (USD)
            </label>
            <span className="font-mono text-sm font-bold text-foreground">
              ${Number(answers.budget).toLocaleString()}/yr
            </span>
          </div>
          <input
            type="range"
            min="20000"
            max="90000"
            step="5000"
            value={answers.budget}
            onChange={(e) => set("budget", e.target.value)}
            className="w-full accent-primary"
          />
          <div className="flex justify-between text-[10px] text-muted-foreground">
            <span>$20k</span>
            <span>$90k+</span>
          </div>
        </div>
      );
    case "citizenship":
      return (
        <input
          type="text"
          placeholder="e.g. UAE, India, UK, Canada (used for tuition/eligibility modeling)"
          value={answers.citizenship}
          onChange={(e) => set("citizenship", e.target.value)}
          className={inputCls}
        />
      );
    case "preferences":
      return (
        <textarea
          placeholder="City/campus preference, language, degree length, anything else…"
          value={answers.preferences}
          onChange={(e) => set("preferences", e.target.value)}
          rows={4}
          className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
        />
      );
    default:
      return null;
  }
}
