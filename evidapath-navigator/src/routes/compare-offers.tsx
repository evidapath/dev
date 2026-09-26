import { createFileRoute, Link } from "@tanstack/react-router";
import { useServerFn } from "@tanstack/react-start";
import { useQuery } from "@tanstack/react-query";
import { Scale, ShieldCheck, Inbox, ArrowRight } from "lucide-react";
import { requireAuth } from "../lib/route-guard";
import { Button } from "../components/ui/button";
import { listOfferComposites } from "../lib/offer-vault.functions";
import type { OfferComposite } from "../lib/offer-vault.types";
import {
  EmptyState,
  IllustrativePreviewLabel,
  Money,
  PendingData,
  SectionCard,
  VerificationBadge,
} from "../components/offer-vault/shared";

export const Route = createFileRoute("/compare-offers")({
  head: () => ({
    meta: [
      { title: "Compare Offers — EvidaPath" },
      {
        name: "description",
        content:
          "Compare admitted universities by net cost, awards, deadlines, renewal requirements, and funding gaps.",
      },
      { property: "og:title", content: "Compare Offers — EvidaPath" },
      {
        property: "og:description",
        content: "Compare your offers before you commit.",
      },
    ],
  }),
  beforeLoad: ({ context, location }) => requireAuth(context, location.pathname),
  component: CompareOffersPage,
});

function CompareOffersPage() {
  const listFn = useServerFn(listOfferComposites);
  const { data: composites = [] } = useQuery({
    queryKey: ["offer-composites"],
    queryFn: () => listFn(),
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <div className="max-w-3xl space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold">
          <Scale className="w-3.5 h-3.5" />
          <span>My EvidaPath • Compare Offers</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-display font-extrabold text-foreground">
          Compare Offers
        </h1>
        <p className="text-sm sm:text-base text-muted-foreground leading-relaxed">
          Compare your offers before you commit. See net family cost, awards, deadlines, renewal
          requirements, and funding gaps side by side — not reduced to a single opaque score.
        </p>
        <IllustrativePreviewLabel text="Comparison uses your stored offers and awards plus public university cost data. Cost figures are illustrative until verified data is connected." />
      </div>

      {composites.length < 2 ? (
        <EmptyState
          icon={Inbox}
          title="Add at least two offers to compare"
          description="Add at least two offers to compare net cost, awards, deadlines and funding gaps. Once you have offers in your Offer Vault, they'll appear here side by side."
          action={
            <Link to="/offer-vault">
              <Button className="bg-primary hover:bg-primary/90 text-primary-foreground text-sm font-semibold mt-2 flex items-center gap-1.5">
                Go to Offer Vault <ArrowRight className="w-3.5 h-3.5" />
              </Button>
            </Link>
          }
        />
      ) : (
        <ComparisonTable composites={composites} />
      )}

      <div className="flex items-center gap-2 text-[11px] text-muted-foreground border-t border-border pt-6">
        <ShieldCheck className="w-3.5 h-3.5 text-primary shrink-0" />
        <span>
          Comparison data is accessed only through your authenticated session and is subject to Row
          Level Security. No single opaque score is produced.
        </span>
      </div>
    </div>
  );
}

function ComparisonTable({ composites }: { composites: OfferComposite[] }) {
  const rows: {
    label: string;
    render: (c: OfferComposite) => React.ReactNode;
    note?: string;
  }[] = [
    {
      label: "University",
      render: (c) => (
        <span className="font-display font-bold text-sm">{c.application.university_name}</span>
      ),
    },
    {
      label: "Program",
      render: (c) => <span className="text-xs">{c.application.program_name ?? "—"}</span>,
    },
    {
      label: "Degree duration",
      render: (c) =>
        c.analysis.degreeDurationYears ? (
          <span className="font-mono text-xs">{c.analysis.degreeDurationYears} yrs</span>
        ) : (
          <PendingData label="Pending" />
        ),
    },
    {
      label: "Published tuition / yr",
      render: (c) => {
        const uni = c.analysis;
        return <Money value={uni.annualCost} currency={c.offer.currency} />;
      },
      note: "Illustrative until verified",
    },
    {
      label: "Scholarship awarded (annual)",
      render: (c) => (
        <span className="font-mono text-primary">
          ${c.analysis.totalAwardAnnual.toLocaleString()}
        </span>
      ),
    },
    {
      label: "Net annual family cost",
      render: (c) =>
        c.analysis.netAnnualFamilyCost != null ? (
          <span className="font-mono font-bold text-foreground">
            ${c.analysis.netAnnualFamilyCost.toLocaleString()}
          </span>
        ) : (
          <PendingData label="Pending verified cost" />
        ),
      note: "Cost minus awards",
    },
    {
      label: "Estimated total family cost",
      render: (c) =>
        c.analysis.totalDegreeFamilyCost != null ? (
          <span className="font-mono font-bold text-bronze">
            ${c.analysis.totalDegreeFamilyCost.toLocaleString()}
          </span>
        ) : (
          <PendingData label="Pending" />
        ),
    },
    {
      label: "Remaining funding gap",
      render: (c) =>
        c.analysis.netAnnualFamilyCost != null ? (
          <span className="font-mono text-bronze">
            ${c.analysis.netAnnualFamilyCost.toLocaleString()}/yr
          </span>
        ) : (
          <PendingData label="Pending" />
        ),
      note: "Before family contribution",
    },
    {
      label: "Deposit",
      render: (c) =>
        c.offer.enrollment_deposit_amount != null ? (
          <span className="font-mono text-xs">
            ${c.offer.enrollment_deposit_amount.toLocaleString()} {c.offer.currency}
          </span>
        ) : (
          "—"
        ),
    },
    {
      label: "Acceptance deadline",
      render: (c) => <span className="text-xs">{c.offer.response_deadline ?? "—"}</span>,
    },
    {
      label: "Renewal requirements",
      render: (c) => {
        const renewals = c.awards.filter((a) => a.renewal_criteria).map((a) => a.renewal_criteria);
        return renewals.length ? (
          <span className="text-xs">{renewals.join("; ")}</span>
        ) : (
          <span className="text-xs text-muted-foreground">None recorded</span>
        );
      },
    },
    {
      label: "Verification status",
      render: (c) => (
        <div className="flex flex-col gap-1 items-start">
          <VerificationBadge level={c.offer.verification_level} />
          {c.analysis.hasDocumentVerifiedAwards && (
            <span className="text-[10px] text-primary">Some awards verified</span>
          )}
        </div>
      ),
    },
  ];

  return (
    <SectionCard>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr>
              <th className="text-left text-[11px] font-semibold uppercase tracking-wide text-muted-foreground p-3 border-b border-border w-48 sticky left-0 bg-card">
                Dimension
              </th>
              {composites.map((c) => (
                <th key={c.offer.id} className="text-left p-3 border-b border-border min-w-[180px]">
                  <div className="space-y-0.5">
                    <div className="font-display font-bold text-sm text-foreground">
                      {c.application.university_name}
                    </div>
                    <div className="text-[10px] text-muted-foreground">
                      {c.application.program_name ?? "Program"}
                    </div>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={row.label} className={i % 2 ? "bg-secondary/20" : ""}>
                <td className="p-3 border-b border-border/60 text-xs font-medium text-muted-foreground sticky left-0 bg-inherit">
                  {row.label}
                  {row.note && (
                    <span className="block text-[10px] text-muted-foreground/70">{row.note}</span>
                  )}
                </td>
                {composites.map((c) => (
                  <td key={c.offer.id} className="p-3 border-b border-border/60 align-top">
                    {row.render(c)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </SectionCard>
  );
}
