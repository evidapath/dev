import { useUniversitiesFn, useFxRatesFn, useScholarshipsFn } from "../lib/use-live-data";
import { buildPathways } from "../lib/pathways";
import { PathwayResults } from "../components/PathwayResults";
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
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "../components/ui/button";
import { type FxRates } from "../lib/fx.functions";
import { BUDGET_MAX, BUDGET_MIN } from "../lib/budget";
import {
  getProfile,
  upsertProfile,
  saveUniversity,
  listSavedUniversities,
} from "../lib/profile.functions";
import { useAuth } from "../components/AuthContext";
import { CounselingWaitlist } from "../components/CounselingWaitlist";
import type { Scholarship, University } from "../lib/mock-data";
import { DataStatus } from "../components/DataStatus";
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
  const [quick, setQuick] = useState(true);
  const [savedIds, setSavedIds] = useState<Set<string>>(new Set());
  const [universities, setUniversities] = useState<University[]>([]);
  const [source, setSource] = useState<"sanity" | "mock" | null>(null);
  const [fx, setFx] = useState<FxRates | null>(null);
  const [scholarships, setScholarships] = useState<Scholarship[]>([]);
  // True when the results were opened straight from the student's saved profile.
  const [fromProfile, setFromProfile] = useState(false);
  const navigate = useNavigate();

  const fetchUniversities = useUniversitiesFn();
  const fetchFx = useFxRatesFn();
  const fetchScholarships = useScholarshipsFn();
  useEffect(() => {
    let active = true;
    fetchScholarships()
      .then((res) => active && setScholarships(res.scholarships))
      .catch(() => {});
    fetchUniversities().then((res) => {
      if (!active) return;
      setUniversities(res.universities);
      setSource(res.source);
    });
    fetchFx()
      .then((r) => active && setFx(r))
      .catch(() => {});
    return () => {
      active = false;
    };
  }, [fetchUniversities, fetchFx, fetchScholarships]);

  // Prefill from a saved profile so a returning (signed-in) student sees their
  // answers persist. Silently ignored when signed out (intake still works locally).
  const getProfileFn = useServerFn(getProfile);
  const upsertProfileFn = useServerFn(upsertProfile);
  const listSavedFn = useServerFn(listSavedUniversities);
  useEffect(() => {
    let active = true;
    listSavedFn()
      .then((rows) => {
        if (!active) return;
        setSavedIds(new Set(rows.map((r) => r.sanity_university_id)));
      })
      .catch(() => {});
    getProfileFn()
      .then((p) => {
        if (!active || !p) return;
        setAnswers((a) => ({
          ...a,
          curriculum: p.curriculum ?? a.curriculum,
          gradeBand: p.grade_band ?? a.gradeBand,
          subject: p.intended_subject ?? a.subject,
          region: p.preferred_region ?? a.region,
          budget: p.annual_budget != null ? String(p.annual_budget) : a.budget,
          citizenship: p.citizenship ?? a.citizenship,
          preferences: p.preferences ?? a.preferences,
        }));
        // A student who already answered once goes straight to their results;
        // they can change any answer there instead of repeating every question.
        if (p.curriculum || p.intended_subject || p.annual_budget != null) {
          setShowResults(true);
          setFromProfile(true);
        }
      })
      .catch(() => {});
    return () => {
      active = false;
    };
  }, [getProfileFn, listSavedFn]);

  // Save a pathway's university to the student's persisted path (Supabase).
  const saveUniFn = useServerFn(saveUniversity);
  const saveUni = (u: University) => {
    saveUniFn({ data: { sanity_university_id: u.id, university_name: u.name } })
      .then(() => {
        setSavedIds((s) => new Set(s).add(u.id));
        toast.success(`${u.shortName} saved to your path.`);
      })
      .catch((err: Error) => {
        console.error("[find-my-path] save university failed:", err);
        toast.error(
          /not authenticated/i.test(err?.message ?? "")
            ? "Sign in to save universities to your path."
            : "Could not save — please try again.",
        );
      });
  };

  // Bottom "Save my path" action. When signed in: save ALL shown pathways + the
  // profile, then go to the dashboard. When signed out: send to sign-in (the
  // intake stays in session). Previously this was a dead <Link to="/sign-in">
  // that saved nothing even for logged-in users (the reported bug).
  const { user } = useAuth();
  const saveMyPath = () => {
    if (!user) {
      navigate({ to: "/sign-in", search: { redirect: "/dashboard" } });
      return;
    }
    saveProfile();
    Promise.allSettled(
      pathways.map((u) =>
        saveUniFn({ data: { sanity_university_id: u.id, university_name: u.name } }),
      ),
    )
      .then((results) => {
        const ok = results.filter((r) => r.status === "fulfilled").length;
        if (ok > 0) toast.success(`Saved ${ok} universit${ok === 1 ? "y" : "ies"} to your path.`);
        else toast.error("Could not save your path — please try again.");
        navigate({ to: "/dashboard" });
      })
      .catch(() => toast.error("Could not save your path — please try again."));
  };

  const set = (k: keyof IntakeAnswers, v: string) => setAnswers((a) => ({ ...a, [k]: v }));

  // Persist the profile when the student finishes the intake. Best-effort:
  // signed-out users just don't persist (the results still render from session).
  const saveProfile = () => {
    const budget = Number(answers.budget);
    upsertProfileFn({
      data: {
        curriculum: answers.curriculum || null,
        grade_band: answers.gradeBand || null,
        intended_subject: answers.subject || null,
        preferred_region: answers.region || null,
        annual_budget: Number.isFinite(budget) ? budget : null,
        citizenship: answers.citizenship || null,
        preferences: answers.preferences || null,
      },
      // Best-effort (signed-out users just don't persist), but never swallow the
      // error silently — log it so a real failure is visible, not hidden.
    }).catch((err: Error) => console.error("[find-my-path] profile save failed:", err));
  };

  const next = () => {
    if (step < STEPS.length - 1) setStep(step + 1);
    else {
      saveProfile();
      setShowResults(true);
    }
  };
  const back = () => (step > 0 ? setStep(step - 1) : null);

  // Changing a filter on the results page updates the saved profile too, so the
  // student never has to answer the questions again. Debounced; signed-in only.
  useEffect(() => {
    if (!showResults || !user) return;
    const t = setTimeout(saveProfile, 1000);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [answers, showResults, user]);

  const countries = Array.from(new Set(universities.map((u) => u.country))).sort();

  // Results grouped the way a student reads them (see lib/pathways.ts): what fits
  // the budget first, then good matches that cost more with ways to close the gap.
  const budgetUsd = Number(answers.budget);
  const noBudgetLimit = !Number.isFinite(budgetUsd) || budgetUsd >= BUDGET_MAX;
  const result = buildPathways({
    universities,
    scholarships,
    fx,
    region: answers.region,
    input: {
      curriculum: answers.curriculum,
      gradeBand: answers.gradeBand,
      subject: answers.subject,
      budgetUsd: noBudgetLimit ? BUDGET_MAX : budgetUsd,
      citizenship: answers.citizenship,
    },
  });
  // "Save my path" saves what's realistic: within budget, plus probably-affordable.
  const pathways = [...result.groups.within, ...result.groups.unpriced].map((r) => r.u);

  if (showResults) {
    return (
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
        <div className="space-y-3 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold">
            <Compass className="w-3.5 h-3.5" />
            <span>Your pathways</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-display font-extrabold text-foreground">
            Your options
          </h1>
          <p className="text-sm text-muted-foreground">
            Real costs and requirements from official sources. Change a filter and results update
            instantly
            {fromProfile ? " — we'll remember it." : "."}
          </p>
          {source === "mock" && (
            <DataStatus level="illustrative">
              Live data is unavailable right now — these are sample figures, not real costs.
            </DataStatus>
          )}
        </div>

        <ResultsFilters
          answers={answers}
          set={set}
          countries={countries}
          onEditAll={() => {
            setShowResults(false);
            setQuick(false);
            setStep(0);
          }}
        />
        {!noBudgetLimit && !fx && (
          <p className="text-xs text-bronze">
            Exchange rates are unavailable right now, so costs in other currencies can't be compared
            with your budget yet.
          </p>
        )}

        {universities.length === 0 ? (
          <div className="space-y-3" aria-busy="true">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-36 rounded-2xl bg-secondary/60 animate-pulse" />
            ))}
          </div>
        ) : (
          <PathwayResults
            result={result}
            budgetUsd={budgetUsd}
            noBudgetLimit={noBudgetLimit}
            region={answers.region}
            subject={answers.subject}
            savedIds={savedIds}
            onSave={saveUni}
          />
        )}

        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-border">
          <Button
            variant="outline"
            className="border-border text-foreground"
            onClick={() => {
              setShowResults(false);
              setQuick(false);
              setStep(0);
            }}
          >
            <ArrowLeft className="w-4 h-4" /> Edit all answers
          </Button>
          <div className="flex gap-2">
            <Link to="/universities">
              <Button variant="outline" className="border-border text-foreground text-sm">
                Browse all universities
              </Button>
            </Link>
            <Button
              onClick={saveMyPath}
              className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold text-sm"
            >
              {user ? "Save my path" : "Save my path & sign in"} <ArrowRight className="w-4 h-4" />
            </Button>
          </div>
        </div>

        <CounselingWaitlist
          defaultEmail={user?.email}
          shortlist={universities.filter((u) => savedIds.has(u.id)).map((u) => u.name)}
          source="Find My Path results"
        />
      </div>
    );
  }

  // Quick mode (default): the four answers that matter most, on one screen.
  // Country, citizenship and preferences can be added from the results page.
  if (quick) {
    const QUICK = ["curriculum", "gradeBand", "subject", "budget"] as const;
    return (
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-6">
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold">
            <Compass className="w-3.5 h-3.5" />
            <span>Find My Path</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-display font-extrabold text-foreground">
            4 questions. Your options.
          </h1>
          <p className="text-sm text-muted-foreground">About 30 seconds.</p>
        </div>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            saveProfile();
            setShowResults(true);
          }}
          className="bg-card border border-border rounded-2xl p-6 sm:p-8 shadow-sm space-y-5"
        >
          {QUICK.map((k) => {
            const meta = STEPS.find((x) => x.key === k)!;
            const QIcon = meta.icon;
            return (
              <div key={k} className="space-y-1.5">
                <p className="text-sm font-semibold text-foreground flex items-center gap-2">
                  <QIcon className="w-4 h-4 text-primary" />
                  {meta.title}
                </p>
                <StepField stepKey={k} answers={answers} set={set} countries={countries} />
              </div>
            );
          })}
          <Button
            type="submit"
            className="w-full h-11 bg-primary hover:bg-primary/90 text-primary-foreground font-semibold"
          >
            Show my options <ArrowRight className="w-4 h-4" />
          </Button>
          <button
            type="button"
            onClick={() => setQuick(false)}
            className="block mx-auto text-xs font-semibold text-muted-foreground hover:text-primary"
          >
            Add country and citizenship too (better scholarship matches)
          </button>
        </form>
      </div>
    );
  }

  const Step = STEPS[step]!;
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

        <StepField stepKey={Step.key} answers={answers} set={set} countries={countries} />

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

