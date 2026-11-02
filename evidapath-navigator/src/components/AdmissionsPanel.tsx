import { useEffect, useState } from "react";
import { BookOpen, CalendarDays, ClipboardCheck, Info, Target, Users } from "lucide-react";
import type { University } from "../lib/mock-data";
import {
  isCompetitive,
  keyFigure,
  otherTermsNote,
  sentences,
  shortQualification,
} from "../lib/requirement-summary";

type Admission = NonNullable<University["admissionsByCurriculum"]>[number];
type Deadline = NonNullable<University["deadlines"]>[number];

// The qualification a student last picked, so every card opens on it.
const QUAL_KEY = "evidapath.qualification";
function storedQualification(): string | null {
  try {
    return localStorage.getItem(QUAL_KEY);
  } catch {
    return null;
  }
}
function storeQualification(q: string) {
  try {
    localStorage.setItem(QUAL_KEY, q);
  } catch {
    /* private mode — the choice just isn't remembered */
  }
}

const DAY_MS = 86_400_000;
function daysUntil(date: string): number | null {
  const day = date.slice(0, 10);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(day)) return null;
  const today = new Date(new Date().toISOString().slice(0, 10)).getTime();
  return Math.round((new Date(day).getTime() - today) / DAY_MS);
}
function prettyDate(date: string): string {
  const day = date.slice(0, 10);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(day)) return date;
  return new Date(`${day}T00:00:00Z`).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  });
}

export function AdmissionsPanel({
  deadlines,
  admissions,
}: {
  deadlines: Deadline[] | undefined;
  admissions: Admission[] | undefined;
}) {
  return (
    <div className="mt-3 space-y-4">
      {deadlines && deadlines.length > 0 && <Deadlines deadlines={deadlines} />}
      {admissions && admissions.length > 0 && <Requirements admissions={admissions} />}
    </div>
  );
}

