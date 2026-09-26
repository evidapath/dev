import { Link } from "@tanstack/react-router";
import { useServerFn } from "@tanstack/react-start";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";
import { Trash2, ArrowRight, X, CalendarClock, FileCheck2, TrendingDown } from "lucide-react";
import { Button } from "../ui/button";
import { listApplications, upsertOffer } from "../../lib/offer-vault.functions";
import type { OfferComposite } from "../../lib/offer-vault.types";
import { VerificationBadge, Money, PendingData, SectionCard, inputCls, labelCls } from "./shared";
import { AwardsSection } from "./AwardsSection";
import { DocumentsSection } from "./DocumentsSection";
import { EnrollmentSection } from "./EnrollmentSection";

export function OfferDetail({
  composite,
  onDelete,
}: {
  composite: OfferComposite;
  onDelete: () => void;
}) {
  const { offer, application, awards, documents, enrollment, analysis } = composite;

  const invalidate = () => {
    // Parent owns the query; we trigger via a custom event the parent listens to.
    window.dispatchEvent(new CustomEvent("offer-vault-mutated"));
  };

  return (
    <div className="space-y-6">
      <SectionCard>
        <div className="flex items-start justify-between gap-3">
          <div className="space-y-1">
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="font-display font-bold text-xl text-foreground">
                {application.university_name}
              </h3>
              <VerificationBadge level={offer.verification_level} />
            </div>
            <p className="text-xs text-muted-foreground">
              {application.program_name ?? "Program not specified"}
              {application.application_cycle ? ` • ${application.application_cycle}` : ""}
            </p>
          </div>
          <button
            onClick={onDelete}
            className="p-2 rounded-lg text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
            aria-label="Delete offer"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </SectionCard>

      {/* Offer Analysis */}
      <SectionCard
        title="Offer Analysis"
        subtitle="Published/estimated cost minus verified awards = estimated net family cost."
        action={
          <span className="text-[10px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded bg-secondary text-muted-foreground">
            {analysis.costDataStatus === "pending"
              ? "Cost data pending"
              : "Illustrative cost basis"}
          </span>
        }
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <AnalysisRow
            label="Published / estimated annual cost"
            value={<Money value={analysis.annualCost} currency={offer.currency} />}
            note="University-published / EvidaPath estimate (public data)"
          />
          <AnalysisRow
            label="Verified + reported awards (annual equiv.)"
            value={
              <span className="font-mono text-primary">
                −${analysis.totalAwardAnnual.toLocaleString()}
              </span>
            }
            note="From your stored awards"
          />
          <AnalysisRow
            label="Estimated net annual family cost"
            value={
              analysis.netAnnualFamilyCost != null ? (
                <span className="font-mono font-bold text-foreground">
                  ${analysis.netAnnualFamilyCost.toLocaleString()}
                </span>
              ) : (
                <PendingData label="Pending verified cost data" />
              )
            }
            note="Cost minus awards"
            highlight
          />
          <AnalysisRow
            label="Estimated total degree family cost"
            value={
              analysis.totalDegreeFamilyCost != null ? (
                <span className="font-mono font-bold text-bronze">
                  ${analysis.totalDegreeFamilyCost.toLocaleString()}
                </span>
              ) : (
                <PendingData label="Pending verified cost + duration" />
              )
            }
            note={
              analysis.degreeDurationYears
                ? `Over ${analysis.degreeDurationYears} years`
                : "Duration pending"
            }
            highlight
          />
        </div>

        {analysis.costDataStatus === "pending" && (
          <div className="text-[11px] text-muted-foreground bg-secondary/40 rounded-lg px-3 py-2 flex items-center gap-2">
            <TrendingDown className="w-3.5 h-3.5 text-bronze shrink-0" />
            Gap analysis available once verified cost data is connected. Your awards are still
            stored and will reduce the gap automatically.
          </div>
        )}
        {analysis.hasDocumentVerifiedAwards && (
          <div className="text-[11px] text-primary bg-primary/5 rounded-lg px-3 py-2 flex items-center gap-2">
            <FileCheck2 className="w-3.5 h-3.5 shrink-0" />
            One or more awards are document-verified.
          </div>
        )}
      </SectionCard>

      {/* Offer terms */}
      <SectionCard title="Offer terms" subtitle="Admission details, deposit, and deadlines.">
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-xs">
          <DetailField label="Admission result" value={offer.admission_result} />
          <DetailField label="Offer date" value={offer.official_offer_date ?? "—"} />
          <DetailField
            label="Response deadline"
            value={offer.response_deadline ?? "—"}
            icon={CalendarClock}
          />
          <DetailField
            label="Enrollment deposit"
            value={
              offer.enrollment_deposit_amount != null
                ? `$${offer.enrollment_deposit_amount.toLocaleString()} ${offer.currency}`
                : "—"
            }
          />
          <DetailField label="Deposit deadline" value={offer.deposit_deadline ?? "—"} />
          <DetailField label="Currency" value={offer.currency} />
        </div>
        {offer.conditions_of_admission && (
          <div className="text-xs text-muted-foreground pt-2 border-t border-border/60">
            <strong className="text-foreground">Conditions:</strong> {offer.conditions_of_admission}
          </div>
        )}
        {offer.notes && (
          <div className="text-xs text-muted-foreground">
            <strong className="text-foreground">Notes:</strong> {offer.notes}
          </div>
        )}
      </SectionCard>

      <AwardsSection
        offerId={offer.id}
        currency={offer.currency}
        awards={awards}
        onMutated={invalidate}
      />
      <DocumentsSection offerId={offer.id} documents={documents} onMutated={invalidate} />
      <EnrollmentSection
        offerId={offer.id}
        currency={offer.currency}
        enrollment={enrollment}
        onMutated={invalidate}
      />

      <div className="flex justify-end">
        <Link to="/compare-offers">
          <Button className="bg-primary hover:bg-primary/90 text-primary-foreground text-sm font-semibold flex items-center gap-1.5">
            Compare this offer <ArrowRight className="w-3.5 h-3.5" />
          </Button>
        </Link>
      </div>
    </div>
  );
}