type SetAnswer = (k: keyof IntakeAnswers, v: string) => void;

const inputCls =
  "w-full h-10 px-3 rounded-lg border border-input bg-background text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary";

// Countries come from the live university data, so every country we cover is offered.
function RegionSelect({
  value,
  set,
  countries,
}: {
  value: string;
  set: SetAnswer;
  countries: string[];
}) {
  const options =
    value === "Open to anywhere" || countries.includes(value) ? countries : [...countries, value];
  return (
    <select value={value} onChange={(e) => set("region", e.target.value)} className={inputCls}>
      <option>Open to anywhere</option>
      {options.map((c) => (
        <option key={c}>{c}</option>
      ))}
    </select>
  );
}

function BudgetSlider({ value, set }: { value: string; set: SetAnswer }) {
  const n = Number(value);
  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <label className="text-xs font-semibold uppercase text-muted-foreground">
          Annual budget (USD)
        </label>
        <span className="font-mono text-sm font-bold text-foreground">
          {n >= BUDGET_MAX ? "No limit" : `$${n.toLocaleString()}/yr`}
        </span>
      </div>
      <input
        type="range"
        min={BUDGET_MIN}
        max={BUDGET_MAX}
        step="5000"
        value={value}
        onChange={(e) => set("budget", e.target.value)}
        className="w-full accent-primary"
        aria-label="Annual budget in US dollars"
      />
      <div className="flex justify-between text-[10px] text-muted-foreground">
        <span>${BUDGET_MIN / 1000}k</span>
        <span>$90k+ (no limit)</span>
      </div>
    </div>
  );
}

