import { createFileRoute, Link } from "@tanstack/react-router";
import { requireAuth } from "../lib/route-guard";
import { useEffect, useState } from "react";
import { useServerFn } from "@tanstack/react-start";
import { PiggyBank, Scale } from "lucide-react";
import { Button } from "../components/ui/button";
import { getUniversities } from "../lib/universities.functions";
import { getFxRates, toUsd, type FxRates } from "../lib/fx.functions";
import type { University } from "../lib/mock-data";
import { isPending } from "../lib/format";
import { VerifiedAwardsPanel } from "../components/offer-vault/VerifiedAwardsPanel";
import { canonicalLink, ogUrlMeta } from "../lib/seo";

function money(value: number | null): string {
  if (isPending(value)) return "Pending verified data";
  return `$${Math.round(value!).toLocaleString()}`;
}

export const Route = createFileRoute("/fund")({
  head: () => ({
    meta: [
      { title: "Family Education Capital Plan — EvidaPath" },
      {
        name: "description",
        content:
          "Turn an acceptance goal into a four-year financial plan. Compare multi-year education pathways, scholarships, and family funding gaps.",
      },
      { property: "og:title", content: "Family Education Capital Plan — EvidaPath" },
      {
        property: "og:description",
        content:
          "Model multi-year tuition, living costs, identified aid, and family capital commitments.",
      },
      ogUrlMeta("/fund"),
    ],
    links: [canonicalLink("/fund")],
  }),
  beforeLoad: ({ context, location }) => requireAuth(context, location.pathname),
  component: FundPage,
});

// One pathway's plan, entirely in USD so it can be compared with the (USD) family
// capacity and scholarship sliders. Null figures mean the cost isn't verified yet.
interface PathwayPlan {
  u: University;
  tuitionFees: number | null;
  living: number | null;
  degreeTotal: number | null;
  scholarship: number;
  family: number;
  gap: number | null;
}

function buildPlan(
  u: University,
  fx: FxRates | null,
  familyPerYear: number,
  scholarshipPerYear: number,
): PathwayPlan {
  const usd = (v: number | null) => (v == null ? null : toUsd(v, u.costs.currency || "", fx));
  const tuition = usd(u.costs.tuitionPerYear);
  const fees = usd(u.costs.mandatoryFees);
  const annualTotal = usd(u.costs.totalAnnual);
  const years = u.durationYears || 0;
  const degreeTotal = annualTotal != null && years > 0 ? annualTotal * years : null;
  // A scholarship can't cover more than the annual cost.
  const perYear =
    annualTotal != null ? Math.min(scholarshipPerYear, annualTotal) : scholarshipPerYear;
  const scholarship = perYear * years;
  const family = familyPerYear * years;
  return {
    u,
    tuitionFees: tuition == null ? null : tuition + (fees ?? 0),
    living: usd(u.costs.livingPerYear),
    degreeTotal,
    scholarship,
    family,
    gap: degreeTotal != null ? Math.max(0, degreeTotal - scholarship - family) : null,
  };
}

