import { Link, useNavigate } from "@tanstack/react-router";
import {
  ArrowLeft,
  BookOpen,
  CalendarDays,
  ExternalLink,
  FileText,
  GraduationCap,
  Info,
  Languages,
  MapPin,
  Plane,
} from "lucide-react";
import { useState, type ReactNode } from "react";
import { FitCta } from "./FitCta";
import { SearchSelect } from "./SearchSelect";
import { countryHue } from "./UniversityCard";
import { formatCost, NOT_PUBLISHED } from "../lib/format";
import type { CostView, ProgramView, University } from "../lib/mock-data";
import { countryCostPath, coursePath } from "../lib/paths";

// A university's page, one course at a time: the student types or picks a course and sees
// it as a "course pass" (length, yearly money, entry rules by qualification). Every line of
// text is the stored wording, only split into sentences and sorted under icons; nothing is
// summarised or reworded, so no figure can drift from its source. Each course has its own
// URL (/universities/<uni>/<course>), rendered on the server for search engines.

// International students first: they are who the site is for.
const TIER_ORDER = ["international", "uniform", "eu", "home", "domestic", "national"];

// The qualification a student last looked at, kept while they switch courses.
let lastCurriculum: string | null = null;

function longDate(iso: string | null): string {
  if (!iso) return NOT_PUBLISHED;
  const d = new Date(iso);
  return Number.isNaN(d.getTime())
    ? iso
    : d.toLocaleDateString("en-GB", {
        day: "numeric",
        month: "long",
        year: "numeric",
        timeZone: "UTC",
      });
}

type Group = "grades" | "needed" | "english" | "note";
const GROUPS: { key: Group; title: string; icon: ReactNode; tone: string }[] = [
  {
    key: "grades",
    title: "Grades and subjects",
    icon: <GraduationCap className="w-4 h-4" />,
    tone: "text-primary bg-primary/10",
  },
  {
    key: "needed",
    title: "Also needed",
    icon: <FileText className="w-4 h-4" />,
    tone: "text-navy dark:text-stone-200 bg-navy/10 dark:bg-stone-300/10",
  },
  {
    key: "english",
    title: "English",
    icon: <Languages className="w-4 h-4" />,
    tone: "text-sky-700 dark:text-sky-300 bg-sky-500/10",
  },
  {
    key: "note",
    title: "Good to know",
    icon: <Info className="w-4 h-4" />,
    tone: "text-bronze bg-bronze/10",
  },
];

/** The stored wording, split at sentence ends. Text is kept exactly; only the breaks change. */
export function sentences(text: string): string[] {
  return text
    .split(/(?<=[.!?])\s+(?=[A-Z(])/)
    .map((s) => s.trim())
    .filter(Boolean);
}

export function groupOf(s: string): Group {
  if (/^english\b|\bIELTS\b|\bTOEFL\b|\bDuolingo\b|\bPTE\b|\bCambridge English\b/i.test(s))
    return "english";
  if (
    /guideline|competitive|not guarantee|doesn't guarantee|does not guarantee|can be higher|may be higher|vary|varies/i.test(
      s,
    )
  )
    return "note";
  if (
    /statement|recommendation|reference|letter|portfolio|interview|essay|admission tests?|placement test|aptitude|audition|\bCV\b|résumé/i.test(
      s,
    )
  )
    return "needed";
  return "grades";
}

