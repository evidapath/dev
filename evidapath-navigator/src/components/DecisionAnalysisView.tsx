import {
  AlertTriangle,
  ArrowRight,
  BookOpen,
  CalendarClock,
  CheckCircle2,
  CircleHelp,
  DollarSign,
  ExternalLink,
  GraduationCap,
  Layers,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import type { ReactNode } from "react";
import type { DecisionAnalysis, Level, Lever } from "../lib/decision-engine";
import { fmtDate, usd } from "../lib/decision-engine";
import type { University } from "../lib/mock-data";

// Renders a computed DecisionAnalysis. Purely presentational: every figure comes
// from the engine, which only uses published data.

const LEVEL_STYLE: Record<Level, string> = {
  strong: "text-primary bg-primary/10 border-primary/20",
  edge: "text-bronze bg-bronze/10 border-bronze/25",
  gap: "text-destructive bg-destructive/10 border-destructive/20",
  unknown: "text-muted-foreground bg-secondary border-border",
};

function Badge({ level, children }: { level: Level; children: ReactNode }) {
  return (
    <span
      className={`text-[11px] font-medium px-2 py-0.5 rounded-full border whitespace-nowrap ${LEVEL_STYLE[level]}`}
    >
      {children}
    </span>
  );
}

function Card({
  n,
  icon,
  title,
  badge,
  children,
}: {
  n: number;
  icon: ReactNode;
  title: string;
  badge: ReactNode;
  children: ReactNode;
}) {
  return (
    <section className="p-5 rounded-xl border border-border bg-card flex flex-col gap-3 transition-shadow hover:shadow-sm">
      <div className="flex items-center justify-between gap-2">
        <span className="flex items-center gap-1.5 text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
          {icon}
          {n}. {title}
        </span>
        {badge}
      </div>
      {children}
    </section>
  );
}

function Row({ label, value, strong }: { label: string; value: ReactNode; strong?: boolean }) {
  return (
    <div className="flex justify-between gap-3 text-xs">
      <span className="text-muted-foreground">{label}</span>
      <span
        className={`font-mono text-right ${strong ? "font-bold text-foreground" : "text-foreground"}`}
      >
        {value}
      </span>
    </div>
  );
}

const LEVER_ICON: Record<Lever["kind"], ReactNode> = {
  deadline: <CalendarClock className="w-3.5 h-3.5" />,
  academic: <GraduationCap className="w-3.5 h-3.5" />,
  funding: <Sparkles className="w-3.5 h-3.5" />,
  budget: <DollarSign className="w-3.5 h-3.5" />,
  language: <BookOpen className="w-3.5 h-3.5" />,
  evidence: <CircleHelp className="w-3.5 h-3.5" />,
};

export function DecisionAnalysisView({
  u,
  a,
  compact = false,
}: {
  u: University;
  a: DecisionAnalysis;
  compact?: boolean;
}) {
  const f = a.financial;
  const fitLabel =
    f.fit === "within"
      ? "Within budget"
      : f.fit === "over"
        ? "Over budget"
        : "Cost not fully published";

  return (
    <div className="space-y-5">
      {/* Summary strip */}
      <div className="rounded-xl border border-border bg-secondary/40 p-4 flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div className="flex items-center gap-3 min-w-0">
          <span className="text-2xl">{u.flag}</span>
          <div className="min-w-0">
            <h4 className="font-display font-bold text-foreground text-base truncate">{u.name}</h4>
            <p className="text-xs text-muted-foreground">
              {u.city}, {u.country} • {a.programName}
              {a.taughtIn ? ` • taught in ${a.taughtIn}` : ""}
              {f.years ? ` • ${f.years} years` : ""}
            </p>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-3 sm:gap-5 bg-card rounded-lg border border-border px-3 py-2 text-center sm:text-right">
          <div>
            <span className="block text-[10px] uppercase font-semibold text-muted-foreground">
              Degree cost
            </span>
            <span className="font-mono font-bold text-sm text-foreground">{usd(f.degreeUsd)}</span>
          </div>
          <div>
            <span className="block text-[10px] uppercase font-semibold text-primary">
              Guaranteed aid
            </span>
            <span className="font-mono font-bold text-sm text-primary">
              {f.guaranteedAnnualUsd ? `−${usd(f.guaranteedAnnualUsd * f.years)}` : "$0"}
            </span>
          </div>
          <div>
            <span className="block text-[10px] uppercase font-semibold text-bronze">
              {f.gapDegreeUsd != null && f.gapDegreeUsd > 0 ? "Gap vs budget" : "Net cost"}
            </span>
            <span className="font-mono font-bold text-sm text-bronze">
              {f.gapDegreeUsd != null && f.gapDegreeUsd > 0
                ? usd(f.gapDegreeUsd)
                : usd(f.netDegreeUsd)}
            </span>
          </div>
        </div>
      </div>

      <div className={`grid grid-cols-1 md:grid-cols-2 ${compact ? "" : "xl:grid-cols-3"} gap-4`}>
        {/* 1 Academic */}
        <Card
          n={1}
          icon={<GraduationCap className="w-3.5 h-3.5" />}
          title="Academic readiness"
          badge={
            <Badge level={a.academic.level}>
              {
                {
                  strong: "Meets",
                  edge: "Borderline",
                  gap: "Below",
                  unknown: "No grade to compare",
                }[a.academic.level]
              }
            </Badge>
          }
        >
          <p className="text-sm font-medium text-foreground leading-snug">{a.academic.headline}</p>
          <div className="space-y-1.5 pt-2 border-t border-border/60">
            <Row label="Your band" value={a.academic.studentBand.replace(/^[^:]+:\s*/, "")} />
            {a.academic.curriculumLabel && (
              <Row label="Compared with" value={a.academic.curriculumLabel} />
            )}
          </div>
          {a.academic.requirement && (
            <p className="text-xs text-muted-foreground leading-relaxed bg-secondary/40 rounded-lg p-2.5">
              <span className="font-semibold text-foreground">Published: </span>
              {a.academic.requirement}
            </p>
          )}
        </Card>

        {/* 2 Admissions evidence */}
        <Card
          n={2}
          icon={<ShieldCheck className="w-3.5 h-3.5" />}
          title="Admissions evidence"
          badge={
            <Badge level={a.admissions.level}>
              {a.admissions.level === "strong"
                ? "Verified"
                : a.admissions.level === "edge"
                  ? "Published, verification in progress"
                  : "Thin evidence"}
            </Badge>
          }
        >
          <div className="space-y-1.5">
            <Row
              label="Curricula covered"
              value={
                a.admissions.published ? `${a.admissions.published}` : "Holistic / not published"
              }
            />
            <Row
              label="Next deadline"
              value={
                a.admissions.nextDeadline
                  ? `${fmtDate(a.admissions.nextDeadline.date)}`
                  : a.admissions.pastDeadlines
                    ? "This cycle closed"
                    : "Not published"
              }
            />
            {a.admissions.nextDeadline && (
              <Row label="Round" value={a.admissions.nextDeadline.label} />
            )}
          </div>
          <p className="text-[11px] text-bronze font-medium flex items-start gap-1.5 pt-2 border-t border-border/60">
            <AlertTriangle className="w-3 h-3 shrink-0 mt-0.5" />
            No admission "chance" is shown — published requirements and deadlines only.
          </p>
          {a.admissions.sourceUrl && (
            <a
              href={a.admissions.sourceUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[11px] text-primary inline-flex items-center gap-1 hover:underline"
            >
              Official source <ExternalLink className="w-3 h-3" />
            </a>
          )}
        </Card>

        {/* 3 Financial */}
        <Card
          n={3}
          icon={<DollarSign className="w-3.5 h-3.5" />}
          title="Financial fit"
          badge={<Badge level={f.level}>{fitLabel}</Badge>}
        >
          <div className="space-y-1.5">
            <Row
              label={f.annualComplete ? "Per year (all-in)" : "Per year (tuition, lower bound)"}
              value={`≈ ${usd(f.annualUsd)}`}
            />
            {f.localAnnual != null && f.currency && f.currency !== "USD" && (
              <Row label="Published" value={`${f.localAnnual.toLocaleString()} ${f.currency}`} />
            )}
            <Row label={`Degree (${f.years || "?"} yrs)`} value={usd(f.degreeUsd)} />
            {f.budgetDegreeUsd != null && (
              <Row label="Your budget over degree" value={usd(f.budgetDegreeUsd)} />
            )}
            {f.gapDegreeUsd != null && (
              <Row
                label={f.gapDegreeUsd > 0 ? "Shortfall" : "Headroom"}
                value={usd(Math.abs(f.gapDegreeUsd))}
                strong
              />
            )}
          </div>
          {f.livingSource && (
            <p className="text-[11px] text-muted-foreground">Living cost: {f.livingSource}</p>
          )}
        </Card>

        {/* 4 Funding */}
        <Card
          n={4}
          icon={<Sparkles className="w-3.5 h-3.5" />}
          title="Scholarships for you"
          badge={
            <Badge
              level={
                f.funding.some((x) => x.basis === "guaranteed" && x.eligible === "yes")
                  ? "strong"
                  : f.funding.length
                    ? "edge"
                    : "unknown"
              }
            >
              {f.funding.length ? `${f.funding.length} found` : "None in our data"}
            </Badge>
          }
        >
          {f.funding.length === 0 ? (
            <p className="text-xs text-muted-foreground">
              No institutional scholarship you're eligible for is in EvidaPath's verified data for
              this university yet.
            </p>
          ) : (
            <ul className="space-y-2">
              {f.funding.slice(0, compact ? 2 : 4).map((s) => (
                <li
                  key={s.name}
                  className="text-xs border-b border-border/50 last:border-0 pb-2 last:pb-0"
                >
                  <div className="flex items-start justify-between gap-2">
                    <a
                      href={s.source || undefined}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-semibold text-foreground hover:text-primary"
                    >
                      {s.name}
                    </a>
                    <span
                      className={`text-[10px] px-1.5 py-0.5 rounded border shrink-0 ${s.basis === "guaranteed" ? LEVEL_STYLE.strong : LEVEL_STYLE.unknown}`}
                    >
                      {s.basis === "guaranteed"
                        ? "Guaranteed"
                        : s.basis === "competitive"
                          ? "Competitive"
                          : "Check criteria"}
                    </span>
                  </div>
                  <p className="text-muted-foreground mt-0.5 line-clamp-2">{s.award}</p>
                  {s.eligible === "check" && (
                    <p className="text-bronze mt-0.5">Check your citizenship is eligible.</p>
                  )}
                </li>
              ))}
            </ul>
          )}
        </Card>

        {/* 5 Pathways */}
        <Card
          n={5}
          icon={<Layers className="w-3.5 h-3.5" />}
          title="Other options"
          badge={
            <Badge level={a.alternatives.length ? "strong" : "unknown"}>
              {a.alternatives.length} within reach
            </Badge>
          }
        >
          {!a.offersSubject && (
            <p className="text-xs text-bronze">
              This university doesn't list a matching programme — showing its closest one.
            </p>
          )}
          {a.alternatives.length === 0 ? (
            <p className="text-xs text-muted-foreground">
              No other university in our data offers this subject within your budget.
            </p>
          ) : (
            <ul className="space-y-1.5">
              {a.alternatives.map((alt) => (
                <li key={alt.id} className="flex justify-between gap-3 text-xs">
                  <span className="text-foreground truncate">
                    {alt.flag} {alt.name}
                    {alt.language && (
                      <span className="text-bronze"> · taught in {alt.language}</span>
                    )}
                  </span>
                  <span className="font-mono text-muted-foreground shrink-0">
                    ≈ {usd(alt.annualUsd)}/yr{alt.complete ? "" : " tuition"}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </Card>

        {/* 6 Levers */}
        <Card
          n={6}
          icon={<CheckCircle2 className="w-3.5 h-3.5" />}
          title="What you can do next"
          badge={
            <Badge level={a.levers.length ? "strong" : "unknown"}>
              {a.levers.length} {a.levers.length === 1 ? "action" : "actions"}
            </Badge>
          }
        >
          <ul className="space-y-2">
            {a.levers.slice(0, compact ? 3 : 6).map((l, i) => (
              <li
                key={i}
                className="flex items-start gap-2 text-xs text-foreground leading-relaxed"
              >
                <span className="text-primary mt-0.5 shrink-0">{LEVER_ICON[l.kind]}</span>
                <span>{l.text}</span>
              </li>
            ))}
          </ul>
        </Card>
      </div>
    </div>
  );
}

export function AnalysisFootnote() {
  return (
    <p className="text-[11px] text-muted-foreground flex items-start gap-1.5">
      <ArrowRight className="w-3 h-3 mt-0.5 shrink-0" />
      Costs are converted to USD at today's ECB reference rates. Guaranteed aid is only counted when
      the official source says every eligible student receives it.
    </p>
  );
}
