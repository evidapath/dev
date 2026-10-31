import { useState } from "react";
import { Link } from "@tanstack/react-router";
import {
  ArrowRight,
  Check,
  ChevronDown,
  Gem,
  Globe2,
  Save,
  Sparkles,
  Trophy,
  Wallet,
} from "lucide-react";
import type { PathwayGroup, PathwayResult, PathwayRow } from "../lib/pathways";
import { fmtDate } from "../lib/decision-engine";
import { money, TONE_CLASS, verdictFor, type Tone } from "../lib/verdict";
import type { University } from "../lib/mock-data";
import { CostBar } from "./CostBar";
import { Illustration } from "./Illustration";

// Find My Path results, built for a quick read: a top-3 strip, then compact
// cards (verdict + tags + cost bar). Everything else is behind "Why?".

const HEADLINE_TONE: Record<Tone, string> = {
  good: "text-primary",
  warn: "text-bronze",
  bad: "text-destructive",
  neutral: "text-foreground",
};

interface Ctx {
  budgetUsd: number;
  noLimit: boolean;
  regionLabel: string | null;
  savedIds: Set<string>;
  onSave: (u: University) => void;
}

// Top picks, the way a student would choose: stay in their country and in a
// language they can study in; only call something a "grade match" when the
// grades really meet the published requirement; with no budget limit, rank by
// academic fit instead of price.
function pickTop3(
  r: PathwayResult,
  noLimit: boolean,
): { label: string; icon: typeof Trophy; row: PathwayRow }[] {
  const { within, stretch, unpriced } = r.groups;
  const all = [...within, ...stretch, ...unpriced];
  const ok = (x: PathwayRow) => !x.a.taughtIn;
  const home = (x: PathwayRow) => x.inRegion && ok(x);
  const used = new Set<string>();
  const take = (label: string, icon: typeof Trophy, row: PathwayRow | undefined) => {
    if (!row || used.has(row.u.id)) return null;
    used.add(row.u.id);
    return { label, icon, row };
  };
  const free = (x: PathwayRow) => !used.has(x.u.id);
  const strong = (x: PathwayRow) => x.a.academic.level === "strong";
  const byDemand = (x: PathwayRow, y: PathwayRow) =>
    (y.a.academic.reqLevel ?? 0) - (x.a.academic.reqLevel ?? 0);
  const byNet = (x: PathwayRow, y: PathwayRow) =>
    (x.netAnnualUsd ?? Infinity) - (y.netAnnualUsd ?? Infinity);

  if (noLimit) {
    const matches = all.filter((x) => home(x) && strong(x)).sort(byDemand);
    // Holistic universities (no grade cut-off): those that meet full financial
    // need first, then fully priced, then cheapest.
    const fullNeed = (x: PathwayRow) =>
      x.a.financial.funding.some((f) =>
        /100% of demonstrated|full(?:y)? (?:demonstrated )?need/i.test(`${f.name} ${f.award}`),
      );
    const holistic = all
      .filter((x) => home(x) && x.a.academic.level === "unknown")
      .sort(
        (x, y) =>
          Number(fullNeed(y)) - Number(fullNeed(x)) ||
          Number(!x.a.financial.annualComplete) - Number(!y.a.financial.annualComplete) ||
          byNet(x, y),
      );
    if (matches.length) {
      const out = [take("Strongest match for your grades", Trophy, matches[0])];
      out.push(
        take("Also a strong match", Trophy, matches.filter(free)[0] ?? holistic.filter(free)[0]),
      );
      out.push(take("Best value among your matches", Gem, matches.filter(free).sort(byNet)[0]));
      return out.filter((x): x is NonNullable<typeof x> => !!x);
    }
    const out = [take("Top pick — holistic admissions", Trophy, holistic[0])];
    out.push(take("Also worth a look", Trophy, holistic.filter(free)[0]));
    out.push(take("Best value", Gem, holistic.filter(free).sort(byNet)[0]));
    return out.filter((x): x is NonNullable<typeof x> => !!x);
  }

  const affordable =
    within.filter(home).find((x) => !x.nearMiss) ??
    within.filter(home)[0] ??
    within.filter((x) => ok(x) && !x.inRegion)[0] ??
    unpriced.filter(home)[0];
  const out = [take("Best you can afford", Wallet, affordable)];
  const gradeMatch = all
    .filter((x) => home(x) && strong(x) && free(x))
    .sort((x, y) => (x.gapPerYear ?? 0) - (y.gapPerYear ?? 0) || byDemand(x, y))[0];
  out.push(
    gradeMatch
      ? take("Best match for your grades", Trophy, gradeMatch)
      : take("Closest option above budget", Trophy, stretch.filter((x) => home(x) && free(x))[0]),
  );
  const cheapest = [...within, ...unpriced]
    .filter((x) => home(x) && free(x) && x.netAnnualUsd != null)
    .sort(
      (x, y) =>
        Number(!x.a.financial.annualComplete) - Number(!y.a.financial.annualComplete) ||
        byNet(x, y),
    )[0];
  out.push(take("Lowest cost", Gem, cheapest));
  return out.filter((x): x is NonNullable<typeof x> => !!x);
}