function CoursePicker({
  u,
  programmes,
  slugs,
  index,
}: {
  u: University;
  programmes: ProgramView[];
  slugs: string[];
  index: number;
}) {
  const navigate = useNavigate();
  const fields = [...new Set(programmes.map((p) => p.fieldOfStudy || "Other"))].sort();
  return (
    <div className="rounded-3xl border border-border bg-card p-5 sm:p-6 space-y-3 shadow-sm">
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Pick a course · {programmes.length} at {u.name}
        </p>
        <SearchSelect
          aria-label={`Course at ${u.name}`}
          value={String(index)}
          onChange={(v) => {
            const s = slugs[Number(v)];
            if (s) void navigate({ to: coursePath(u.name, s), resetScroll: false });
          }}
          searchPlaceholder="Type a subject, e.g. Engineering"
          options={programmes.map((p, i) => ({
            value: String(i),
            label: `${p.name}${p.degree ? ` (${p.degree})` : ""}`,
            keywords: [p.fieldOfStudy],
            group: p.fieldOfStudy || "Other",
          }))}
          className="mt-1 w-full h-12 px-4 rounded-2xl border border-input bg-background text-base font-semibold text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
        />
      </div>
      {/* Plain links to every course: search engines follow these, and they double as a
          browse-by-subject list for students who'd rather scan than type. */}
      <details className="text-sm">
        <summary className="cursor-pointer text-primary font-medium inline-flex items-center gap-1">
          <BookOpen className="w-4 h-4" /> Browse all courses by subject
        </summary>
        <div className="mt-3 space-y-3">
          {fields.map((f) => (
            <div key={f}>
              <p className="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
                {f}
              </p>
              <div className="mt-1 flex flex-wrap gap-1.5">
                {programmes.map((p, i) =>
                  (p.fieldOfStudy || "Other") === f ? (
                    <Link
                      key={slugs[i]}
                      to={coursePath(u.name, slugs[i]!)}
                      resetScroll={false}
                      aria-current={i === index ? "page" : undefined}
                      className={`rounded-full border px-3 py-1 text-xs ${
                        i === index
                          ? "border-primary bg-primary text-primary-foreground"
                          : "border-border hover:border-primary/50 hover:text-primary"
                      }`}
                    >
                      {p.name}
                      {p.degree ? ` (${p.degree})` : ""}
                    </Link>
                  ) : null,
                )}
              </div>
            </div>
          ))}
        </div>
      </details>
    </div>
  );
}

/** The years of the degree as stops on a route. */
function YearRoute({ years }: { years: number }) {
  if (!(years > 0)) return <p className="text-sm text-muted-foreground">Length not published</p>;
  const stops = Math.ceil(years);
  return (
    <div>
      <div className="flex items-center" aria-hidden>
        {Array.from({ length: stops }, (_, i) => (
          <div key={i} className="flex items-center flex-1 last:flex-none">
            <span className="grid place-items-center w-8 h-8 rounded-full border-2 border-primary bg-card text-[11px] font-bold text-primary">
              Y{i + 1}
            </span>
            {i < stops - 1 ? (
              <span className="flex-1 border-t-2 border-dashed border-primary/40 mx-1" />
            ) : null}
          </div>
        ))}
        <GraduationCap className="w-6 h-6 text-primary ml-2 shrink-0" />
      </div>
      <p className="mt-1 text-xs text-muted-foreground">{years} years full time</p>
    </div>
  );
}

/** One year's money as a split bar, then the amounts. */
function MoneyBar({ c }: { c: CostView }) {
  const parts = [
    { label: "Tuition", v: c.tuitionPerYear, cls: "bg-navy dark:bg-stone-300" },
    { label: "Compulsory fees", v: c.mandatoryFees, cls: "bg-bronze" },
    { label: "Living", v: c.livingPerYear, cls: "bg-primary" },
  ];
  const known = parts.reduce((s, p) => s + (p.v ?? 0), 0);
  return (
    <div className="space-y-3">
      {known > 0 ? (
        <div className="flex h-4 w-full overflow-hidden rounded-full bg-secondary" aria-hidden>
          {parts.map((p) =>
            p.v ? (
              <span key={p.label} className={p.cls} style={{ width: `${(p.v / known) * 100}%` }} />
            ) : null,
          )}
        </div>
      ) : null}
      <dl className="grid grid-cols-3 gap-2">
        {parts.map((p) => (
          <div key={p.label} className="rounded-xl bg-secondary/60 p-2.5">
            <dt className="flex items-center gap-1.5 text-[11px] text-muted-foreground">
              <span className={`inline-block w-2 h-2 rounded-full shrink-0 ${p.cls}`} />
              {p.label}
            </dt>
            <dd className="mt-0.5 text-sm font-bold text-foreground leading-tight break-words">
              {formatCost(p.v, c.currency)}
            </dd>
          </div>
        ))}
      </dl>
      {c.livingSource ? (
        <p className="text-xs text-muted-foreground">Living: {c.livingSource}</p>
      ) : null}
    </div>
  );
}

