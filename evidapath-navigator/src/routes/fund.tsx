import { useUniversitiesFn, useFxRatesFn } from "../lib/use-live-data";
import { PageGuide } from "../components/PageGuide";
import { createFileRoute, Link } from "@tanstack/react-router";
import { requireAuth } from "../lib/route-guard";
import { useEffect, useState } from "react";
import { PiggyBank, Scale } from "lucide-react";
import { Button } from "../components/ui/button";
import { toUsd, type FxRates } from "../lib/fx.functions";
import type { University } from "../lib/mock-data";
import { VerifiedAwardsPanel } from "../components/offer-vault/VerifiedAwardsPanel";
import { formatCurrency } from "../lib/format";
import { canonicalLink, ogUrlMeta } from "../lib/seo";
import { SearchSelect } from "../components/SearchSelect";
import { universityOption } from "../lib/university-options";
import { PageHeader } from "../components/PageHeader";

function money(value: number | null): string {
  return formatCurrency(value, "USD");
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

// One university's plan, entirely in USD so it can be compared with the (USD) family
// and scholarship sliders. Parts are rounded first and the total is their sum, so
// every column on the page adds up. Null figures mean the cost isn't published.
interface PathwayPlan {
  u: University;
  tuitionFees: number | null;
  living: number | null;
  degreeTotal: number | null;
  /** Scholarship actually used (never more than the cost). */
  scholarship: number;
  /** Family money actually needed (never more than what's left after scholarships). */
  family: number;
  familyCapacity: number;
  gap: number | null;
}

function buildPlan(
  u: University,
  fx: FxRates | null,
  familyPerYear: number,
  scholarshipPerYear: number,
): PathwayPlan {
  const usd = (v: number | null) =>
    v == null ? null : Math.round(toUsd(v, u.costs.currency || "", fx) ?? NaN);
  const ok = (v: number | null) => (v == null || Number.isNaN(v) ? null : v);
  const tuition = ok(usd(u.costs.tuitionPerYear));
  const fees = ok(usd(u.costs.mandatoryFees)) ?? 0;
  const living = ok(usd(u.costs.livingPerYear));
  const years = u.durationYears || 0;
  const tuitionFees = tuition == null ? null : tuition + fees;
  const degreeTotal =
    tuitionFees != null && years > 0 ? (tuitionFees + (living ?? 0)) * years : null;
  const familyCapacity = familyPerYear * years;
  if (degreeTotal == null)
    return {
      u,
      tuitionFees,
      living,
      degreeTotal,
      scholarship: 0,
      family: 0,
      familyCapacity,
      gap: null,
    };
  const scholarship = Math.min(scholarshipPerYear * years, degreeTotal);
  const family = Math.min(familyCapacity, degreeTotal - scholarship);
  return {
    u,
    tuitionFees,
    living,
    degreeTotal,
    scholarship,
    family,
    familyCapacity,
    gap: degreeTotal - scholarship - family,
  };
}

function FundPage() {
  const [universities, setUniversities] = useState<University[]>([]);
  const [fx, setFx] = useState<FxRates | null>(null);
  const [selectedUniv1, setSelectedUniv1] = useState("");
  const [selectedUniv2, setSelectedUniv2] = useState("");
  const [expectedFamilyContribution, setExpectedFamilyContribution] = useState(35000); // per year
  const [appliedScholarship, setAppliedScholarship] = useState(15000); // per year

  const fetchUniversities = useUniversitiesFn();
  const fetchFx = useFxRatesFn();
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
  const uniOptions = universities.map((u) =>
    universityOption(u, `${u.name} (${u.durationYears} yrs)`),
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      <PageHeader
        icon={PiggyBank}
        eyebrow="Funding"
        title="Can your family"
        accent="afford it?"
        intro="Pick two universities, set what your family can pay and the scholarships you expect, and see what's left to find over the whole degree."
        note={`Costs come from official sources${
          fx ? `, converted to US dollars at European Central Bank rates from ${fx.date}` : ""
        }. The amounts you set are your own estimates and aren't saved.`}
      />

      <PageGuide
        id="fund"
        title="See whether your family can afford a university"
        steps={[
          {
            title: "Pick two universities",
            text: "Choose the two options you're weighing. Their yearly costs come from official sources, converted to US dollars.",
          },
          {
            title: "Enter what your family can pay",
            text: "Move the family contribution slider to what you can realistically spend each year.",
          },
          {
            title: "Add expected scholarships",
            text: "Only include money you're confident about. Awards you've recorded in your Offer Vault are shown in their own panel below, so you can check your estimate against them.",
          },
          {
            title: "Read the gap",
            text: "The gap is what's left to find over the whole degree. The cheaper option is named for you.",
          },
        ]}
        tip="Planning guesses are fine here — nothing on this page is saved or shared."
      />

      {/* Assumptions & Controller Box */}
      <div className="bg-card border border-border rounded-2xl p-6 shadow-xs space-y-6">
        <div className="border-b border-border pb-3">
          <h2 className="font-display font-bold text-base text-foreground">Your numbers</h2>
          <p className="text-xs text-muted-foreground">
            Change these and both universities update below.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div>
            <label className="block text-xs font-semibold text-muted-foreground mb-1.5">
              First university
            </label>
            <SearchSelect
              aria-label="First university"
              options={uniOptions}
              value={selectedUniv1}
              onChange={setSelectedUniv1}
              searchPlaceholder="Type a university or country…"
              className={selectCls}
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-muted-foreground mb-1.5">
              Second university
            </label>
            <SearchSelect
              aria-label="Second university"
              options={uniOptions}
              value={selectedUniv2}
              onChange={setSelectedUniv2}
              searchPlaceholder="Type a university or country…"
              className={selectCls}
            />
          </div>

          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="text-xs font-semibold text-muted-foreground">Family can pay</label>
              <span className="text-sm font-bold text-foreground tabular-nums">
                {money(expectedFamilyContribution)} / year
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
              <label className="text-xs font-semibold text-muted-foreground">
                Scholarships expected
              </label>
              <span className="text-sm font-bold text-primary tabular-nums">
                {money(appliedScholarship)} / year
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
        {plan1 && <PathwayColumn label="First university" plan={plan1} />}
        {plan2 && <PathwayColumn label="Second university" plan={plan2} accent />}
      </div>

      {/* Strategic Capital Delta Takeaway */}
      <div className="rounded-2xl border border-primary/30 bg-primary/5 p-6 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Scale className="w-5 h-5 text-primary" />
            <h4 className="font-display font-bold text-foreground text-base">Which costs less?</h4>
          </div>
          <p className="text-xs sm:text-sm text-muted-foreground">
            {cheaper ? (
              <>
                Choosing {cheaper.pick.u.shortName} over {cheaper.other.u.shortName} costs about{" "}
                <strong className="text-foreground tabular-nums">{money(cheaper.saves)}</strong>{" "}
                less over the full degree, before scholarships.
              </>
            ) : t1 != null && t2 != null ? (
              "Both cost about the same over the full degree."
            ) : (
              "A comparison needs a published tuition for both universities."
            )}
          </p>
        </div>

        <Link to="/academic-readiness" className="shrink-0">
          <Button className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold text-xs px-5">
            Check my academic readiness
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
  const { u, degreeTotal } = plan;
  const years = u.durationYears;
  const pct = (v: number) => (degreeTotal ? Math.max(0, (v / degreeTotal) * 100) : 0);
  const rows: [string, string, string?][] = [
    ["Tuition and fees / year", money(plan.tuitionFees)],
    ["Living / year", plan.living == null ? "Not published" : money(plan.living)],
  ];
  return (
    <div className="rounded-2xl border border-border bg-card shadow-sm overflow-hidden flex flex-col">
      <div className="px-6 pt-5 pb-4 border-b border-border/70 bg-secondary/40">
        <span
          className={`text-[11px] font-semibold uppercase tracking-wider ${
            accent ? "text-primary" : "text-muted-foreground"
          }`}
        >
          {label}
        </span>
        <h3 className="font-display font-bold text-xl text-foreground mt-0.5 leading-tight">
          <span className="mr-1.5">{u.flag}</span>
          {u.name}
        </h3>
        <p className="text-xs text-muted-foreground mt-0.5">
          {years}-year degree · {u.city}, {u.country}
          {u.costs.currency && u.costs.currency !== "USD"
            ? ` · converted from ${u.costs.currency}`
            : ""}
        </p>
      </div>

      <div className="p-6 space-y-5 flex-1">
        <div>
          <p className="text-xs text-muted-foreground">Whole degree</p>
          <p className="font-display font-extrabold text-3xl text-foreground tabular-nums leading-tight">
            {money(degreeTotal)}
          </p>
          {degreeTotal != null && (
            <p className="text-[11px] text-muted-foreground">
              (tuition and fees{plan.living != null ? " + living" : ""}) × {years} years
              {plan.living == null ? " · living cost not published, not included" : ""}
            </p>
          )}
        </div>

        {/* Where the money comes from, as one bar */}
        {degreeTotal != null && degreeTotal > 0 && (
          <div className="space-y-2">
            <div
              className="flex h-4 w-full overflow-hidden rounded-full bg-secondary"
              role="img"
              aria-label={`Scholarships ${money(plan.scholarship)}, family ${money(plan.family)}, still to find ${money(plan.gap)}`}
            >
              <div className="bg-primary" style={{ width: `${pct(plan.scholarship)}%` }} />
              <div className="bg-navy dark:bg-sky-400" style={{ width: `${pct(plan.family)}%` }} />
              <div className="bg-bronze" style={{ width: `${pct(plan.gap ?? 0)}%` }} />
            </div>
            <dl className="grid grid-cols-3 gap-2 text-[11px]">
              {(
                [
                  ["bg-primary", "Scholarships", plan.scholarship],
                  ["bg-navy dark:bg-sky-400", "Your family", plan.family],
                  ["bg-bronze", "Still to find", plan.gap ?? 0],
                ] as const
              ).map(([c, k, v]) => (
                <div key={k}>
                  <dt className="flex items-center gap-1.5 text-muted-foreground">
                    <span className={`w-2 h-2 rounded-full ${c}`} />
                    {k}
                  </dt>
                  <dd className="font-semibold text-foreground tabular-nums mt-0.5">{money(v)}</dd>
                </div>
              ))}
            </dl>
          </div>
        )}

        <dl className="space-y-1.5 text-xs border-t border-border/60 pt-4">
          {rows.map(([k, v]) => (
            <div key={k} className="flex justify-between gap-3">
              <dt className="text-muted-foreground">{k}</dt>
              <dd className="font-medium text-foreground tabular-nums">{v}</dd>
            </div>
          ))}
          {degreeTotal != null && plan.family < plan.familyCapacity && (
            <p className="text-[11px] text-muted-foreground pt-1">
              Your family needs {money(plan.family)} of the {money(plan.familyCapacity)} it could
              pay over {years} years.
            </p>
          )}
        </dl>
      </div>

      <div
        className={`px-6 py-4 text-center border-t ${
          plan.gap ? "bg-bronze/10 border-bronze/20" : "bg-primary/5 border-primary/15"
        }`}
      >
        <p className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
          Still to find
        </p>
        <p
          className={`font-display font-extrabold text-2xl sm:text-3xl tabular-nums ${
            plan.gap ? "text-bronze" : "text-primary"
          }`}
        >
          {plan.gap != null ? money(plan.gap) : "Not published"}
        </p>
        <p className="text-[11px] text-muted-foreground">
          {plan.gap == null
            ? "This university's tuition isn't published yet."
            : plan.gap > 0
              ? "This would need more scholarships, loans or other funding."
              : "Covered by your family and expected scholarships."}
        </p>
      </div>
    </div>
  );
}
