import { useServerFn } from "@tanstack/react-start";
import { useQuery } from "@tanstack/react-query";
import { FileCheck2, TrendingDown, Vault, ArrowRight } from "lucide-react";
import { Link } from "@tanstack/react-router";
import { getVerifiedAwardsSummary } from "../../lib/offer-vault.functions";
import { SectionCard, PendingData } from "./shared";

/**
 * Surfaces the student's verified + reported awards from the Offer Vault inside
 * the Family Education Capital Plan. Shows previous gap → new award → updated gap.
 * This is the primary incentive for students to upload real offers.
 */
export function VerifiedAwardsPanel({
  expectedFamilyContribution,
  appliedScholarship,
}: {
  expectedFamilyContribution: number;
  appliedScholarship: number;
}) {
  const summaryFn = useServerFn(getVerifiedAwardsSummary);
  const { data: summary } = useQuery({
    queryKey: ["verified-awards"],
    queryFn: () => summaryFn(),
  });

  const verifiedAnnual = summary?.totalAnnualAward ?? 0;
  const hasVerified = (summary?.count ?? 0) > 0;
  const hasDocVerified = summary?.hasDocumentVerified ?? false;

  // "Previous" projected funding = the modeled/target scholarship slider.
  // "New" verified funding = actual awards from the Offer Vault.
  const previousProjectedFunding = appliedScholarship;
  const newVerifiedFunding = verifiedAnnual;
  const fundingDelta = newVerifiedFunding - previousProjectedFunding;

  return (
    <SectionCard
      title="Verified awards from your Offer Vault"
      subtitle="Add your scholarship award to update your funding gap. Awards you've stored replace the modeled target."
      action={
        <Link
          to="/offer-vault"
          className="text-xs font-semibold text-primary flex items-center gap-1 hover:underline"
        >
          <Vault className="w-3.5 h-3.5" /> Open Offer Vault
        </Link>
      }
    >
      {!hasVerified ? (
        <div className="rounded-xl border border-dashed border-border bg-secondary/20 p-6 text-center space-y-2">
          <TrendingDown className="w-6 h-6 text-bronze mx-auto" />
          <p className="text-sm text-muted-foreground">
            No awards stored yet. Once you receive a scholarship or aid letter, add it to your Offer
            Vault and your funding gap will update here automatically.
          </p>
          <Link to="/offer-vault">
            <span className="text-xs font-semibold text-primary inline-flex items-center gap-1 hover:underline">
              Upload your offer <ArrowRight className="w-3 h-3" />
            </span>
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="rounded-xl border border-border bg-secondary/30 p-4">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
                Previous projected funding
              </div>
              <div className="text-lg font-mono mt-1 text-muted-foreground">
                ${previousProjectedFunding.toLocaleString()}/yr
              </div>
              <div className="text-[10px] text-muted-foreground mt-1">
                Modeled target scholarship
              </div>
            </div>
            <div className="rounded-xl border border-primary/30 bg-primary/5 p-4">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-primary flex items-center gap-1">
                <FileCheck2 className="w-3 h-3" /> New verified / reported award
              </div>
              <div className="text-lg font-mono mt-1 text-primary font-bold">
                ${newVerifiedFunding.toLocaleString()}/yr
              </div>
              <div className="text-[10px] text-muted-foreground mt-1">
                {summary?.count ?? 0} award(s) stored
                {hasDocVerified ? " • some document-verified" : " • self-reported"}
              </div>
            </div>
            <div className="rounded-xl border border-bronze/30 bg-bronze/5 p-4">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-bronze">
                Funding change
              </div>
              <div className="text-lg font-mono mt-1 text-bronze font-bold">
                {fundingDelta >= 0 ? "+" : ""}
                {fundingDelta.toLocaleString()}/yr
              </div>
              <div className="text-[10px] text-muted-foreground mt-1">
                {fundingDelta >= 0 ? "Reduces your annual family gap" : "Below your modeled target"}
              </div>
            </div>
          </div>

          <div className="text-[11px] text-muted-foreground bg-secondary/40 rounded-lg px-3 py-2 flex items-center gap-2">
            <span className="inline-block w-1.5 h-1.5 rounded-full bg-bronze" />
            Updated projected funding gap uses your stored awards instead of the modeled target.
            Cost figures remain illustrative until verified data is connected.
            {hasDocVerified ? (
              <span className="text-primary"> • Some awards document-verified.</span>
            ) : (
              <PendingData label=" • Awards self-reported — upload letters to verify." />
            )}
          </div>
        </div>
      )}
    </SectionCard>
  );
}