export function PathwayResults({
  result,
  budgetUsd,
  noBudgetLimit,
  region,
  subject,
  savedIds,
  onSave,
  subjectCovered = true,
}: {
  result: PathwayResult;
  budgetUsd: number;
  noBudgetLimit: boolean;
  region: string;
  subject: string;
  savedIds: Set<string>;
  onSave: (u: University) => void;
  /** False when no university in EvidaPath offers this subject at all. */
  subjectCovered?: boolean;
}) {
  const { groups } = result;
  const total =
    groups.within.length + groups.stretch.length + groups.unpriced.length + groups.reach.length;
  const ctx: Ctx = {
    budgetUsd,
    noLimit: noBudgetLimit,
    regionLabel: result.regionLimited ? region : null,
    savedIds,
    onSave,
  };
  const top = pickTop3(result, noBudgetLimit);
  const where = result.regionLimited ? ` in ${region}` : "";

  if (total === 0)
    return (
      <div className="rounded-2xl border border-border bg-card p-8 text-center text-sm text-muted-foreground flex flex-col items-center gap-2">
        <Illustration name="search" />
        {subjectCovered ? (
          <p>
            Nothing for {subject || "that subject"}
            {where} yet. Try “Open to anywhere”, or{" "}
            <Link to="/universities" className="text-primary font-semibold">
              browse all universities
            </Link>
            .
          </p>
        ) : (
          <div className="space-y-3 max-w-md">
            <p className="text-base font-semibold text-foreground">
              We don't cover {subject || "that subject"} yet.
            </p>
            <p>
              EvidaPath currently covers{" "}
              <strong>Computer Science, Engineering, Business and Economics</strong> at 51
              universities. More subjects are coming.
            </p>
            <div className="flex flex-wrap justify-center gap-2">
              <a
                href="#counseling"
                className="inline-flex items-center h-9 px-4 rounded-lg bg-primary text-primary-foreground text-sm font-semibold hover:bg-primary/90"
              >
                Tell us you want {subject || "it"}
              </a>
              <Link
                to="/universities"
                className="inline-flex items-center h-9 px-4 rounded-lg border border-border text-sm font-semibold text-foreground hover:bg-secondary"
              >
                Browse what we cover
              </Link>
            </div>
          </div>
        )}
      </div>
    );

  return (
    <div className="space-y-8">
      {/* The deal, in one line */}
      <p className="text-base font-semibold text-foreground">
        {noBudgetLimit
          ? `${total} options${where} — ranked by how well your grades match.`
          : result.withinInRegion > 0
            ? `${result.withinInRegion} fit${result.withinInRegion === 1 ? "s" : ""} your budget${where}.`
            : `Nothing${where} fits ${money(budgetUsd)}/yr on published costs.`}{" "}
        <span className="font-normal text-muted-foreground">
          {groups.stretch.length > 0 && `${groups.stretch.length} more cost a bit more. `}
          {result.withinElsewhere > 0 && `${result.withinElsewhere} cheaper options elsewhere.`}
        </span>
      </p>

      {top.length > 0 && (
        <section aria-labelledby="top3" className="space-y-3">
          <h2 id="top3" className="font-display font-bold text-xl text-foreground">
            Your top {top.length}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {top.map(({ label, icon: Icon, row }) => (
              <TopCard key={row.u.id} label={label} Icon={Icon} row={row} ctx={ctx} />
            ))}
          </div>
        </section>
      )}

      <Group
        id="within"
        title={noBudgetLimit ? "Fully priced" : "Fits your budget"}
        note="After any guaranteed scholarship. English-taught first."
        rows={groups.within}
        ctx={ctx}
        empty={`Nothing fits ${money(budgetUsd)}/yr once living costs are included.`}
      />
      <Group
        id="stretch"
        title={`A bit over budget${where}`}
        note="Smallest gap first — tap “Why?” to see how to close it."
        rows={groups.stretch}
        ctx={{ ...ctx, regionLabel: null }}
      />
      <Group
        id="unpriced"
        title="Tuition fits — living cost unknown"
        note="Budget a margin before relying on these."
        rows={groups.unpriced}
        ctx={ctx}
      />
      <Group
        id="reach"
        title={`Reach options${where}`}
        note="Big gap or grades below. Good to know, not to plan around."
        rows={groups.reach}
        ctx={{ ...ctx, regionLabel: null }}
        collapsed
      />

      <p className="text-[11px] text-muted-foreground">
        USD at European Central Bank rates. No admission chances — only published data.
      </p>
    </div>
  );
}