function FundPage() {
  const [universities, setUniversities] = useState<University[]>([]);
  const [fx, setFx] = useState<FxRates | null>(null);
  const [selectedUniv1, setSelectedUniv1] = useState("");
  const [selectedUniv2, setSelectedUniv2] = useState("");
  const [expectedFamilyContribution, setExpectedFamilyContribution] = useState(35000); // per year
  const [appliedScholarship, setAppliedScholarship] = useState(15000); // per year

  const fetchUniversities = useServerFn(getUniversities);
  const fetchFx = useServerFn(getFxRates);
  useEffect(() => {
    let active = true;
    fetchUniversities().then((res) => {
      if (!active) return;
      const sorted = [...res.universities].sort((a, b) => a.name.localeCompare(b.name));
      setUniversities(sorted);
      // Default to the first two universities with a verified full annual cost.
      const priced = sorted.filter((u) => u.costs.totalAnnual != null);
      setSelectedUniv1((v) => v || priced[0]?.id || sorted[0]?.id || "");
      setSelectedUniv2((v) => v || priced[1]?.id || sorted[1]?.id || "");
    });
    fetchFx()
      .then((r) => active && setFx(r))
      .catch(() => {});
    return () => {
      active = false;
    };
  }, [fetchUniversities, fetchFx]);

  const u1 = universities.find((u) => u.id === selectedUniv1);
  const u2 = universities.find((u) => u.id === selectedUniv2);
  const plan1 = u1 ? buildPlan(u1, fx, expectedFamilyContribution, appliedScholarship) : null;
  const plan2 = u2 ? buildPlan(u2, fx, expectedFamilyContribution, appliedScholarship) : null;
  const t1 = plan1?.degreeTotal ?? null;
  const t2 = plan2?.degreeTotal ?? null;
  const cheaper =
    plan1 && plan2 && t1 != null && t2 != null && t1 !== t2
      ? t1 < t2
        ? { pick: plan1, other: plan2, saves: t2 - t1 }
        : { pick: plan2, other: plan1, saves: t1 - t2 }
      : null;

  const selectCls =
    "w-full h-10 px-3 rounded-lg border border-input bg-background text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary";
  const uniOptions = universities.map((u) => (
    <option key={u.id} value={u.id}>
      {u.flag} {u.name} ({u.durationYears} yrs)
    </option>
  ));

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      {/* Header */}
      <div className="max-w-3xl space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-bronze/10 text-bronze text-xs font-semibold">
          <PiggyBank className="w-3.5 h-3.5" />
          <span>Decision Suite • Fund</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-display font-extrabold text-foreground">
          Family Education Capital Plan
        </h1>
        <p className="text-sm sm:text-base text-muted-foreground leading-relaxed">
          Turn an acceptance goal into a multi-year financial roadmap. Compare two universities side
          by side against what your family can contribute and the funding you expect.
        </p>
        <div className="flex items-center gap-2 text-[11px] text-muted-foreground bg-secondary/50 border border-border rounded-lg px-3 py-2">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-bronze" />
          <span>
            University costs are live EvidaPath data traced to official sources, converted to USD
            {fx ? ` at European Central Bank reference rates from ${fx.date}` : ""}. Family capacity
            and scholarship amounts are your own assumptions. Universities without a verified full
            annual cost show "Pending verified data".
          </span>
        </div>
      </div>

      {/* Assumptions & Controller Box */}
      <div className="bg-card border border-border rounded-2xl p-6 shadow-xs space-y-6">
        <div className="border-b border-border pb-3">
          <h2 className="font-display font-bold text-base text-foreground">
            Capital Assumptions & Household Parameters
          </h2>
          <p className="text-xs text-muted-foreground">
            Model family contributions and potential scholarships across candidate pathways.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div>
            <label className="block text-xs font-semibold uppercase text-muted-foreground mb-1.5">
              Pathway A (Primary Target)
            </label>
            <select
              value={selectedUniv1}
              onChange={(e) => setSelectedUniv1(e.target.value)}
              className={selectCls}
            >
              {uniOptions}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase text-muted-foreground mb-1.5">
              Pathway B (Comparison / Strategic Pivot)
            </label>
            <select
              value={selectedUniv2}
              onChange={(e) => setSelectedUniv2(e.target.value)}
              className={selectCls}
            >
              {uniOptions}
            </select>
          </div>

          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="text-xs font-semibold uppercase text-muted-foreground">
                Family Annual Capacity
              </label>
              <span className="font-mono text-xs font-bold text-foreground">
                ${expectedFamilyContribution.toLocaleString()}/yr
              </span>
            </div>
            <input
              type="range"
              min="10000"
              max="70000"
              step="5000"
              value={expectedFamilyContribution}
              onChange={(e) => setExpectedFamilyContribution(Number(e.target.value))}
              className="w-full accent-primary mt-2"
              aria-label="Family annual capacity in US dollars"
            />
          </div>

          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="text-xs font-semibold uppercase text-muted-foreground">
                Target Scholarship / Aid
              </label>
              <span className="font-mono text-xs font-bold text-primary">
                ${appliedScholarship.toLocaleString()}/yr
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="40000"
              step="2500"
              value={appliedScholarship}
              onChange={(e) => setAppliedScholarship(Number(e.target.value))}
              className="w-full accent-primary mt-2"
              aria-label="Target scholarship per year in US dollars"
            />
          </div>
        </div>
      </div>

      {/* Verified awards from Offer Vault — updates the funding gap */}
      <VerifiedAwardsPanel
        expectedFamilyContribution={expectedFamilyContribution}
        appliedScholarship={appliedScholarship}
      />

      {/* Side-by-side Capital Plan Comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {plan1 && <PathwayColumn label="Pathway A" plan={plan1} />}
        {plan2 && <PathwayColumn label="Pathway B (Strategic Comparison)" plan={plan2} accent />}
      </div>

      {/* Strategic Capital Delta Takeaway */}
      <div className="rounded-2xl border border-primary/30 bg-primary/5 p-6 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Scale className="w-5 h-5 text-primary" />
            <h4 className="font-display font-bold text-foreground text-base">
              Capital Delta Analysis
            </h4>
          </div>
          <p className="text-xs sm:text-sm text-muted-foreground">
            {cheaper ? (
              <>
                Choosing {cheaper.pick.u.shortName} over {cheaper.other.u.shortName} costs about{" "}
                <strong className="text-foreground font-mono">{money(cheaper.saves)} USD</strong>{" "}
                less over the full degree, before scholarships.
              </>
            ) : t1 != null && t2 != null ? (
              "Both pathways cost about the same over the full degree."
            ) : (
              "A comparison needs a verified full annual cost for both universities."
            )}
          </p>
        </div>

        <Link to="/academic-readiness" className="shrink-0">
          <Button className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold text-xs px-5">
            Save to My Capital Plan
          </Button>
        </Link>
      </div>
    </div>
  );
}

