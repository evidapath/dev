import { createFileRoute, Link } from "@tanstack/react-router";
import { Columns3, X } from "lucide-react";
import { useEffect, useMemo, useState, type ReactNode } from "react";
import { PageHeader } from "../components/PageHeader";
import { SearchSelect } from "../components/SearchSelect";
import { LocalAmount } from "../components/LocalAmount";
import { analyze, fmtDate, type DecisionAnalysis } from "../lib/decision-engine";
import type { University } from "../lib/mock-data";
import { universityOption } from "../lib/university-options";
import { useStudent } from "../lib/use-student";
import { money, verdictFor } from "../lib/verdict";
import { BUDGET_MAX } from "../lib/budget";
import { visaFor } from "../lib/visa";
import { otherTests } from "../lib/tests";
import { canonicalLink, ogUrlMeta } from "../lib/seo";

const MAX = 3;

export const Route = createFileRoute("/compare")({
  validateSearch: (s: Record<string, unknown>): { u?: string } =>
    typeof s["u"] === "string" && s["u"] ? { u: s["u"] } : {},
  head: () => ({
    meta: [
      { title: "Compare Universities — EvidaPath" },
      {
        name: "description",
        content:
          "Compare up to three universities side by side before you apply: cost, entry grades, English test, deadlines, scholarships and visa rules.",
      },
      { property: "og:title", content: "Compare Universities — EvidaPath" },
      ogUrlMeta("/compare"),
    ],
    links: [canonicalLink("/compare")],
  }),
  component: ComparePage,
});