function AnalysisRow({
  label,
  value,
  note,
  highlight,
}: {
  label: string;
  value: React.ReactNode;
  note?: string;
  highlight?: boolean;
}) {
  return (
    <div
      className={`rounded-xl p-4 border ${
        highlight ? "border-primary/30 bg-primary/5" : "border-border bg-secondary/30"
      }`}
    >
      <div className="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
        {label}
      </div>
      <div className="text-lg mt-1">{value}</div>
      {note && <div className="text-[10px] text-muted-foreground mt-1">{note}</div>}
    </div>
  );
}

function DetailField({
  label,
  value,
  icon: Icon,
}: {
  label: string;
  value: string;
  icon?: typeof CalendarClock;
}) {
  return (
    <div>
      <div className="text-[10px] font-semibold uppercase tracking-wide text-muted-foreground flex items-center gap-1">
        {Icon && <Icon className="w-3 h-3" />}
        {label}
      </div>
      <div className="text-sm text-foreground mt-0.5">{value}</div>
    </div>
  );
}

// ── Add offer dialog ───────────────────────────────────────────────────────

export function AddOfferDialog({
  onClose,
  onCreated,
}: {
  onClose: () => void;
  onCreated: (id: string) => void;
}) {
  const listAppsFn = useServerFn(listApplications);
  const upsertOfferFn = useServerFn(upsertOffer);
  const { data: applications = [] } = useQuery({
    queryKey: ["applications"],
    queryFn: () => listAppsFn(),
  });

  const admittedApps = applications.filter((a) => a.status === "admitted");
  const [appId, setAppId] = useState("");
  const [offerDate, setOfferDate] = useState("");
  const [deadline, setDeadline] = useState("");
  const [deposit, setDeposit] = useState("");
  const [depositDeadline, setDepositDeadline] = useState("");
  const [currency, setCurrency] = useState("USD");
  const [conditions, setConditions] = useState("");
  const [saving, setSaving] = useState(false);

  const submit = async () => {
    if (!appId) {
      toast.error("Select an admitted application to attach the offer to.");
      return;
    }
    setSaving(true);
    try {
      const created = await upsertOfferFn({
        data: {
          application_id: appId,
          admission_result: "admitted",
          official_offer_date: offerDate || null,
          response_deadline: deadline || null,
          enrollment_deposit_amount: deposit ? Number(deposit) : null,
          deposit_deadline: depositDeadline || null,
          currency,
          conditions_of_admission: conditions || null,
          verification_level: "self_reported",
        },
      });
      onCreated(created.id);
      toast.success("Offer added.");
    } catch (e) {
      toast.error((e as Error).message || "Could not create offer.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-card border border-border rounded-2xl shadow-xl w-full max-w-lg p-6 space-y-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between">
          <h3 className="font-display font-bold text-lg text-foreground">Add offer</h3>
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-muted-foreground hover:bg-secondary"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {admittedApps.length === 0 ? (
          <div className="text-sm text-muted-foreground space-y-3 py-4">
            <p>
              You need an application marked <strong>admitted</strong> before you can create an
              offer. Mark an application as admitted first.
            </p>
            <Link to="/applications">
              <Button className="bg-primary hover:bg-primary/90 text-primary-foreground text-sm font-semibold">
                Go to Applications
              </Button>
            </Link>
          </div>
        ) : (
          <>
            <div>
              <label className={labelCls}>Admitted application</label>
              <select value={appId} onChange={(e) => setAppId(e.target.value)} className={inputCls}>
                <option value="">Select an application…</option>
                {admittedApps.map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.university_name} — {a.program_name ?? "Program"}
                  </option>
                ))}
              </select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className={labelCls}>Offer date</label>
                <input
                  type="date"
                  value={offerDate}
                  onChange={(e) => setOfferDate(e.target.value)}
                  className={inputCls}
                />
              </div>
              <div>
                <label className={labelCls}>Response deadline</label>
                <input
                  type="date"
                  value={deadline}
                  onChange={(e) => setDeadline(e.target.value)}
                  className={inputCls}
                />
              </div>
              <div>
                <label className={labelCls}>Deposit amount</label>
                <input
                  type="number"
                  value={deposit}
                  onChange={(e) => setDeposit(e.target.value)}
                  className={inputCls}
                />
              </div>
              <div>
                <label className={labelCls}>Deposit deadline</label>
                <input
                  type="date"
                  value={depositDeadline}
                  onChange={(e) => setDepositDeadline(e.target.value)}
                  className={inputCls}
                />
              </div>
            </div>
            <div>
              <label className={labelCls}>Currency</label>
              <input
                value={currency}
                onChange={(e) => setCurrency(e.target.value)}
                className={inputCls}
              />
            </div>
            <div>
              <label className={labelCls}>Conditions of admission</label>
              <textarea
                value={conditions}
                onChange={(e) => setConditions(e.target.value)}
                placeholder="e.g. Final grades meeting offer conditions"
                className={`${inputCls} h-20 py-2`}
              />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" onClick={onClose} className="text-sm">
                Cancel
              </Button>
              <Button
                onClick={submit}
                disabled={saving}
                className="bg-primary hover:bg-primary/90 text-primary-foreground text-sm font-semibold"
              >
                {saving ? "Saving…" : "Create offer"}
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