function PathwayColumn({
  label,
  plan,
  accent = false,
}: {
  label: string;
  plan: PathwayPlan;
  accent?: boolean;
}) {
  const { u } = plan;
  const years = u.durationYears;
  return (
    <div className="rounded-2xl border border-border bg-card p-6 shadow-xs space-y-6">
      <div className="flex items-center justify-between border-b border-border pb-4">
        <div>
          <span
            className={`text-xs font-semibold uppercase tracking-wider ${
              accent ? "text-primary" : "text-muted-foreground"
            }`}
          >
            {label}
          </span>
          <h3 className="font-display font-bold text-xl text-foreground mt-0.5">
            {u.flag} {u.name}
          </h3>
          <p className="text-xs text-muted-foreground">
            {years}-Year Degree • {u.city}, {u.country}
          </p>
        </div>
        <span className="font-mono text-xs bg-secondary px-2.5 py-1 rounded font-semibold text-foreground">
          USD{u.costs.currency && u.costs.currency !== "USD" ? ` (from ${u.costs.currency})` : ""}
        </span>
      </div>

      <div className="space-y-3 text-xs">
        <div className="flex justify-between py-1 border-b border-border/60">
          <span className="text-muted-foreground">Annual Tuition & Mandatory Fees:</span>
          <span className="font-mono font-medium text-muted-foreground">
            {money(plan.tuitionFees)}
          </span>
        </div>
        <div className="flex justify-between py-1 border-b border-border/60">
          <span className="text-muted-foreground">Estimated Living & Accommodation / yr:</span>
          <span className="font-mono font-medium text-muted-foreground">{money(plan.living)}</span>
        </div>
        <div className="flex justify-between py-1 border-b border-border/60">
          <span className="text-muted-foreground font-semibold">Total Cumulative Degree Cost:</span>
          <span className="font-mono font-bold text-sm text-muted-foreground">
            {money(plan.degreeTotal)}
          </span>
        </div>
        <div className="flex justify-between py-1 border-b border-border/60 text-primary">
          <span>Less: Modeled Scholarships ({years} yrs):</span>
          <span className="font-mono font-bold">-{money(plan.scholarship)}</span>
        </div>
        <div className="flex justify-between py-1 border-b border-border/60">
          <span className="text-muted-foreground">
            Less: Expected Family Commitment ({years} yrs):
          </span>
          <span className="font-mono font-medium">-{money(plan.family)}</span>
        </div>
      </div>

      <div className="bg-secondary/50 rounded-xl p-4 border border-border text-center space-y-1">
        <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Remaining Family Capital Gap
        </span>
        <div
          className={`text-2xl sm:text-3xl font-mono font-extrabold ${
            plan.gap ? "text-bronze" : "text-primary"
          }`}
        >
          {plan.gap != null ? `${money(plan.gap)} USD` : "Pending verified data"}
        </div>
        <p className="text-[11px] text-muted-foreground">
          {plan.gap == null
            ? "The gap appears once this university has a verified full annual cost."
            : plan.gap > 0
              ? "This gap would need external scholarships, loans, or other funding."
              : "Covered by your family capacity and target scholarship."}
        </p>
      </div>
    </div>
  );
}
