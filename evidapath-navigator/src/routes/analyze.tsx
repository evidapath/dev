import { useUniversitiesFn, useScholarshipsFn, useFxRatesFn } from "../lib/use-live-data";
import { PageGuide } from "../components/PageGuide";
import { createFileRoute, Link } from "@tanstack/react-router";
import { useServerFn } from "@tanstack/react-start";
import { useEffect, useMemo, useState } from "react";
import { BarChart3, Pencil } from "lucide-react";
import { requireAuth } from "../lib/route-guard";
import { type FxRates } from "../lib/fx.functions";
import { getProfile, listSavedUniversities } from "../lib/profile.functions";
import type { Scholarship, University } from "../lib/mock-data";
import { analyze, type StudentInput } from "../lib/decision-engine";
import { BUDGET_MAX, BUDGET_MIN } from "../lib/budget";
import { AnalysisFootnote, DecisionAnalysisView } from "../components/DecisionAnalysisView";
import { canonicalLink, ogUrlMeta } from "../lib/seo";

export const Route = createFileRoute("/analyze")({
  head: () => ({
    meta: [
      { title: "Analyze Your Fit — EvidaPath" },
      {
        name: "description",
        content:
          "Compare your grades, budget and citizenship with a university's verified requirements, costs and scholarships.",
      },
      { property: "og:title", content: "Analyze Your Fit — EvidaPath" },
      {
        property: "og:description",
        content:
          "Verified requirements, real costs, scholarships you qualify for and your next steps.",
      },
      ogUrlMeta("/analyze"),
    ],
    links: [canonicalLink("/analyze")],
  }),
  validateSearch: (s: Record<string, unknown>): { uni?: string } =>
    typeof s["uni"] === "string" && s["uni"] ? { uni: s["uni"] } : {},
  beforeLoad: ({ context, location }) => requireAuth(context, location.pathname),
  component: AnalyzePage,
});

const CURRICULA = [
  "IB Diploma",
  "Cambridge A-Levels",
  "US High School Diploma + APs",
  "German Abitur",
  "National Curriculum / Other",
];
const BANDS = [
  "Top Tier: IB 40+ / A*A*A / GPA 4.0",
  "Strong: IB 37-39 / A*AA / GPA 3.8-3.9",
  "Competitive: IB 34-36 / AAA-AAB / GPA 3.6-3.7",
  "Foundation: IB 30-33 / ABB-BBB / GPA 3.3-3.5",
];
const DEFAULT_INPUT: StudentInput = {
  curriculum: "IB Diploma",
  gradeBand: BANDS[1]!,
  subject: "Computer Science",
  budgetUsd: 40000,
  citizenship: "",
};

const field =
  "w-full h-10 px-3 rounded-lg border border-input bg-background text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary";
const label =
  "block text-[11px] font-semibold uppercase tracking-wide text-muted-foreground mb-1.5";

