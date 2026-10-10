import { createFileRoute, Link } from "@tanstack/react-router";
import { requireAuth } from "../lib/route-guard";
import { useState } from "react";
import {
  PiggyBank,
  DollarSign,
  ArrowRight,
  ShieldCheck,
  TrendingDown,
  Scale,
  CheckCircle2,
} from "lucide-react";
import { Button } from "../components/ui/button";
import { UNIVERSITIES_DATA } from "../lib/mock-data";
import { isPending } from "../lib/format";
import { VerifiedAwardsPanel } from "../components/offer-vault/VerifiedAwardsPanel";
import { canonicalLink, ogUrlMeta } from "../lib/seo";

function money(value: number | null): string {
  if (isPending(value)) return "Pending verified data";
  return `$${value!.toLocaleString()}`;
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

function FundPage() {
  const [selectedUniv1, setSelectedUniv1] = useState("oxford-univ");
  const [selectedUniv2, setSelectedUniv2] = useState("tum-germany");
  const [expectedFamilyContribution, setExpectedFamilyContribution] = useState(35000); // per year
  const [appliedScholarship, setAppliedScholarship] = useState(15000); // per year

  const u1 = UNIVERSITIES_DATA.find((u) => u.id === selectedUniv1) || UNIVERSITIES_DATA[0];
  const u2 = UNIVERSITIES_DATA.find((u) => u.id === selectedUniv2) || UNIVERSITIES_DATA[2];

  const u1HasData = !isPending(u1.costs.totalAnnual);
  const u2HasData = !isPending(u2.costs.totalAnnual);

  // Calculations for Option 1 (only when verified cost data exists)
  const u1AnnualTotal = u1.costs.totalAnnual ?? 0;
  const u1DegreeTotal = u1AnnualTotal * u1.durationYears;
  const u1DegreeFunding = appliedScholarship * u1.durationYears;
  const u1FamilyCapacity = expectedFamilyContribution * u1.durationYears;
  const u1NetGap = Math.max(0, u1DegreeTotal - u1DegreeFunding - u1FamilyCapacity);

  // Calculations for Option 2
  const u2AnnualTotal = u2.costs.totalAnnual ?? 0;
  const u2DegreeTotal = u2AnnualTotal * u2.durationYears;
  const u2DegreeFunding = Math.min(appliedScholarship, u2AnnualTotal) * u2.durationYears;
  const u2FamilyCapacity = expectedFamilyContribution * u2.durationYears;
  const u2NetGap = Math.max(0, u2DegreeTotal - u2DegreeFunding - u2FamilyCapacity);

  const deltaAvailable = u1HasData && u2HasData;

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
          Turn an acceptance goal into a four-year financial roadmap. Closer to private wealth
          planning than an arbitrary college-cost calculator. Verified cost figures will populate
          the plan as data is added.
        </p>
        <div className="flex items-center gap-2 text-[11px] text-muted-foreground bg-secondary/50 border border-border rounded-lg px-3 py-2">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-bronze" />
          <span>
            Illustrative product preview. Live analysis will use verified EvidaPath data. Cost
            figures currently being verified.
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
              className="w-full h-10 px-3 rounded-lg border border-input bg-background text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
            >
              {UNIVERSITIES_DATA.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.flag} {u.name} ({u.durationYears} yrs)
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase text-muted-foreground mb-1.5">
              Pathway B (Comparison / Strategic Pivot)
            </label>
            <select
              value={selectedUniv2}
              onChange={(e) => setSelectedUniv2(e.target.value)}
              className="w-full h-10 px-3 rounded-lg border border-input bg-background text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
            >
              {UNIVERSITIES_DATA.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.flag} {u.name} ({u.durationYears} yrs)
                </option>
              ))}
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
        {/* Pathway A */}
        <div className="rounded-2xl border border-border bg-card p-6 shadow-xs space-y-6">
          <div className="flex items-center justify-between border-b border-border pb-4">
            <div>
              <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Pathway A
              </span>
              <h3 className="font-display font-bold text-xl text-foreground mt-0.5">
                {u1.flag} {u1.name}
              </h3>
              <p className="text-xs text-muted-foreground">
                {u1.durationYears}-Year Degree • {u1.city}, {u1.country}
              </p>
            </div>
            <span className="font-mono text-xs bg-secondary px-2.5 py-1 rounded font-semibold text-foreground">
              {u1.costs.currency} Base
            </span>
          </div>

          {/* Breakdown numbers */}
          <div className="space-y-3 text-xs">
            <div className="flex justify-between py-1 border-b border-border/60">
              <span className="text-muted-foreground">Annual Tuition & Mandatory Fees:</span>
              <span className="font-mono font-medium text-muted-foreground">
                {u1HasData
                  ? money(u1.costs.tuitionPerYear! + (u1.costs.mandatoryFees ?? 0))
                  : "Pending verified data"}
              </span>
            </div>
            <div className="flex justify-between py-1 border-b border-border/60">
              <span className="text-muted-foreground">Estimated Living & Accommodation / yr:</span>
              <span className="font-mono font-medium text-muted-foreground">
                {money(u1.costs.livingPerYear)}
              </span>
            </div>
            <div className="flex justify-between py-1 border-b border-border/60">
              <span className="text-muted-foreground font-semibold">
                Total Cumulative Degree Cost:
              </span>
              <span className="font-mono font-bold text-sm text-muted-foreground">
                {u1HasData ? money(u1DegreeTotal) : "Pending verified data"}
              </span>
            </div>
            <div className="flex justify-between py-1 border-b border-border/60 text-primary">
              <span>Less: Modeled Scholarships ({u1.durationYears} yrs):</span>
              <span className="font-mono font-bold">-${u1DegreeFunding.toLocaleString()}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-border/60">
              <span className="text-muted-foreground">
                Less: Expected Family Commitment ({u1.durationYears} yrs):
              </span>
              <span className="font-mono font-medium">-${u1FamilyCapacity.toLocaleString()}</span>
            </div>
          </div>

          {/* Net Funding Gap Box */}
          <div className="bg-secondary/50 rounded-xl p-4 border border-border text-center space-y-1">
            <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Remaining Family Capital Gap
            </span>
            <div className="text-2xl sm:text-3xl font-mono font-extrabold text-bronze">
              {u1HasData ? `${money(u1NetGap)} USD` : "Pending verified data"}
            </div>
            <p className="text-[11px] text-muted-foreground">
              {u1HasData
                ? u1NetGap > 0
                  ? "Funding gap requires targeted external scholarships, student loans, or campus employment."
                  : "Fully funded within current family capacity and target scholarship range."
                : "Gap analysis available once verified cost data is connected."}
            </p>
          </div>
        </div>

        {/* Pathway B */}
        <div className="rounded-2xl border border-border bg-card p-6 shadow-xs space-y-6">
          <div className="flex items-center justify-between border-b border-border pb-4">
            <div>
              <span className="text-xs font-semibold uppercase tracking-wider text-primary">
                Pathway B (Strategic Comparison)
              </span>
              <h3 className="font-display font-bold text-xl text-foreground mt-0.5">
                {u2.flag} {u2.name}
              </h3>
              <p className="text-xs text-muted-foreground">
                {u2.durationYears}-Year Degree • {u2.city}, {u2.country}
              </p>
            </div>
            <span className="font-mono text-xs bg-secondary px-2.5 py-1 rounded font-semibold text-foreground">
              {u2.costs.currency} Base
            </span>
          </div>

          {/* Breakdown numbers */}
          <div className="space-y-3 text-xs">
            <div className="flex justify-between py-1 border-b border-border/60">
              <span className="text-muted-foreground">Annual Tuition & Mandatory Fees:</span>
              <span className="font-mono font-medium text-muted-foreground">
                {u2HasData
                  ? money(u2.costs.tuitionPerYear! + (u2.costs.mandatoryFees ?? 0))
                  : "Pending verified data"}
              </span>
            </div>
            <div className="flex justify-between py-1 border-b border-border/60">
              <span className="text-muted-foreground">Estimated Living & Accommodation / yr:</span>
              <span className="font-mono font-medium text-muted-foreground">
                {money(u2.costs.livingPerYear)}
              </span>
            </div>
            <div className="flex justify-between py-1 border-b border-border/60">
              <span className="text-muted-foreground font-semibold">
                Total Cumulative Degree Cost:
              </span>
              <span className="font-mono font-bold text-sm text-muted-foreground">
                {u2HasData ? money(u2DegreeTotal) : "Pending verified data"}
              </span>
            </div>
            <div className="flex justify-between py-1 border-b border-border/60 text-primary">
              <span>Less: Modeled Scholarships ({u2.durationYears} yrs):</span>
              <span className="font-mono font-bold">-${u2DegreeFunding.toLocaleString()}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-border/60">
              <span className="text-muted-foreground">
                Less: Expected Family Commitment ({u2.durationYears} yrs):
              </span>
              <span className="font-mono font-medium">-${u2FamilyCapacity.toLocaleString()}</span>
            </div>
          </div>

          {/* Net Funding Gap Box */}
          <div className="bg-secondary/50 rounded-xl p-4 border border-border text-center space-y-1">
            <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Remaining Family Capital Gap
            </span>
            <div className="text-2xl sm:text-3xl font-mono font-extrabold text-primary">
              {u2HasData ? `${money(u2NetGap)} USD` : "Pending verified data"}
            </div>
            <p className="text-[11px] text-muted-foreground">
              {u2HasData
                ? u2NetGap === 0
                  ? "Zero capital shortfall. Leaves family surplus capital for postgraduate study."
                  : "Manageable low-capital gap."
                : "Gap analysis available once verified cost data is connected."}
            </p>
          </div>
        </div>
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
            {deltaAvailable ? (
              <>
                Selecting Pathway B ({u2.shortName}) over Pathway A ({u1.shortName}) preserves
                approximately{" "}
                <strong className="text-foreground font-mono">
                  ${Math.abs(u1DegreeTotal - u2DegreeTotal).toLocaleString()} USD
                </strong>{" "}
                in total family educational capital over the course of the degree.
              </>
            ) : (
              "Capital delta analysis available once verified cost data is connected for both pathways."
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