function TopCard({
  label,
  Icon,
  row,
  ctx,
}: {
  label: string;
  Icon: typeof Trophy;
  row: PathwayRow;
  ctx: Ctx;
}) {
  const v = verdictFor(row.a, ctx.budgetUsd, ctx.noLimit);
  const f = row.a.financial;
  return (
    <Link
      to="/analyze"
      search={{ uni: row.u.id }}
      className="group rounded-2xl border border-border bg-card p-4 space-y-3 hover:border-primary/50 hover:shadow-sm transition-all"
    >
      <p className="text-[11px] font-bold uppercase tracking-wider text-primary flex items-center gap-1.5">
        <Icon className="w-3.5 h-3.5" /> {label}
      </p>
      <div>
        <p className="font-display font-bold text-foreground leading-snug">
          {row.u.flag} {row.u.name}
        </p>
        <p className={`text-sm font-medium ${HEADLINE_TONE[v.tone]}`}>{v.headline}</p>
      </div>
      <CostBar
        cost={f.annualUsd}
        aid={f.guaranteedAnnualUsd}
        budget={ctx.budgetUsd}
        complete={f.annualComplete}
        noLimit={ctx.noLimit}
        compact
      />
      <p className="text-xs text-muted-foreground flex items-center justify-between">
        <span className="font-mono text-foreground">
          {money(row.netAnnualUsd)}/yr{f.annualComplete ? "" : " tuition"}
        </span>
        <span className="text-primary font-semibold inline-flex items-center gap-1 group-hover:gap-1.5 transition-all">
          See analysis <ArrowRight className="w-3 h-3" />
        </span>
      </p>
    </Link>
  );
}

function Group({
  id,
  title,
  note,
  rows,
  ctx,
  empty,
  collapsed = false,
}: {
  id: PathwayGroup;
  title: string;
  note: string;
  rows: PathwayRow[];
  ctx: Ctx;
  empty?: string;
  collapsed?: boolean;
}) {
  const [open, setOpen] = useState(!collapsed);
  const [showAll, setShowAll] = useState(false);
  if (rows.length === 0 && !empty) return null;
  const shown = showAll ? rows : rows.slice(0, 5);
  return (
    <section className="space-y-3" aria-labelledby={`g-${id}`}>
      <button
        onClick={() => setOpen(!open)}
        aria-expanded={open}
        className="w-full text-left flex items-end justify-between gap-3"
      >
        <span>
          <h2 id={`g-${id}`} className="font-display font-bold text-lg text-foreground">
            {title} <span className="text-muted-foreground font-normal">({rows.length})</span>
          </h2>
          <span className="text-xs text-muted-foreground">{note}</span>
        </span>
        <ChevronDown
          className={`w-4 h-4 text-muted-foreground mb-1 shrink-0 transition-transform ${open ? "rotate-180" : ""}`}
        />
      </button>
      {open &&
        (rows.length === 0 ? (
          <p className="text-sm text-muted-foreground rounded-xl border border-dashed border-border p-4">
            {empty}
          </p>
        ) : (
          <div className="space-y-2">
            {shown.map((r) => (
              <CompactCard key={r.u.id} row={r} ctx={ctx} />
            ))}
            {rows.length > shown.length && (
              <button
                onClick={() => setShowAll(true)}
                className="text-sm font-semibold text-primary hover:underline pt-1"
              >
                Show {rows.length - shown.length} more
              </button>
            )}
          </div>
        ))}
    </section>
  );
}

