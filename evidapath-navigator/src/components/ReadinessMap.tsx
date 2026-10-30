import { useMemo } from "react";
import { analyze, usd, type StudentInput } from "../lib/decision-engine";
import type { LiveData } from "../lib/use-live-data";

// Live "readiness map": one sample student run through the decision engine
// against every university offering their subject. Real data, fictional student.

const SAMPLE_STUDENT: StudentInput = {
  curriculum: "IB Diploma",
  gradeBand: "Competitive: IB 34-36 / AAA-AAB / GPA 3.6-3.7",
  subject: "Computer Science",
  budgetUsd: 50000,
  citizenship: "UAE",
};

export function ReadinessMap({ data }: { data: LiveData | null }) {
  const stats = useMemo(() => {
    if (!data) return null;
    const runs = data.universities
      .map((u) => analyze(u, SAMPLE_STUDENT, data.scholarships, [], data.fx))
      .filter((a) => a.offersSubject);
    const nets = runs
      .filter((a) => a.financial.fit === "within" && a.financial.netDegreeUsd != null)
      .map((a) => a.financial.netDegreeUsd!)
      .sort((a, b) => a - b);
    const median = nets.length ? nets[Math.floor(nets.length / 2)]! : null;
    return {
      total: runs.length,
      meets: runs.filter((a) => a.academic.level === "strong").length,
      edge: runs.filter((a) => a.academic.level === "edge" || a.academic.level === "gap").length,
      noGrade: runs.filter((a) => a.academic.level === "unknown").length,
      subjects: runs.filter((a) => a.academic.subjects.length > 0).length,
      within: runs.filter((a) => a.financial.fit === "within").length,
      guaranteed: runs.filter((a) => a.financial.guaranteedAnnualUsd > 0).length,
      median,
    };
  }, [data]);

  const row = (label: string, value: string) => (
    <div className="flex justify-between gap-3">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-mono font-semibold text-foreground">{value}</span>
    </div>
  );

  return (
    <div className="w-full lg:w-96 bg-card rounded-2xl border border-border p-5 shadow-sm space-y-3.5">
      <div className="flex items-center justify-between border-b border-border pb-3 gap-2">
        <span className="text-xs font-semibold text-foreground">Live readiness map</span>
        <span className="text-[10px] bg-primary/10 text-primary px-2 py-0.5 rounded font-mono">
          Verified data
        </span>
      </div>
      <p className="text-[11px] text-muted-foreground">
        Sample student: Emirati, IB 34–36, Computer Science, $50k/yr.
      </p>
      {!stats ? (
        <div className="space-y-2" aria-busy="true">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-4 rounded bg-secondary/70 animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="space-y-2 text-xs">
          {row("Universities offering CS", String(stats.total))}
          {row("Grades meet published requirement", String(stats.meets))}
          {row("Borderline or below", String(stats.edge))}
          {row("Holistic / no comparable grade", String(stats.noGrade))}
          {row("Prerequisite subjects to check", String(stats.subjects))}
          {row("Within budget (all-in)", String(stats.within))}
          {row("With guaranteed aid", String(stats.guaranteed))}
          {row("Median net degree cost (in budget)", usd(stats.median))}
        </div>
      )}
      <div className="pt-2 border-t border-border text-[11px] text-muted-foreground">
        Computed live from EvidaPath's verified university and scholarship data.
      </div>
    </div>
  );
}
