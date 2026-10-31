import { useState } from "react";
import { Link } from "@tanstack/react-router";
import {
  AlertTriangle,
  ArrowRight,
  Check,
  CheckCircle2,
  ChevronDown,
  Globe2,
  MapPin,
  Save,
  Sparkles,
  XCircle,
} from "lucide-react";
import { Button } from "./ui/button";
import type { PathwayGroup, PathwayResult, PathwayRow } from "../lib/pathways";
import { fmtDate, usd } from "../lib/decision-engine";
import type { University } from "../lib/mock-data";

const GRADE_LABEL = {
  strong: "Meets requirement",
  edge: "Borderline",
  gap: "Below requirement",
  unknown: "No grade cut-off",
} as const;
const GRADE_TONE = {
  strong: "text-primary",
  edge: "text-bronze",
  gap: "text-destructive",
  unknown: "text-muted-foreground",
} as const;
const ISSUE_ICON = { ok: CheckCircle2, warn: AlertTriangle, bad: XCircle } as const;
const ISSUE_TONE = { ok: "text-primary", warn: "text-bronze", bad: "text-destructive" } as const;

export function PathwayResults({
  result,
  budgetUsd,
  noBudgetLimit,
  region,
  subject,
  savedIds,
  onSave,
}: {
  result: PathwayResult;
  budgetUsd: number;
  noBudgetLimit: boolean;
  region: string;
  subject: string;
  savedIds: Set<string>;
  onSave: (u: University) => void;
}) {
  const { groups } = result;
  const place = result.regionLimited ? region : "anywhere";
  const budgetText = noBudgetLimit ? "any budget" : `your $${budgetUsd.toLocaleString()}/yr budget`;
  const total =
    groups.within.length + groups.stretch.length + groups.unpriced.length + groups.reach.length;

  if (total === 0)
    return (
      <div className="rounded-2xl border border-border bg-card p-8 text-center text-sm text-muted-foreground">
        No universities in EvidaPath offer {subject || "that subject"}{" "}
        {result.regionLimited ? `in ${region}` : ""} yet. Try a broader subject or “Open to
        anywhere”, or{" "}
        <Link to="/universities" className="text-primary font-semibold">
          browse all universities
        </Link>
        .
      </div>
    );

  return (
    <div className="space-y-10">
      {/* Plain-language summary */}
      <div className="rounded-2xl border border-border bg-secondary/40 p-5 space-y-2">
        <p className="text-sm font-semibold text-foreground">
          {result.withinInRegion > 0
            ? `${result.withinInRegion} ${result.withinInRegion === 1 ? "university fits" : "universities fit"} ${budgetText}${result.regionLimited ? ` in ${region}` : ""}.`
            : result.regionLimited
              ? `Nothing in ${region} fits ${budgetText} for ${subject || "this subject"} on published costs.`
              : `Nothing fits ${budgetText} for ${subject || "this subject"} on published costs.`}
          {result.withinElsewhere > 0 &&
            ` ${result.withinElsewhere} ${result.withinElsewhere === 1 ? "option" : "options"} elsewhere ${
              result.withinElsewhere === 1 ? "does" : "do"
            }${
              groups.within.filter((r) => !r.inRegion).every((r) => r.a.taughtIn)
                ? " (taught in German)"
                : ""
            } — shown below.`}
        </p>
        {groups.stretch.length > 0 && (
          <p className="text-sm text-muted-foreground">
            {groups.stretch.length} more {groups.stretch.length === 1 ? "match" : "matches"}{" "}
            {result.regionLimited ? `in ${region}` : ""} cost more — from ≈{" "}
            {usd(groups.stretch[0]!.gapPerYear)}/yr over budget. Each shows how you could close the
            gap.
          </p>
        )}
      </div>

      <Group
        id="within"
        title={noBudgetLimit ? "Fully priced options" : "Within your budget"}
        note={
          noBudgetLimit
            ? "Tuition, fees and living costs all published. Best academic fit first."
            : "All-in yearly cost (tuition, fees and living) fits your budget, after any scholarship you're guaranteed. Best academic fit first."
        }
        rows={groups.within}
        empty={
          result.regionLimited
            ? `No university in ${region} fits ${budgetText} once living costs are included, and none elsewhere does either.`
            : `No university fits ${budgetText} once living costs are included.`
        }
        savedIds={savedIds}
        onSave={onSave}
        regionLabel={result.regionLimited ? region : null}
      />

      {groups.stretch.length > 0 && (
        <Group
          id="stretch"
          title={`Good matches above your budget${result.regionLimited ? ` in ${region}` : ""}`}
          note="These fit your subject and grades but cost more than you said you can spend. Smallest gap first, with the funding routes that could close it."
          rows={groups.stretch}
          savedIds={savedIds}
          onSave={onSave}
          regionLabel={null}
        />
      )}

      {groups.unpriced.length > 0 && (
        <Group
          id="unpriced"
          title="Probably affordable — confirm living costs"
          note="Tuition fits your budget, but the university doesn't publish a living-cost figure we can verify. Budget a margin before you rely on these."
          rows={groups.unpriced}
          savedIds={savedIds}
          onSave={onSave}
          regionLabel={result.regionLimited ? region : null}
        />
      )}

      {groups.reach.length > 0 && (
        <Collapsible
          title={`Reach options${result.regionLimited ? ` in ${region}` : ""} (${groups.reach.length})`}
        >
          <p className="text-xs text-muted-foreground">
            The cost gap is more than your whole budget again, or your predicted grades are below
            the published requirement. Worth knowing about, not worth building a plan around.
          </p>
          <div className="space-y-3">
            {groups.reach.map((r) => (
              <PathwayCard
                key={r.u.id}
                row={r}
                saved={savedIds.has(r.u.id)}
                onSave={onSave}
                regionLabel={null}
              />
            ))}
          </div>
        </Collapsible>
      )}

      <p className="text-[11px] text-muted-foreground">
        Showing {place === "anywhere" ? "all countries" : place}. Costs in USD at European Central
        Bank reference rates (AED at its 3.6725 peg). These are pathways to explore — EvidaPath
        never shows admission chances.
      </p>
    </div>
  );
}