function Money({ p }: { p: ProgramView }) {
  const tiers = p.costTiers?.length
    ? [...p.costTiers].sort((a, b) => TIER_ORDER.indexOf(a.kind) - TIER_ORDER.indexOf(b.kind))
    : [{ kind: "international", label: p.costLabel ?? "All students", costs: p.costs }];
  const [t, setT] = useState(0);
  const tier = tiers[Math.min(t, tiers.length - 1)]!;
  const c = tier.costs;
  return (
    <section className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="font-display font-bold text-foreground">One year costs</h3>
        {tiers.length > 1 ? (
          <div role="tablist" aria-label="Who pays" className="flex flex-wrap gap-1">
            {tiers.map((x, i) => (
              <button
                key={x.label}
                role="tab"
                type="button"
                aria-selected={i === t}
                onClick={() => setT(i)}
                className={`rounded-full px-3 py-1 text-xs font-medium border ${
                  i === t
                    ? "bg-foreground text-background border-foreground"
                    : "border-border text-muted-foreground hover:text-foreground"
                }`}
              >
                {x.label}
              </button>
            ))}
          </div>
        ) : (
          <span className="text-xs text-muted-foreground">{tier.label}</span>
        )}
      </div>
      {p.costs.notChecked ? (
        <p className="text-xs text-amber-700 dark:text-amber-400">
          Not yet re-checked against the university's page.
        </p>
      ) : null}
      <MoneyBar c={c} />
      {c.totalDegree != null ? (
        <p className="rounded-xl border border-dashed border-border px-3 py-2 text-sm">
          <span className="text-muted-foreground">Whole degree: </span>
          <span className="font-bold text-foreground">{formatCost(c.totalDegree, c.currency)}</span>
          <span className="text-xs text-muted-foreground">
            {" "}
            (our calculation: {c.totalIncludes})
          </span>
        </p>
      ) : null}
      {p.costResidencyNote ? (
        <p className="text-xs text-muted-foreground">{p.costResidencyNote}</p>
      ) : null}
    </section>
  );
}

function EnglishTile({ text }: { text: string }) {
  return (
    <div className="rounded-2xl border border-border p-3">
      <p className="flex items-center gap-2 text-xs font-semibold text-foreground">
        <span className="grid place-items-center w-7 h-7 rounded-lg text-sky-700 dark:text-sky-300 bg-sky-500/10">
          <Languages className="w-4 h-4" />
        </span>
        English
      </p>
      <p className="mt-2 text-sm text-muted-foreground">{text}</p>
    </div>
  );
}

