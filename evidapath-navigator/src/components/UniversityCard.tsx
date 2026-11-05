import { Link } from "@tanstack/react-router";
import { useRef, useState } from "react";
import {
  GraduationCap,
  ShieldCheck,
  MapPin,
  ArrowRight,
  ExternalLink,
  Info,
  ClipboardCheck,
} from "lucide-react";
import { otherTests } from "../lib/tests";
import { Button } from "./ui/button";
import type { University } from "../lib/mock-data";
import { formatCost, NOT_PUBLISHED } from "../lib/format";
import { AdmissionsPanel } from "./AdmissionsPanel";
import { CardScholarships } from "./CardScholarships";

// Skeleton placeholder shown while verified data loads — keeps the grid layout
// stable (no pop-in / layout shift) and signals progress with a gentle pulse.
/** A big cost figure; a missing one reads as a quiet "Not published", never as a number. */
function CostTile({
  label,
  value,
  currency,
}: {
  label: string;
  value: number | null;
  currency: string;
}) {
  return (
    <div className="rounded-xl bg-secondary/60 px-3 py-2.5">
      <p className="text-[11px] text-muted-foreground">{label}</p>
      {value == null ? (
        <p className="text-sm font-medium text-muted-foreground leading-tight mt-1">
          {NOT_PUBLISHED}
        </p>
      ) : (
        <p className="font-display font-bold text-lg text-foreground tabular-nums leading-tight mt-0.5">
          {formatCost(value, currency)}
        </p>
      )}
    </div>
  );
}

export function UniversityCardSkeleton({ index = 0 }: { index?: number }) {
  return (
    <div
      className="rounded-2xl border border-border bg-card p-6 space-y-6 motion-safe:animate-in motion-safe:fade-in fill-mode-both"
      style={{ animationDelay: `${Math.min(index, 8) * 60}ms`, animationDuration: "400ms" }}
      aria-hidden="true"
    >
      <div className="animate-pulse space-y-6">
        <div className="flex items-center justify-between">
          <div className="h-8 w-8 rounded-full bg-muted" />
          <div className="h-5 w-24 rounded bg-muted" />
        </div>
        <div className="space-y-2">
          <div className="h-5 w-3/4 rounded bg-muted" />
          <div className="h-3 w-1/2 rounded bg-muted" />
        </div>
        <div className="h-9 w-full rounded-lg bg-muted" />
        <div className="space-y-2.5">
          <div className="h-3 w-full rounded bg-muted" />
          <div className="h-3 w-5/6 rounded bg-muted" />
          <div className="h-3 w-2/3 rounded bg-muted" />
        </div>
        <div className="flex gap-2 pt-2">
          <div className="h-9 w-28 rounded-lg bg-muted" />
          <div className="h-9 w-28 rounded-lg bg-muted" />
        </div>
      </div>
    </div>
  );
}

// "2026-10-21" → "Oct 2026"; anything else is shown as written.
function monthYear(date: string): string {
  if (!/^\d{4}-\d{2}-\d{2}/.test(date)) return date;
  return new Date(`${date.slice(0, 10)}T00:00:00Z`).toLocaleDateString("en-GB", {
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  });
}

// Header tint per country (an oklch hue), so neighbouring cards read apart.
const COUNTRY_HUE: Record<string, number> = {
  "United Kingdom": 255,
  "United States": 25,
  Canada: 15,
  Germany: 85,
  Netherlands: 50,
  "United Arab Emirates": 155,
  Australia: 200,
  Malaysia: 300,
  Switzerland: 0,
  France: 270,
  Ireland: 140,
  Singapore: 340,
};
function countryHue(country: string): number {
  return COUNTRY_HUE[country] ?? 230;
}