function Group({
  id,
  title,
  note,
  rows,
  empty,
  savedIds,
  onSave,
  regionLabel,
}: {
  id: PathwayGroup;
  title: string;
  note: string;
  rows: PathwayRow[];
  empty?: string;
  savedIds: Set<string>;
  onSave: (u: University) => void;
  regionLabel: string | null;
}) {
  const [showAll, setShowAll] = useState(false);
  const shown = showAll ? rows : rows.slice(0, 6);
  return (
    <section className="space-y-3" aria-labelledby={`group-${id}`}>
      <div>
        <h2 id={`group-${id}`} className="font-display font-bold text-xl text-foreground">
          {title}{" "}
          <span className="text-muted-foreground font-normal text-base">({rows.length})</span>
        </h2>
        <p className="text-xs text-muted-foreground max-w-3xl">{note}</p>
      </div>
      {rows.length === 0 && empty ? (
        <p className="text-sm text-muted-foreground rounded-xl border border-dashed border-border p-4">
          {empty}
        </p>
      ) : (
        <div className="space-y-3">
          {shown.map((r) => (
            <PathwayCard
              key={r.u.id}
              row={r}
              saved={savedIds.has(r.u.id)}
              onSave={onSave}
              regionLabel={regionLabel}
            />
          ))}
          {rows.length > shown.length && (
            <button
              onClick={() => setShowAll(true)}
              className="text-sm font-semibold text-primary hover:underline"
            >
              Show {rows.length - shown.length} more
            </button>
          )}
        </div>
      )}
    </section>
  );
}