function CompactCard({ row, ctx }: { row: PathwayRow; ctx: Ctx }) {
  const { u, a } = row;
  const [why, setWhy] = useState(false);
  const v = verdictFor(a, ctx.budgetUsd, ctx.noLimit);
  const f = a.financial;
  const saved = ctx.savedIds.has(u.id);
  const toApply = f.funding.filter((x) => x.basis !== "guaranteed");
  const guaranteed = f.funding.filter((x) => x.basis === "guaranteed" && x.eligible === "yes");
  const outside = ctx.regionLabel && !row.inRegion;
  const bar = (compact: boolean) => (
    <CostBar
      cost={f.annualUsd}
      aid={f.guaranteedAnnualUsd}
      budget={ctx.budgetUsd}
      complete={f.annualComplete}
      noLimit={ctx.noLimit}
      compact={compact}
    />
  );

  return (
    <article className="rounded-xl border border-border bg-card p-4 space-y-3 hover:border-primary/40 transition-colors">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="font-display font-bold text-[15px] text-foreground leading-snug">
            {u.flag} {u.name}
          </h3>
          <p className="text-xs text-muted-foreground">
            {u.city} · {a.programName.split(" (")[0]}
            {f.years ? ` · ${f.years} yrs` : ""}
            {outside && (
              <span className="ml-1.5 inline-flex items-center gap-0.5 text-bronze font-medium">
                <Globe2 className="w-3 h-3" /> outside {ctx.regionLabel}
              </span>
            )}
          </p>
        </div>
        <div className="text-right shrink-0">
          <p className="font-mono font-bold text-foreground">{money(row.netAnnualUsd)}</p>
          <p className="text-[10px] text-muted-foreground">
            {f.annualComplete ? "per year, all-in" : "tuition / yr"}
          </p>
        </div>
      </div>

      <p className={`text-sm font-semibold ${HEADLINE_TONE[v.tone]}`}>{v.headline}</p>
      <div className="flex flex-wrap gap-1.5">
        {v.tags.map((t) => (
          <span
            key={t.text}
            className={`text-[11px] font-medium px-2 py-0.5 rounded-full border ${TONE_CLASS[t.tone]}`}
          >
            {t.text}
          </span>
        ))}
      </div>
      {bar(true)}

      <div className="flex flex-wrap items-center gap-2 pt-1">
        <button
          onClick={() => setWhy(!why)}
          aria-expanded={why}
          className="inline-flex items-center gap-1 h-8 px-3 rounded-lg border border-border text-xs font-semibold text-foreground hover:bg-secondary"
        >
          Why? <ChevronDown className={`w-3 h-3 transition-transform ${why ? "rotate-180" : ""}`} />
        </button>
        <button
          onClick={() => ctx.onSave(u)}
          disabled={saved}
          className="inline-flex items-center gap-1 h-8 px-3 rounded-lg border border-border text-xs font-semibold text-foreground hover:bg-secondary disabled:opacity-60"
        >
          {saved ? <Check className="w-3 h-3" /> : <Save className="w-3 h-3" />}
          {saved ? "Saved" : "Save"}
        </button>
        <Link
          to="/analyze"
          search={{ uni: u.id }}
          className="inline-flex items-center gap-1 h-8 px-3 rounded-lg text-xs font-semibold text-primary hover:bg-primary/10"
        >
          Full analysis <ArrowRight className="w-3 h-3" />
        </Link>
      </div>

      {why && (
        <div className="rounded-lg bg-secondary/40 p-3 space-y-2 text-xs text-foreground motion-safe:animate-in motion-safe:fade-in duration-200">
          {bar(false)}
          <p>
            <span className="font-semibold">Grades: </span>
            {a.academic.headline}
          </p>
          {a.academic.requirement && (
            <p className="text-muted-foreground">“{a.academic.requirement}”</p>
          )}
          {guaranteed.map((g) => (
            <p key={g.name} className="text-primary">
              <span className="font-semibold">Guaranteed: </span>
              {g.name}
            </p>
          ))}
          {row.group === "stretch" && (
            <div className="space-y-1">
              <p className="font-semibold">Ways to close the gap</p>
              {toApply.slice(0, 2).map((s) => (
                <p key={s.name} className="flex gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-primary shrink-0 mt-0.5" />
                  <span>
                    {s.name} — {s.award}
                    {s.deadline && /^\d{4}-\d{2}-\d{2}/.test(s.deadline)
                      ? ` (by ${fmtDate(s.deadline)})`
                      : ""}
                  </span>
                </p>
              ))}
              {toApply.length === 0 && (
                <p className="text-muted-foreground">
                  No scholarship you qualify for in our data — ask the university's aid office.
                </p>
              )}
              {a.alternatives[0] && (
                <p className="flex gap-1.5">
                  <ArrowRight className="w-3.5 h-3.5 text-primary shrink-0 mt-0.5" />
                  <span>
                    Cheaper: {a.alternatives[0].flag} {a.alternatives[0].name},{" "}
                    {money(a.alternatives[0].annualUsd)}/yr
                    {a.alternatives[0].complete ? "" : " tuition"}
                  </span>
                </p>
              )}
            </div>
          )}
          <p>
            <span className="font-semibold">Next deadline: </span>
            {a.admissions.nextDeadline
              ? `${fmtDate(a.admissions.nextDeadline.date)} (${a.admissions.nextDeadline.label})`
              : a.admissions.pastDeadlines
                ? "closed this cycle"
                : "not published"}
          </p>
          {f.livingSource && <p className="text-muted-foreground">Living cost: {f.livingSource}</p>}
        </div>
      )}
    </article>
  );
}