function ComparePage() {
  const { u: fromUrl } = Route.useSearch();
  const { data, input, savedIds, hasProfile, loading } = useStudent();
  const [ids, setIds] = useState<string[]>([]);

  // Start from the URL (?u=a,b,c), else the student's saved universities.
  useEffect(() => {
    if (!data || ids.length) return;
    const known = new Set(data.universities.map((x) => x.id));
    const start = (fromUrl ? fromUrl.split(",") : savedIds).filter((id) => known.has(id));
    setIds(start.slice(0, MAX));
  }, [data, savedIds, fromUrl, ids.length]);

  const cols = useMemo(() => {
    if (!data) return [];
    return ids.flatMap((id) => {
      const u = data.universities.find((x) => x.id === id);
      return u ? [{ u, a: analyze(u, input, data.scholarships, data.universities, data.fx) }] : [];
    });
  }, [data, ids, input]);

  const options = (data?.universities ?? [])
    .filter((u) => !ids.includes(u.id))
    .map((u) =>
      universityOption(
        u,
        u.name,
        savedIds.includes(u.id) ? "Saved to your path" : "All universities",
      ),
    )
    .sort((a, b) => (a.group === b.group ? 0 : a.group === "Saved to your path" ? -1 : 1));

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <PageHeader
        icon={Columns3}
        eyebrow="Compare"
        title="Compare before"
        accent="you apply."
        intro="Up to three universities side by side: what a year costs you, the grades and English test they ask for, deadlines, scholarships and visa rules."
        note={
          hasProfile
            ? `Judged for you: ${input.curriculum}, ${input.subject}, budget $${input.budgetUsd.toLocaleString()}/yr.`
            : "Answer Find My Path to see costs and grades judged for you."
        }
      >
        <div className="flex flex-wrap items-center gap-2">
          {cols.map(({ u }) => (
            <span
              key={u.id}
              className="inline-flex items-center gap-1.5 h-9 pl-3 pr-1.5 rounded-full border border-border bg-card text-xs font-semibold"
            >
              {u.flag} {u.shortName || u.name}
              <button
                onClick={() => setIds((cur) => cur.filter((x) => x !== u.id))}
                aria-label={`Remove ${u.name}`}
                className="w-6 h-6 rounded-full hover:bg-secondary inline-flex items-center justify-center"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </span>
          ))}
          {ids.length < MAX && (
            <SearchSelect
              aria-label="Add a university"
              options={options}
              value=""
              onChange={(v) => v && setIds((cur) => [...cur, v].slice(0, MAX))}
              placeholder="+ Add a university"
              searchPlaceholder="Type a university or country…"
              className="h-9 px-3 rounded-full border border-dashed border-primary/50 bg-background text-xs font-semibold text-primary min-w-48"
            />
          )}
        </div>
      </PageHeader>

      {loading ? (
        <div className="h-64 rounded-2xl bg-secondary/60 animate-pulse" />
      ) : cols.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          Add two or three universities above to compare them.
        </p>
      ) : (
        <div className="overflow-x-auto rounded-2xl border border-border bg-card shadow-xs">
          <table className="w-full min-w-[640px] text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="w-40 p-4" />
                {cols.map(({ u }) => (
                  <th key={u.id} className="p-4 text-left align-top">
                    <p className="font-display font-bold text-foreground">
                      {u.flag} {u.name}
                    </p>
                    <p className="text-xs font-normal text-muted-foreground">
                      {u.city}, {u.country}
                    </p>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {ROWS.map(([label, cell]) => (
                <tr key={label} className="border-b border-border/60 last:border-0 align-top">
                  <th
                    scope="row"
                    className="p-4 text-left text-xs font-semibold text-muted-foreground"
                  >
                    {label}
                  </th>
                  {cols.map(({ u, a }) => (
                    <td key={u.id} className="p-4 text-xs text-foreground">
                      {cell(u, a, input.budgetUsd)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <p className="text-[11px] text-muted-foreground">
        Costs from official university and government pages, converted to US dollars at official
        rates. Visa figures from government pages. Check each official page before you apply.
      </p>
    </div>
  );
}

const muted = (t: string) => <span className="text-muted-foreground">{t}</span>;

const ROWS: [string, (u: University, a: DecisionAnalysis, budget: number) => ReactNode][] = [
  [
    "Programme",
    (_u, a) => (
      <>
        {a.programName}
        {a.financial.years ? muted(` · ${a.financial.years} years`) : null}
      </>
    ),
  ],
  [
    "Cost per year",
    (_u, a) =>
      a.financial.annualUsd == null ? (
        muted("Not published")
      ) : (
        <>
          <span className="font-mono font-bold">{money(a.financial.annualUsd)}</span>
          {muted(a.financial.annualComplete ? " all-in" : " tuition only")}
          <LocalAmount usd={a.financial.annualUsd} />
        </>
      ),
  ],
  [
    "Whole degree",
    (_u, a) =>
      a.financial.degreeUsd == null ? muted("Not published") : money(a.financial.degreeUsd),
  ],
  [
    "Against your budget",
    (_u, a, budget) => {
      const v = verdictFor(a, budget, budget >= BUDGET_MAX);
      return <span className="font-semibold">{v.headline}</span>;
    },
  ],
  [
    "Entry grades for you",
    (_u, a) => (
      <>
        <span className="font-semibold">{a.academic.headline}</span>
        {a.academic.requirement && (
          <p className="text-muted-foreground mt-0.5 line-clamp-3">{a.academic.requirement}</p>
        )}
      </>
    ),
  ],
  ["English test", (_u, a) => (a.program?.english ? a.program.english : muted("Not published"))],
  [
    "Other tests",
    (_u, a) => {
      const t = otherTests(a.program);
      return t.length ? t.join(" · ") : muted("None listed");
    },
  ],
  [
    "Next deadline",
    (_u, a) =>
      a.admissions.nextDeadline ? (
        <>
          <span className="font-semibold">{fmtDate(a.admissions.nextDeadline.date)}</span>
          {muted(` · ${a.admissions.nextDeadline.label}`)}
        </>
      ) : (
        muted("No upcoming date published")
      ),
  ],
  [
    "Scholarships for you",
    (_u, a) => {
      const f = a.financial.funding;
      const g = f.filter((x) => x.basis === "guaranteed" && x.eligible === "yes").length;
      return f.length ? `${f.length} to try${g ? ` · ${g} guaranteed` : ""}` : muted("None found");
    },
  ],
  [
    "Visa money",
    (u) => {
      const v = visaFor(u.country);
      const m = v?.money.find((x) => /money to show/i.test(x.label));
      return m ? m.value : muted("See official visa pages");
    },
  ],
  ["Work after graduating", (u) => visaFor(u.country)?.after ?? muted("See official visa pages")],
  [
    "",
    (u) => (
      <Link
        to="/analyze"
        search={{ uni: u.id }}
        className="text-primary font-semibold hover:underline"
      >
        Full analysis →
      </Link>
    ),
  ],
];