function Collapsible({ title, children }: { title: string; children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  return (
    <section className="space-y-3">
      <button
        onClick={() => setOpen(!open)}
        aria-expanded={open}
        className="flex items-center gap-2 font-display font-bold text-lg text-foreground"
      >
        <ChevronDown className={`w-4 h-4 transition-transform ${open ? "rotate-180" : ""}`} />
        {title}
      </button>
      {open && <div className="space-y-3">{children}</div>}
    </section>
  );
}

function PathwayCard({
  row,
  saved,
  onSave,
  regionLabel,
}: {
  row: PathwayRow;
  saved: boolean;
  onSave: (u: University) => void;
  regionLabel: string | null;
}) {
  const { u, a, issue } = row;
  const [open, setOpen] = useState(false);
  const f = a.financial;
  const guaranteed = f.funding.filter((x) => x.basis === "guaranteed" && x.eligible === "yes");
  const toApply = f.funding.filter((x) => x.basis !== "guaranteed");
  const IssueIcon = ISSUE_ICON[issue.tone];
  const outside = regionLabel && !row.inRegion;

  return (
    <article
      className={`rounded-2xl border bg-card shadow-xs overflow-hidden transition-colors ${
        row.group === "stretch" ? "border-bronze/35" : "border-border"
      } hover:border-primary/40`}
    >
      <button
        onClick={() => setOpen(!open)}
        aria-expanded={open}
        className="w-full flex items-center justify-between gap-4 p-5 text-left"
      >
        <div className="flex items-center gap-3 min-w-0">
          <span className="text-2xl shrink-0">{u.flag}</span>
          <div className="min-w-0">
            <h3 className="font-display font-bold text-base text-foreground truncate">{u.name}</h3>
            <p className="text-xs text-muted-foreground flex flex-wrap items-center gap-x-1.5">
              <MapPin className="w-3 h-3" />
              {u.city}, {u.country} · {a.programName}
              {f.years ? ` · ${f.years} yrs` : ""}
              {outside && (
                <span className="inline-flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wide text-bronze bg-bronze/10 rounded px-1.5 py-0.5">
                  <Globe2 className="w-3 h-3" /> Outside {regionLabel}
                </span>
              )}
            </p>
          </div>
        </div>
        <ChevronDown
          className={`w-4 h-4 text-muted-foreground shrink-0 transition-transform ${open ? "rotate-180" : ""}`}
        />
      </button>

      {/* Four answers a student wants at a glance */}
      <div className="px-5 pb-5 grid grid-cols-2 lg:grid-cols-4 gap-4 text-xs border-t border-border pt-4">
        <div>
          <p className="text-muted-foreground">Your grades</p>
          <p className={`font-semibold ${GRADE_TONE[a.academic.level]}`}>
            {a.academic.level === "unknown"
              ? a.academic.aLevelTermsOnly
                ? "Only A-level grades published"
                : /holistic/i.test(a.academic.headline)
                  ? "Holistic review"
                  : "No comparable grade"
              : GRADE_LABEL[a.academic.level]}
          </p>
        </div>
        <div>
          <p className="text-muted-foreground">
            {f.annualComplete ? "Cost per year (all-in)" : "Tuition per year"}
          </p>
          <p className="font-mono font-semibold text-foreground">≈ {usd(f.annualUsd)}</p>
          {guaranteed.length > 0 && row.netAnnualUsd != null && (
            <p className="font-mono text-[11px] text-primary">
              ≈ {usd(row.netAnnualUsd)} after guaranteed aid
            </p>
          )}
        </div>
        <div>
          <p className="text-muted-foreground">Scholarships</p>
          <p className="font-semibold text-foreground">
            {f.funding.length === 0
              ? "None found"
              : [
                  guaranteed.length ? `${guaranteed.length} guaranteed` : "",
                  toApply.length ? `${toApply.length} to apply for` : "",
                ]
                  .filter(Boolean)
                  .join(" · ")}
          </p>
        </div>
        <div>
          <p className="text-muted-foreground">Biggest issue</p>
          <p className={`font-semibold flex items-start gap-1 ${ISSUE_TONE[issue.tone]}`}>
            <IssueIcon className="w-3.5 h-3.5 shrink-0 mt-0.5" />
            {issue.text}
          </p>
        </div>
      </div>

      {/* Over budget: how to close the gap */}
      {row.group === "stretch" && row.gapPerYear != null && (
        <div className="mx-5 mb-5 rounded-xl border border-bronze/30 bg-bronze/5 p-4 space-y-2 text-xs">
          <p className="font-semibold text-foreground">
            How you could close the gap: {f.annualComplete ? "" : "at least "}≈{" "}
            {usd(row.gapPerYear)}/yr ({usd(f.gapDegreeUsd)} over {f.years} years
            {f.annualComplete ? "" : ", before living costs"})
          </p>
          <ul className="space-y-1.5 text-foreground">
            {toApply.slice(0, 2).map((s) => (
              <li key={s.name} className="flex items-start gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-primary shrink-0 mt-0.5" />
                <span>
                  Apply for <span className="font-semibold">{s.name}</span>
                  {s.basis === "competitive" ? " (competitive)" : ""} — {s.award}
                  {s.deadline
                    ? ` · deadline ${/^\d{4}-\d{2}-\d{2}/.test(s.deadline) ? fmtDate(s.deadline) : s.deadline}`
                    : ""}
                </span>
              </li>
            ))}
            {toApply.length === 0 && (
              <li className="flex items-start gap-1.5 text-muted-foreground">
                <Sparkles className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                No scholarship you're eligible for is in our data for this university — ask its
                financial aid office about external or government funding.
              </li>
            )}
            {a.alternatives[0] && (
              <li className="flex items-start gap-1.5">
                <ArrowRight className="w-3.5 h-3.5 text-primary shrink-0 mt-0.5" />
                <span>
                  Cheaper option for {a.programName.split(" (")[0]}:{" "}
                  <span className="font-semibold">
                    {a.alternatives[0].flag} {a.alternatives[0].name}
                  </span>{" "}
                  at ≈ {usd(a.alternatives[0].annualUsd)}/yr
                  {a.alternatives[0].complete
                    ? " all-in"
                    : " tuition only (living costs not published)"}
                  {a.alternatives[0].language ? ` (taught in ${a.alternatives[0].language})` : ""}.
                </span>
              </li>
            )}
          </ul>
        </div>
      )}

      {open && (
        <div className="px-5 pb-5 space-y-3 border-t border-border pt-4 text-xs">
          <p className="text-foreground">
            <span className="font-semibold">Grades: </span>
            {a.academic.headline}
          </p>
          {a.academic.requirement && (
            <p className="text-muted-foreground bg-secondary/40 rounded-lg p-2.5">
              <span className="font-semibold text-foreground">Published requirement: </span>
              {a.academic.requirement}
            </p>
          )}
          <p className="text-foreground">
            <span className="font-semibold">Next deadline: </span>
            {a.admissions.nextDeadline
              ? `${fmtDate(a.admissions.nextDeadline.date)} (${a.admissions.nextDeadline.label})`
              : a.admissions.pastDeadlines
                ? "This cycle has closed"
                : "Not published"}
          </p>
          {f.livingSource && <p className="text-muted-foreground">Living cost: {f.livingSource}</p>}
          {guaranteed.map((g) => (
            <p key={g.name} className="text-primary">
              <span className="font-semibold">Guaranteed: </span>
              {g.name} — {g.award}
            </p>
          ))}
        </div>
      )}

      <div className="px-5 pb-5 flex flex-wrap gap-2">
        <Link to="/analyze" search={{ uni: u.id }}>
          <Button
            size="sm"
            className="bg-primary hover:bg-primary/90 text-primary-foreground text-xs"
          >
            Full analysis <ArrowRight className="w-3 h-3" />
          </Button>
        </Link>
        <Button
          size="sm"
          variant="outline"
          className="border-border text-xs"
          onClick={() => onSave(u)}
          disabled={saved}
        >
          {saved ? (
            <>
              <Check className="w-3 h-3" /> Saved to my path
            </>
          ) : (
            <>
              <Save className="w-3 h-3" /> Save to my path
            </>
          )}
        </Button>
        <Button
          size="sm"
          variant="ghost"
          className="text-xs text-muted-foreground"
          onClick={() => setOpen(!open)}
        >
          {open ? "Less detail" : "More detail"}
        </Button>
      </div>
    </article>
  );
}