function ResultsFilters({
  answers,
  set,
  countries,
  onEditAll,
}: {
  answers: IntakeAnswers;
  set: SetAnswer;
  countries: string[];
  onEditAll: () => void;
}) {
  return (
    <div className="bg-card border border-border rounded-2xl p-5 shadow-xs space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="space-y-2">
          <label className="text-xs font-semibold uppercase text-muted-foreground">Country</label>
          <RegionSelect value={answers.region} set={set} countries={countries} />
        </div>
        <div className="space-y-2">
          <label className="text-xs font-semibold uppercase text-muted-foreground">Subject</label>
          <input
            type="text"
            placeholder="e.g. Economics (leave empty for any)"
            value={answers.subject}
            onChange={(e) => set("subject", e.target.value)}
            className={inputCls}
          />
        </div>
        <BudgetSlider value={answers.budget} set={set} />
      </div>
      <button onClick={onEditAll} className="text-xs font-semibold text-primary hover:underline">
        Edit all my answers (curriculum, grades, citizenship…)
      </button>
    </div>
  );
}

function StepField({
  stepKey,
  answers,
  set,
  countries,
}: {
  stepKey: string;
  answers: IntakeAnswers;
  set: SetAnswer;
  countries: string[];
}) {
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
      return <RegionSelect value={answers.region} set={set} countries={countries} />;
    case "budget":
      return <BudgetSlider value={answers.budget} set={set} />;
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
