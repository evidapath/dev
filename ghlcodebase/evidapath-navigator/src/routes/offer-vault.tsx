import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { useServerFn } from "@tanstack/react-start";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Vault, Plus, Scale, ShieldCheck, Inbox } from "lucide-react";
import { requireAuth } from "../lib/route-guard";
import { Button } from "../components/ui/button";
import { listOfferComposites, deleteOffer } from "../lib/offer-vault.functions";
import {
  EmptyState,
  IllustrativePreviewLabel,
  PendingData,
  VerificationBadge,
} from "../components/offer-vault/shared";
import { OfferDetail, AddOfferDialog } from "../components/offer-vault/OfferDetail";

export const Route = createFileRoute("/offer-vault")({
  head: () => ({
    meta: [
      { title: "Offer Vault — EvidaPath" },
      {
        name: "description",
        content:
          "Store admission and scholarship offers, verify awards, and see what each offer means for your family financially.",
      },
      { property: "og:title", content: "Offer Vault — EvidaPath" },
      { property: "og:description", content: "Upload your offer and see your real family cost." },
    ],
  }),
  beforeLoad: ({ context, location }) => requireAuth(context, location.pathname),
  component: OfferVaultPage,
});

function OfferVaultPage() {
  const qc = useQueryClient();
  const listFn = useServerFn(listOfferComposites);
  const deleteOfferFn = useServerFn(deleteOffer);

  const { data: composites = [], isLoading } = useQuery({
    queryKey: ["offer-composites"],
    queryFn: () => listFn(),
  });

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [addingOffer, setAddingOffer] = useState(false);

  // Child components dispatch this event when they mutate; refetch + bubble up.
  useEffect(() => {
    const handler = () => {
      qc.invalidateQueries({ queryKey: ["offer-composites"] });
      qc.invalidateQueries({ queryKey: ["verified-awards"] });
    };
    window.addEventListener("offer-vault-mutated", handler);
    return () => window.removeEventListener("offer-vault-mutated", handler);
  }, [qc]);

  const selected = useMemo(
    () => composites.find((c) => c.offer.id === selectedId) ?? composites[0] ?? null,
    [composites, selectedId],
  );

  const deleteOfferMut = useMutation({
    mutationFn: (id: string) => deleteOfferFn({ data: { id } }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["offer-composites"] });
      qc.invalidateQueries({ queryKey: ["verified-awards"] });
      setSelectedId(null);
      toast.success("Offer removed.");
    },
    onError: (e: Error) => toast.error(e.message || "Could not remove offer."),
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <div className="max-w-3xl space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold">
          <Vault className="w-3.5 h-3.5" />
          <span>My EvidaPath • Offer Vault</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-display font-extrabold text-foreground">
          Offer Vault
        </h1>
        <p className="text-sm sm:text-base text-muted-foreground leading-relaxed">
          Upload your offer and EvidaPath will tell you what it actually means financially. Store
          admission offers, scholarship awards, and aid packages — then watch your real family cost
          and funding gap update.
        </p>
        <IllustrativePreviewLabel text="Private to your account. Offer, award, and document records are stored under Row Level Security. Uploaded documents are private — no public URLs." />
      </div>

      <div className="flex items-center justify-between flex-wrap gap-3">
        <h2 className="font-display font-bold text-lg text-foreground">Your offers</h2>
        <div className="flex items-center gap-2">
          <Link to="/compare-offers">
            <Button
              variant="outline"
              size="sm"
              className="text-xs font-semibold flex items-center gap-1.5"
            >
              <Scale className="w-3.5 h-3.5" /> Compare Offers
            </Button>
          </Link>
          <Button
            onClick={() => setAddingOffer(true)}
            className="bg-primary hover:bg-primary/90 text-primary-foreground text-sm font-semibold flex items-center gap-1.5"
          >
            <Plus className="w-4 h-4" /> Add Offer
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="text-sm text-muted-foreground">Loading your offers…</div>
      ) : composites.length === 0 && !addingOffer ? (
        <EmptyState
          icon={Inbox}
          title="No offers yet"
          description="Once you receive an admission or scholarship letter, add it here and EvidaPath will calculate what the offer means for your family."
          action={
            <Button
              onClick={() => setAddingOffer(true)}
              className="bg-primary hover:bg-primary/90 text-primary-foreground text-sm font-semibold mt-2"
            >
              <Plus className="w-4 h-4" /> Add your first offer
            </Button>
          }
        />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 space-y-3">
            {composites.map((c) => {
              const isActive = (selected?.offer.id ?? null) === c.offer.id;
              return (
                <button
                  key={c.offer.id}
                  onClick={() => setSelectedId(c.offer.id)}
                  className={`w-full text-left rounded-2xl border p-4 transition-all ${
                    isActive
                      ? "border-primary/50 bg-primary/5 shadow-xs"
                      : "border-border bg-card hover:border-primary/30"
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <h3 className="font-display font-bold text-sm text-foreground truncate">
                      {c.application.university_name}
                    </h3>
                    <VerificationBadge level={c.offer.verification_level} />
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {c.application.program_name ?? "Program not specified"}
                  </p>
                  <div className="mt-2 flex items-center justify-between">
                    <span className="text-[11px] text-muted-foreground">
                      Net annual family cost
                    </span>
                    <span className="font-mono text-xs font-bold text-foreground">
                      {c.analysis.netAnnualFamilyCost != null ? (
                        `$${c.analysis.netAnnualFamilyCost.toLocaleString()}`
                      ) : (
                        <PendingData label="Pending" />
                      )}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>

          <div className="lg:col-span-2">
            {selected ? (
              <OfferDetail
                composite={selected}
                onDelete={() => deleteOfferMut.mutate(selected.offer.id)}
              />
            ) : (
              <div className="text-sm text-muted-foreground text-center py-20">
                Select an offer to view its analysis.
              </div>
            )}
          </div>
        </div>
      )}

      {addingOffer && (
        <AddOfferDialog
          onClose={() => setAddingOffer(false)}
          onCreated={(id) => {
            setAddingOffer(false);
            setSelectedId(id);
            qc.invalidateQueries({ queryKey: ["offer-composites"] });
          }}
        />
      )}

      <div className="flex items-center gap-2 text-[11px] text-muted-foreground border-t border-border pt-6">
        <ShieldCheck className="w-3.5 h-3.5 text-primary shrink-0" />
        <span>
          Offer Vault data is accessed only through your authenticated session and is subject to Row
          Level Security. Uploaded documents are stored privately with signed-URL access only.
        </span>
      </div>
    </div>
  );
}