function AnalyzePage() {
  const { uni } = Route.useSearch();
  const [unis, setUnis] = useState<University[]>([]);
  const [schols, setSchols] = useState<Scholarship[]>([]);
  const [fx, setFx] = useState<FxRates | null>(null);
  const [savedIds, setSavedIds] = useState<string[]>([]);
  const [input, setInput] = useState<StudentInput>(DEFAULT_INPUT);
  const [fromProfile, setFromProfile] = useState(false);
  const [uniId, setUniId] = useState(uni ?? "");
  const [loading, setLoading] = useState(true);

  const fetchUnis = useUniversitiesFn();
  const fetchSchols = useScholarshipsFn();
  const fetchFx = useFxRatesFn();
  const fetchProfile = useServerFn(getProfile);
  const fetchSaved = useServerFn(listSavedUniversities);

  useEffect(() => {
    let live = true;
    Promise.all([
      fetchUnis(),
      fetchSchols(),
      fetchFx().catch(() => null),
      fetchProfile().catch(() => null),
      fetchSaved().catch(() => []),
    ])
      .then(([u, s, r, p, saved]) => {
        if (!live) return;
        setUnis(u.universities);
        setSchols(s.scholarships);
        setFx(r);
        const ids = saved.map((x) => x.sanity_university_id);
        setSavedIds(ids);
        if (p) {
          setFromProfile(true);
          setInput({
            curriculum: p.curriculum || DEFAULT_INPUT.curriculum,
            gradeBand: p.grade_band || DEFAULT_INPUT.gradeBand,
            subject: p.intended_subject || DEFAULT_INPUT.subject,
            budgetUsd: p.annual_budget ?? DEFAULT_INPUT.budgetUsd,
            citizenship: p.citizenship || "",
          });
        }
        setUniId((cur) => cur || ids[0] || u.universities[0]?.id || "");
      })
      .finally(() => live && setLoading(false));
    return () => {
      live = false;
    };
  }, [fetchUnis, fetchSchols, fetchFx, fetchProfile, fetchSaved]);

  const univ = unis.find((u) => u.id === uniId) ?? unis[0];
  const result = useMemo(
    () => (univ ? analyze(univ, input, schols, unis, fx) : null),
    [univ, input, schols, unis, fx],
  );
  const set = <K extends keyof StudentInput>(k: K, v: StudentInput[K]) =>
    setInput((cur) => ({ ...cur, [k]: v }));

  const saved = unis.filter((u) => savedIds.includes(u.id));
  const others = unis.filter((u) => !savedIds.includes(u.id));

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <header className="max-w-3xl space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold">
          <BarChart3 className="w-3.5 h-3.5" />
          <span>Decision Suite • Analyze</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-display font-extrabold text-foreground">
          Analyze your fit
        </h1>
        <p className="text-sm sm:text-base text-muted-foreground leading-relaxed">
          Your grades, budget and citizenship compared with one university's verified requirements,
          costs and scholarships. We never show an admission "chance" — only what is published, and
          what you can still change.
        </p>
      </header>

      <PageGuide
        id="analyze"
        title="Check how one university fits you"
        steps={[
          {
            title: "Choose a university",
            text: "Your saved universities are listed first. Any university in EvidaPath can be picked.",
          },
          {
            title: "Check your inputs",
            text: "They're filled from your profile. Change any of them to try “what if” — it won't change your profile.",
          },
          {
            title: "Read the six panels",
            text: "Grades vs the published requirement, deadlines, real cost vs budget, scholarships you qualify for, other options, and next steps.",
          },
          {
            title: "Act on the next steps",
            text: "The last panel turns gaps into actions. Your Plan page collects them for every saved university.",
          },
        ]}
        tip="EvidaPath never shows an admission “chance” — only what universities publish and what you can still change."
      />

      <section className="bg-card border border-border rounded-2xl p-5 sm:p-6 shadow-xs space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h2 className="font-display font-bold text-base text-foreground">Your inputs</h2>
          <span className="text-[11px] text-muted-foreground inline-flex items-center gap-1">
            <Pencil className="w-3 h-3" />
            {fromProfile
              ? "Filled from your profile — changes here are for this analysis only."
              : "Using example inputs — "}
            {!fromProfile && (
              <Link to="/find-my-path" className="text-primary hover:underline">
                set up your profile
              </Link>
            )}
          </span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="sm:col-span-2 lg:col-span-1">
            <label className={label} htmlFor="an-uni">
              University
            </label>
            <select
              id="an-uni"
              value={univ?.id ?? ""}
              onChange={(e) => setUniId(e.target.value)}
              className={field}
            >
              {saved.length > 0 && (
                <optgroup label="Saved to your path">
                  {saved.map((u) => (
                    <option key={u.id} value={u.id}>
                      {u.flag} {u.name}
                    </option>
                  ))}
                </optgroup>
              )}
              <optgroup label={saved.length ? "All universities" : "Universities"}>
                {others.map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.flag} {u.name}
                  </option>
                ))}
              </optgroup>
            </select>
          </div>
          <div>
            <label className={label} htmlFor="an-subject">
              Subject
            </label>
            <input
              id="an-subject"
              value={input.subject}
              onChange={(e) => set("subject", e.target.value)}
              className={field}
            />
          </div>
          <div>
            <label className={label} htmlFor="an-cit">
              Citizenship
            </label>
            <input
              id="an-cit"
              value={input.citizenship}
              placeholder="e.g. UAE, India"
              onChange={(e) => set("citizenship", e.target.value)}
              className={field}
            />
          </div>
          <div>
            <label className={label} htmlFor="an-cur">
              Curriculum
            </label>
            <select
              id="an-cur"
              value={input.curriculum}
              onChange={(e) => set("curriculum", e.target.value)}
              className={field}
            >
              {(CURRICULA.includes(input.curriculum)
                ? CURRICULA
                : [input.curriculum, ...CURRICULA]
              ).map((c) => (
                <option key={c}>{c}</option>
              ))}
            </select>
          </div>
          <div>
            <label className={label} htmlFor="an-band">
              Predicted grades
            </label>
            <select
              id="an-band"
              value={input.gradeBand}
              onChange={(e) => set("gradeBand", e.target.value)}
              className={field}
            >
              {(BANDS.includes(input.gradeBand) ? BANDS : [input.gradeBand, ...BANDS]).map((b) => (
                <option key={b}>{b}</option>
              ))}
            </select>
          </div>
          <div>
            <label className={label} htmlFor="an-budget">
              Budget per year:{" "}
              {input.budgetUsd >= BUDGET_MAX ? "No limit" : `$${input.budgetUsd.toLocaleString()}`}
            </label>
            <input
              id="an-budget"
              type="range"
              min={BUDGET_MIN}
              max={BUDGET_MAX}
              step={5000}
              value={Math.min(Math.max(input.budgetUsd, BUDGET_MIN), BUDGET_MAX)}
              onChange={(e) => set("budgetUsd", Number(e.target.value))}
              className="w-full accent-primary mt-3"
            />
          </div>
        </div>
      </section>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4" aria-busy="true">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-44 rounded-xl bg-secondary/60 animate-pulse" />
          ))}
        </div>
      ) : univ && result ? (
        <section className="space-y-4" aria-live="polite">
          <DecisionAnalysisView u={univ} a={result} />
          <AnalysisFootnote />
          <div className="flex flex-wrap gap-3 pt-2">
            <Link
              to="/fund"
              className="inline-flex items-center h-10 px-4 rounded-lg bg-primary text-primary-foreground text-sm font-semibold hover:bg-primary/90 transition-colors"
            >
              Build a funding plan
            </Link>
            <Link
              to="/universities"
              className="inline-flex items-center h-10 px-4 rounded-lg border border-border text-sm font-semibold text-foreground hover:bg-secondary transition-colors"
            >
              See full university details
            </Link>
          </div>
        </section>
      ) : (
        <p className="text-sm text-muted-foreground">
          University data is unavailable right now — please try again shortly.
        </p>
      )}
    </div>
  );
}
