import { useMemo, useState } from "react";
import { Link } from "@tanstack/react-router";
import { ArrowRight, UserRound } from "lucide-react";
import type { University } from "../lib/mock-data";
import type { LiveData } from "../lib/use-live-data";
import { analyze, type StudentInput } from "../lib/decision-engine";
import { AnalysisFootnote, DecisionAnalysisView } from "./DecisionAnalysisView";

// Home-page demo: a SAMPLE student run through the real decision engine on
// live, verified university data. The student is fictional; the numbers are not.

const STUDENTS: { key: string; label: string; input: StudentInput }[] = [
  {
    key: "emirati-cs",
    label: "Emirati student · IB 34–36 · Computer Science · $50k/yr",
    input: {
      curriculum: "IB Diploma",
      gradeBand: "Competitive: IB 34-36 / AAA-AAB / GPA 3.6-3.7",
      subject: "Computer Science",
      budgetUsd: 50000,
      citizenship: "UAE",
    },
  },
  {
    key: "expat-econ",
    label: "Indian expat in Dubai · A*AA · Economics · $35k/yr",
    input: {
      curriculum: "Cambridge A-Levels",
      gradeBand: "Strong: IB 37-39 / A*AA / GPA 3.8-3.9",
      subject: "Economics",
      budgetUsd: 35000,
      citizenship: "India",
    },
  },
];

const UNIS: { id: string; label: string }[] = [
  { id: "ae-nyu-abu-dhabi", label: "NYU Abu Dhabi" },
  { id: "au-unimelb", label: "Melbourne" },
  { id: "uk-imperial", label: "Imperial" },
  { id: "nl-tu-delft", label: "TU Delft" },
];

export function DecisionModelDemo({ data }: { data: LiveData | null }) {
  const [studentKey, setStudentKey] = useState(STUDENTS[0]!.key);
  const [uniId, setUniId] = useState(UNIS[0]!.id);
  const unis = data?.universities ?? [];
  const schols = data?.scholarships ?? [];
  const fx = data?.fx ?? null;
  const loaded = !!data;

  const choices = UNIS.map((c) => ({ ...c, u: unis.find((u) => u.id === c.id) })).filter(
    (c): c is { id: string; label: string; u: University } => !!c.u,
  );
  const student = STUDENTS.find((s) => s.key === studentKey)!;
  const univ = (choices.find((c) => c.id === uniId) ?? choices[0])?.u;
  const analysis = useMemo(
    () => (univ ? analyze(univ, student.input, schols, unis, fx) : null),
    [univ, student, schols, unis, fx],
  );

  return (
    <div className="rounded-2xl border border-border bg-card p-6 md:p-8 shadow-sm space-y-6">
      <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-4 pb-5 border-b border-border">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-primary">
            Live decision analysis
          </span>
          <h3 className="text-xl md:text-2xl font-display font-bold text-foreground mt-0.5">
            The EvidaPath Decision Model in Action
          </h3>
          <p className="text-xs sm:text-sm text-muted-foreground mt-1">
            A sample student, run against real verified university data. Pick a student and a
            university.
          </p>
        </div>
        <Link
          to="/find-my-path"
          className="inline-flex items-center gap-1.5 text-sm font-semibold text-primary hover:underline shrink-0"
        >
          Run it on your own profile <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      <div className="flex flex-col gap-3">
        <div className="flex flex-wrap gap-2" role="tablist" aria-label="Sample student">
          {STUDENTS.map((s) => (
            <button
              key={s.key}
              role="tab"
              aria-selected={s.key === studentKey}
              onClick={() => setStudentKey(s.key)}
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
                s.key === studentKey
                  ? "bg-primary text-primary-foreground border-primary"
                  : "bg-card text-muted-foreground border-border hover:text-foreground hover:border-foreground/30"
              }`}
            >
              <UserRound className="w-3.5 h-3.5" />
              {s.label}
            </button>
          ))}
        </div>
        <div
          className="flex flex-wrap gap-1 bg-secondary/70 p-1 rounded-lg border border-border w-fit"
          role="tablist"
          aria-label="University"
        >
          {choices.map((c) => (
            <button
              key={c.id}
              role="tab"
              aria-selected={c.id === univ?.id}
              onClick={() => setUniId(c.id)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                c.id === univ?.id
                  ? "bg-card text-foreground shadow-xs font-semibold"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {c.u.flag} {c.label}
            </button>
          ))}
        </div>
      </div>

      {!loaded ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4" aria-busy="true">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-40 rounded-xl bg-secondary/60 animate-pulse" />
          ))}
        </div>
      ) : univ && analysis ? (
        <>
          <DecisionAnalysisView u={univ} a={analysis} />
          <AnalysisFootnote />
        </>
      ) : (
        <p className="text-sm text-muted-foreground">
          Live university data is unavailable right now — please try again shortly.
        </p>
      )}
    </div>
  );
}