// One university card. When the university has multiple programs (programDetails),
// shows a program selector so the student sees THAT program's own cost + admissions
// (Suhail: program-specific, not university-wide). Falls back to the flat fields for
// single-program universities.
export function UniversityCard({ univ, index = 0 }: { univ: University; index?: number }) {
  const details = univ.programDetails;
  const [sel, setSel] = useState(0);
  const pv = details?.[sel];

  // Displayed values: the selected program view when present, else the flat fields.
  const costs = pv?.costs ?? univ.costs;
  const durationYears = pv?.durationYears ?? univ.durationYears;
  const residencyNote = pv?.costResidencyNote ?? univ.costResidencyNote;
  const admissions = pv?.admissionsByCurriculum ?? univ.admissionsByCurriculum;
  const [admOpen, setAdmOpen] = useState(false);
  const admRef = useRef<HTMLDetailsElement>(null);

  const verified = univ.evidenceConfidence.startsWith("Verified");
  const affordability = univ.affordabilityIndex.category;

  return (
    <div
      className="group rounded-2xl border border-border bg-card shadow-sm overflow-hidden flex flex-col justify-between transition-all duration-200 ease-out hover:border-primary/30 hover:shadow-lg hover:-translate-y-1 motion-safe:animate-in motion-safe:fade-in motion-safe:slide-in-from-bottom-3 fill-mode-both"
      style={{ animationDelay: `${Math.min(index, 8) * 60}ms`, animationDuration: "450ms" }}
    >
      {/* Header band, tinted by country so the grid isn't one white sheet */}
      <div
        className="uni-band px-6 pt-5 pb-4 border-b border-border/60"
        style={{ ["--band-h" as string]: countryHue(univ.country) }}
      >
        <div className="flex items-start justify-between gap-3">
          <span className="text-4xl leading-none drop-shadow-sm">{univ.flag}</span>
          <span className="text-[11px] font-semibold bg-card/80 backdrop-blur px-2.5 py-1 rounded-full text-foreground border border-border/60">
            {durationYears > 0 ? `${durationYears}-year degree` : "Duration pending"}
          </span>
        </div>
        <h3 className="font-display font-bold text-xl text-foreground mt-3 leading-tight">
          {univ.name}
        </h3>
        <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
          <MapPin className="w-3 h-3" />
          {univ.city}, {univ.country}
        </p>
      </div>

      <div className="px-6 pt-4 pb-5 space-y-4 flex-1">
        {/* Program selector (only when the university has more than one program) */}
        {details && details.length > 1 && (
          <div>
            <label className="block text-[11px] font-medium text-muted-foreground mb-1">
              Program
            </label>
            <select
              value={sel}
              onChange={(e) => setSel(Number(e.target.value))}
              className="w-full h-9 px-2 rounded-lg border border-input bg-background text-xs text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
            >
              {details.map((p, i) => (
                <option key={i} value={i}>
                  {p.name}
                  {p.degree ? ` (${p.degree})` : ""}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* The two numbers a family asks first, big */}
        <div className="grid grid-cols-2 gap-2">
          <CostTile label="Tuition / year" value={costs.tuitionPerYear} currency={costs.currency} />
          <CostTile
            label="Living / year (est.)"
            value={costs.livingPerYear}
            currency={costs.currency}
          />
        </div>
        <div className="space-y-1 text-sm">
          {costs.mandatoryFees ? (
            <div className="flex items-baseline justify-between gap-3 text-xs">
              <span className="text-muted-foreground">Compulsory fees / year</span>
              <span className="font-medium text-foreground tabular-nums">
                {formatCost(costs.mandatoryFees, costs.currency)}
              </span>
            </div>
          ) : null}
          <div className="flex items-baseline justify-between gap-3">
            <span className="text-muted-foreground">Whole degree</span>
            <span className="font-display font-bold text-foreground tabular-nums">
              {formatCost(costs.totalDegree, costs.currency)}
            </span>
          </div>
          {costs.totalIncludes && (
            <p className="text-[11px] text-muted-foreground text-right -mt-0.5">
              {costs.totalIncludes}
              {costs.livingPerYear == null ? " (living cost not included)" : ""}
            </p>
          )}
        </div>
        {/* Scholarships near the top, with who can apply and deadlines */}
        <CardScholarships uniId={univ.id} />

        {/* Tests this programme asks for */}
        {(pv?.english ||
          otherTests(pv ?? { admissionsByCurriculum: admissions ?? [] }).length > 0) && (
          <div className="rounded-lg border border-border px-3 py-2 text-[11px] space-y-1">
            <p className="font-semibold text-foreground flex items-center gap-1.5">
              <ClipboardCheck className="w-3.5 h-3.5 text-primary" /> Tests required
            </p>
            {pv?.english && (
              <p className="text-muted-foreground line-clamp-2">
                <span className="font-medium text-foreground">English:</span> {pv.english}
              </p>
            )}
            {otherTests(pv ?? { admissionsByCurriculum: admissions ?? [] }).length > 0 && (
              <p className="text-muted-foreground">
                <span className="font-medium text-foreground">Other:</span>{" "}
                {otherTests(pv ?? { admissionsByCurriculum: admissions ?? [] }).join(" · ")}
              </p>
            )}
          </div>
        )}

        {(costs.livingSource || residencyNote) && (
          <div className="rounded-lg bg-secondary/50 px-3 py-2 space-y-1 text-[11px] leading-snug text-muted-foreground">
            {costs.livingSource && (
              <p className="flex gap-1.5">
                <Info className="w-3 h-3 mt-0.5 shrink-0" aria-hidden />
                <span>Living cost: {costs.livingSource}</span>
              </p>
            )}
            {residencyNote && (
              <p className="flex gap-1.5">
                <Info className="w-3 h-3 mt-0.5 shrink-0" aria-hidden />
                <span>{residencyNote}</span>
              </p>
            )}
          </div>
        )}

        {/* Entry requirements + evidence, as chips */}
        <div className="flex flex-wrap items-center gap-1.5 text-[11px]">
          {admissions?.length ? (
            <button
              type="button"
              onClick={() => {
                setAdmOpen(true);
                requestAnimationFrame(() =>
                  admRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" }),
                );
              }}
              className="inline-flex items-center gap-1 rounded-full bg-accent text-accent-foreground font-semibold px-2.5 py-1 hover:bg-primary/15"
            >
              <GraduationCap className="w-3 h-3" />
              Entry grades ↓
            </button>
          ) : (
            <span className="rounded-full bg-secondary text-muted-foreground px-2.5 py-1 line-clamp-1">
              {univ.academicRequirements.target}
            </span>
          )}
          <span
            className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 font-medium ${
              verified
                ? "bg-primary/10 text-primary border border-primary/25 font-semibold"
                : "bg-bronze/10 text-bronze"
            }`}
            title={`Last checked: ${univ.lastVerified}`}
          >
            <ShieldCheck className="w-3 h-3" />
            {!verified
              ? univ.evidenceConfidence
              : /^\d{4}-/.test(univ.lastVerified)
                ? `Checked ${monthYear(univ.lastVerified)}`
                : "Being checked"}
          </span>
          {/^https?:/.test(univ.officialSourceUrl) && (
            <a
              href={univ.officialSourceUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 rounded-full border border-border px-2.5 py-1 font-medium text-foreground hover:border-primary/40"
            >
              Official site <ExternalLink className="w-3 h-3" />
            </a>
          )}
          {costs.notChecked && (
            <span className="rounded-full bg-bronze/10 text-bronze px-2.5 py-1 font-medium">
              Costs not re-checked yet
            </span>
          )}
          {!affordability.startsWith("Pending") && (
            <span className="rounded-full bg-secondary text-foreground px-2.5 py-1 font-medium">
              {affordability}
            </span>
          )}
        </div>

        {/* Verified admissions + deadlines (surfaced from Sanity) */}
        {(univ.deadlines?.length || admissions?.length) && (
          <details
            ref={admRef}
            open={admOpen}
            onToggle={(e) => setAdmOpen(e.currentTarget.open)}
            className="text-xs border-t border-border/60 pt-2"
          >
            <summary className="cursor-pointer text-primary font-semibold select-none">
              Admissions & deadlines
            </summary>
            <AdmissionsPanel deadlines={univ.deadlines} admissions={admissions} />
          </details>
        )}
      </div>

      <div className="px-6 pb-5">
        <Link to="/find-my-path" className="block">
          <Button className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-semibold rounded-xl">
            Would this work for me? →
          </Button>
        </Link>
      </div>
    </div>
  );
}