function Entry({ p }: { p: ProgramView }) {
  const rows = p.admissionsByCurriculum;
  const [i, setI] = useState(() =>
    Math.max(
      0,
      rows.findIndex((a) => a.curriculum === lastCurriculum),
    ),
  );
  if (!rows.length)
    return (
      <section className="space-y-2">
        <h3 className="font-display font-bold text-foreground">Can I get in?</h3>
        <p className="text-sm text-muted-foreground">Entry requirements: {NOT_PUBLISHED}</p>
        {p.english ? <EnglishTile text={p.english} /> : null}
      </section>
    );
  const a = rows[Math.min(i, rows.length - 1)]!;
  const text = a.summary ?? a.threshold;
  const lines = text ? sentences(text) : [];
  const grouped = GROUPS.map((g) => ({ ...g, lines: lines.filter((s) => groupOf(s) === g.key) }));
  const hasEnglish = grouped.some((g) => g.key === "english" && g.lines.length);
  return (
    <section className="space-y-3">
      <h3 className="font-display font-bold text-foreground">Can I get in?</h3>
      <div role="tablist" aria-label="Your qualification" className="flex flex-wrap gap-1.5">
        {rows.map((r, k) => (
          <button
            key={r.curriculum}
            role="tab"
            type="button"
            aria-selected={k === i}
            onClick={() => {
              setI(k);
              lastCurriculum = r.curriculum;
            }}
            className={`rounded-xl px-3 py-1.5 text-xs font-semibold border text-left ${
              k === i
                ? "bg-primary text-primary-foreground border-primary"
                : "border-border text-muted-foreground hover:text-foreground hover:border-primary/40"
            }`}
          >
            {r.curriculum}
          </button>
        ))}
      </div>
      {a.notChecked ? (
        <p className="text-xs text-amber-700 dark:text-amber-400">
          Not yet re-checked against the university's page.
        </p>
      ) : null}
      {a.subjects.length || a.tests.length ? (
        <div className="flex flex-wrap gap-1.5">
          {a.subjects.map((s) => (
            <span
              key={s}
              className="inline-flex items-center gap-1 rounded-full bg-primary/10 text-primary px-2.5 py-1 text-xs font-medium"
            >
              <BookOpen className="w-3 h-3" /> {s}
            </span>
          ))}
          {a.tests.map((s) => (
            <span
              key={s}
              className="inline-flex items-center gap-1 rounded-full bg-navy/10 dark:bg-stone-300/10 text-foreground px-2.5 py-1 text-xs font-medium"
            >
              <FileText className="w-3 h-3" /> {s}
            </span>
          ))}
        </div>
      ) : null}
      {lines.length ? (
        <div className="grid sm:grid-cols-2 gap-2">
          {grouped
            .filter((g) => g.lines.length)
            .map((g) => (
              <div
                key={g.key}
                className={`rounded-2xl border border-border p-3 ${g.key === "grades" ? "sm:col-span-2" : ""}`}
              >
                <p className="flex items-center gap-2 text-xs font-semibold text-foreground">
                  <span className={`grid place-items-center w-7 h-7 rounded-lg ${g.tone}`}>
                    {g.icon}
                  </span>
                  {g.title}
                </p>
                <ul className="mt-2 space-y-1.5 text-sm text-muted-foreground">
                  {g.lines.map((s) => (
                    <li key={s} className="flex gap-2">
                      <span className="mt-2 w-1 h-1 rounded-full bg-muted-foreground/60 shrink-0" />
                      <span>{s}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">{NOT_PUBLISHED}</p>
      )}
      {p.english && !hasEnglish ? <EnglishTile text={p.english} /> : null}
    </section>
  );
}

/** The selected course as a ticket: stub on top, perforation, then money and entry. */
function CoursePass({ u, p }: { u: University; p: ProgramView }) {
  const deadlines = (u.deadlines ?? []).filter(
    (d) => d.deadline && (!d.program || d.program === p.name),
  );
  return (
    <article className="relative rounded-3xl border border-border bg-card shadow-md overflow-hidden">
      <header
        className="uni-band px-5 sm:px-7 pt-5 pb-6 space-y-4"
        style={{ ["--band-h" as string]: countryHue(u.country) }}
      >
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              <Plane className="w-3.5 h-3.5" /> Course pass · {u.city}, {u.country}
            </p>
            <h2 className="mt-1 font-display font-bold text-2xl sm:text-3xl text-foreground leading-tight">
              {p.name}
            </h2>
            <p className="mt-2 flex flex-wrap gap-1.5 text-xs">
              {p.degree ? (
                <span className="rounded-full bg-foreground text-background px-2.5 py-0.5 font-semibold">
                  {p.degree}
                </span>
              ) : null}
              {p.fieldOfStudy ? (
                <span className="rounded-full border border-border bg-card/70 px-2.5 py-0.5 text-muted-foreground">
                  {p.fieldOfStudy}
                </span>
              ) : null}
              {p.languages?.length ? (
                <span className="rounded-full border border-border bg-card/70 px-2.5 py-0.5 text-muted-foreground">
                  Taught in {p.languages.join(", ").toUpperCase()}
                </span>
              ) : null}
            </p>
          </div>
          <span className="text-4xl leading-none">{u.flag}</span>
        </div>
        <YearRoute years={p.durationYears} />
      </header>

      {/* Perforation with punched notches, like a tear-off ticket stub. */}
      <div className="relative h-0" aria-hidden>
        <span className="absolute -left-3 -top-3 w-6 h-6 rounded-full bg-background border border-border" />
        <span className="absolute -right-3 -top-3 w-6 h-6 rounded-full bg-background border border-border" />
        <span className="block border-t-2 border-dashed border-border mx-5" />
      </div>

      <div className="px-5 sm:px-7 py-6 space-y-7">
        <Money p={p} />
        <Entry p={p} />
        {deadlines.length ? (
          <section className="space-y-2">
            <h3 className="font-display font-bold text-foreground">Deadlines</h3>
            <ol className="space-y-2">
              {deadlines.map((d) => (
                <li
                  key={`${d.label}-${d.deadline}`}
                  className="flex items-start gap-3 rounded-2xl border border-border p-3"
                >
                  <span className="grid place-items-center w-9 h-9 rounded-xl bg-bronze/10 text-bronze shrink-0">
                    <CalendarDays className="w-4 h-4" />
                  </span>
                  <span className="text-sm">
                    <span className="block font-semibold text-foreground">
                      {longDate(d.deadline)}
                    </span>
                    <span className="text-muted-foreground">
                      {d.label}
                      {d.binding ? " · binding" : ""}
                      {d.platform ? ` · apply via ${d.platform}` : ""}
                    </span>
                  </span>
                </li>
              ))}
            </ol>
          </section>
        ) : null}
      </div>
    </article>
  );
}

export function CourseExplorer({
  u,
  index,
  slugs,
}: {
  u: University;
  index: number;
  slugs: string[];
}) {
  const programmes = u.programDetails ?? [];
  const p = programmes[index];
  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-10 space-y-6">
      <Link
        to="/universities"
        className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-primary"
      >
        <ArrowLeft className="w-4 h-4" /> All universities
      </Link>

      <header className="space-y-2">
        <h1 className="font-display font-bold text-3xl sm:text-4xl text-foreground leading-tight">
          {u.name}
        </h1>
        <p className="text-sm text-muted-foreground flex flex-wrap items-center gap-x-3 gap-y-1">
          <span className="inline-flex items-center gap-1">
            <MapPin className="w-4 h-4" /> {u.city}, {u.country}
          </span>
          {u.type ? <span>{u.type}</span> : null}
          {u.lastVerified ? <span>Checked: {u.lastVerified}</span> : null}
        </p>
        <p className="text-sm text-muted-foreground">
          Figures come from {u.name}'s own pages. Where one isn't published, we say so. Confirm with
          the university before you apply or pay.
        </p>
        <div className="flex flex-wrap gap-3 text-sm">
          {u.officialSourceUrl ? (
            <a
              href={u.officialSourceUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-primary underline"
            >
              Official website <ExternalLink className="w-3.5 h-3.5" />
            </a>
          ) : null}
          <Link to={countryCostPath(u.country)} className="text-primary underline">
            Cost of studying in {u.country}
          </Link>
        </div>
      </header>

      <CoursePicker u={u} programmes={programmes} slugs={slugs} index={index} />

      {p ? <CoursePass key={slugs[index]} u={u} p={p} /> : null}

      <FitCta />

      <p className="text-sm text-muted-foreground">
        Missing a course?{" "}
        <Link to="/universities" hash="request-university" className="text-primary underline">
          Ask us to add it
        </Link>
        .
      </p>
    </div>
  );
}