function Deadlines({ deadlines }: { deadlines: Deadline[] }) {
  return (
    <div className="space-y-1.5">
      <p className="text-[10px] uppercase font-semibold text-muted-foreground">
        Application deadlines
      </p>
      {deadlines.map((d, i) => {
        const days = d.deadline ? daysUntil(d.deadline) : null;
        return (
          <div
            key={i}
            className="flex items-center gap-2.5 rounded-lg border border-border/70 px-2.5 py-2"
          >
            <CalendarDays className="w-4 h-4 text-primary shrink-0" />
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-foreground truncate">
                {d.label}
                {d.binding && (
                  <span className="ml-1.5 text-[10px] font-semibold text-bronze">binding</span>
                )}
              </p>
              <p className="text-muted-foreground">
                {d.deadline ? prettyDate(d.deadline) : "Date not published"}
                {d.decisionDate ? ` · decision ${prettyDate(d.decisionDate)}` : ""}
              </p>
            </div>
            {days != null && (
              <span
                className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-semibold ${
                  days < 0
                    ? "bg-secondary text-muted-foreground"
                    : days <= 60
                      ? "bg-bronze/10 text-bronze"
                      : "bg-accent text-accent-foreground"
                }`}
              >
                {days < 0 ? "passed" : days === 0 ? "today" : `in ${days} days`}
              </span>
            )}
          </div>
        );
      })}
      {deadlines[0]?.platform && (
        <p className="text-[10px] text-muted-foreground">Apply via {deadlines[0].platform}</p>
      )}
    </div>
  );
}

function Requirements({ admissions }: { admissions: Admission[] }) {
  const names = admissions.map((a) => shortQualification(a.curriculum));
  // Two rows with the same short name keep their full names on the tab.
  const tabs = names.map((n, i) =>
    names.indexOf(n) === names.lastIndexOf(n) ? n : admissions[i]!.curriculum,
  );
  const [picked, setPicked] = useState(0);
  // After hydration, open on the qualification the student picked last time.
  const namesKey = names.join("|");
  useEffect(() => {
    const q = storedQualification();
    const i = q ? namesKey.split("|").indexOf(q) : -1;
    if (i >= 0) setPicked(i);
  }, [namesKey]);
  const a = admissions[Math.min(picked, admissions.length - 1)]!;
  const fig = keyFigure(a.curriculum, a.threshold);
  const note = a.threshold ? otherTermsNote(a.curriculum, a.threshold) : null;

  return (
    <div className="space-y-2">
      <p className="text-[10px] uppercase font-semibold text-muted-foreground">
        Entry requirements — pick your qualification
      </p>
      <div className="flex flex-wrap gap-1.5" role="tablist">
        {tabs.map((t, i) => (
          <button
            key={i}
            type="button"
            role="tab"
            aria-selected={i === picked}
            title={admissions[i]!.curriculum}
            onClick={() => {
              setPicked(i);
              storeQualification(names[i]!);
            }}
            className={`rounded-full px-2.5 py-1 text-[11px] font-semibold border ${
              i === picked
                ? "bg-primary text-primary-foreground border-primary"
                : "bg-background text-foreground border-border hover:border-primary/50"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="rounded-xl bg-secondary/40 p-3 space-y-3 page-enter" key={picked}>
        <p className="text-[11px] font-medium text-muted-foreground">{a.curriculum}</p>

        {fig?.kind === "figure" && (
          <div className="flex items-end gap-3">
            <div>
              <p className="font-display text-3xl font-extrabold leading-none text-foreground">
                {fig.value}
              </p>
              <p className="mt-1 text-[11px] text-muted-foreground">{fig.label}</p>
            </div>
            {isCompetitive(a.threshold) && (
              <span className="mb-4 rounded-full bg-bronze/10 px-2 py-0.5 text-[10px] font-semibold text-bronze">
                competitive — can be higher
              </span>
            )}
          </div>
        )}
        {a.summary && (
          <div className="flex items-start gap-2.5 rounded-lg bg-background border border-border/70 p-2.5">
            <Target className="w-4 h-4 text-primary shrink-0 mt-0.5" />
            <div>
              <p className="text-[10px] uppercase font-semibold text-primary">What you need</p>
              <p className="text-[13px] leading-relaxed text-foreground">{a.summary}</p>
            </div>
          </div>
        )}
        {!a.summary && fig?.kind === "holistic" && (
          <div className="flex items-start gap-2">
            <Users className="w-5 h-5 text-primary shrink-0" />
            <div>
              <p className="font-semibold text-foreground">No fixed grade cutoff</p>
              <p className="text-muted-foreground">Your whole application is reviewed.</p>
            </div>
          </div>
        )}
        {!a.summary && fig?.kind === "unverified" && (
          <p className="font-semibold text-bronze">Grade requirement not verified yet</p>
        )}

        {a.subjects.length > 0 && (
          <div className="space-y-1">
            <p className="text-[10px] uppercase font-semibold text-muted-foreground">Subjects</p>
            <div className="flex flex-wrap gap-1.5">
              {a.subjects.map((s) => (
                <span
                  key={s}
                  className="inline-flex items-center gap-1 rounded-md bg-background border border-border px-2 py-0.5 text-foreground"
                >
                  <BookOpen className="w-3 h-3 text-primary" />
                  {s}
                </span>
              ))}
            </div>
          </div>
        )}

        {a.tests.length > 0 && (
          <div className="space-y-1">
            <p className="text-[10px] uppercase font-semibold text-muted-foreground">Tests</p>
            <div className="flex flex-wrap gap-1.5">
              {a.tests.map((t) => (
                <span
                  key={t}
                  className="inline-flex items-center gap-1 rounded-md bg-background border border-border px-2 py-0.5 text-foreground"
                >
                  <ClipboardCheck className="w-3 h-3 text-primary" />
                  {t}
                </span>
              ))}
            </div>
          </div>
        )}

        {note && (
          <p className="flex items-start gap-1.5 text-[11px] text-bronze">
            <Info className="w-3.5 h-3.5 shrink-0 mt-px" />
            {note}
          </p>
        )}

        {/* The research wording, only until a plain summary is written. */}
        {a.threshold && !a.summary && (
          <details open={!fig}>
            <summary className="cursor-pointer select-none text-[11px] font-semibold text-primary">
              {fig ? "Full wording from the university" : "What the university asks for"}
            </summary>
            <ul className="mt-1.5 space-y-1 list-disc pl-4 text-muted-foreground">
              {sentences(a.threshold).map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </details>
        )}
      </div>
    </div>
  );
}
