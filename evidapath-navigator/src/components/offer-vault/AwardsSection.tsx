import { useState } from "react";
import { useServerFn } from "@tanstack/react-start";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { Plus, Trash2, Pencil, Award, X } from "lucide-react";
import { Button } from "../ui/button";
import { upsertAward, deleteAward, setAwardVerification } from "../../lib/offer-vault.functions";
import type {
  StudentAward,
  VerificationLevel,
  AwardType,
  AwardFrequency,
} from "../../lib/offer-vault.types";
import { AWARD_TYPES, AWARD_FREQUENCIES } from "../../lib/offer-vault.types";
import { VerificationBadge, SectionCard, inputCls, labelCls } from "./shared";

export function AwardsSection({
  offerId,
  currency,
  awards,
  onMutated,
}: {
  offerId: string;
  currency: string;
  awards: StudentAward[];
  onMutated: () => void;
}) {
  const upsertAwardFn = useServerFn(upsertAward);
  const deleteAwardFn = useServerFn(deleteAward);
  const setVerFn = useServerFn(setAwardVerification);
  const [editing, setEditing] = useState<Partial<StudentAward> | null>(null);

  const saveMut = useMutation({
    mutationFn: (input: Partial<StudentAward>) => upsertAwardFn({ data: input }),
    onSuccess: () => {
      onMutated();
      setEditing(null);
      toast.success("Award saved.");
    },
    onError: (e: Error) => toast.error(e.message || "Could not save award."),
  });

  const delMut = useMutation({
    mutationFn: (id: string) => deleteAwardFn({ data: { id } }),
    onSuccess: () => {
      onMutated();
      toast.success("Award removed.");
    },
    onError: (e: Error) => toast.error(e.message || "Could not remove award."),
  });

  const verMut = useMutation({
    mutationFn: ({ id, level }: { id: string; level: VerificationLevel }) =>
      setVerFn({ data: { id, level } }),
    onSuccess: () => onMutated(),
    onError: (e: Error) => toast.error(e.message || "Could not update verification."),
  });

  return (
    <SectionCard
      title="Scholarships, grants & aid"
      subtitle="Add your scholarship award to update your funding gap. Multiple awards per offer."
      action={
        <Button
          onClick={() =>
            setEditing({
              offer_id: offerId,
              award_type: "scholarship",
              frequency: "annual_renewable",
              currency,
              verification_level: "self_reported",
            })
          }
          size="sm"
          className="bg-primary hover:bg-primary/90 text-primary-foreground text-xs font-semibold flex items-center gap-1.5"
        >
          <Plus className="w-3.5 h-3.5" /> Add award
        </Button>
      }
    >
      {awards.length === 0 ? (
        <p className="text-xs text-muted-foreground py-4 text-center">
          No awards yet. Add a scholarship or aid package to see your net family cost update.
        </p>
      ) : (
        <div className="space-y-3">
          {awards.map((a) => (
            <div
              key={a.id}
              className="rounded-xl border border-border p-4 flex flex-col sm:flex-row sm:items-start justify-between gap-3"
            >
              <div className="space-y-1.5">
                <div className="flex items-center gap-2 flex-wrap">
                  <Award className="w-3.5 h-3.5 text-primary" />
                  <span className="font-display font-bold text-sm text-foreground">
                    {a.award_name}
                  </span>
                  <span className="text-[10px] uppercase font-semibold px-1.5 py-0.5 rounded bg-secondary text-muted-foreground">
                    {a.award_type.replace(/_/g, " ")}
                  </span>
                  <VerificationBadge level={a.verification_level} />
                </div>
                <div className="text-xs text-muted-foreground space-y-0.5">
                  <div>
                    Amount:{" "}
                    <span className="font-mono text-foreground">
                      {a.amount != null ? `$${a.amount.toLocaleString()} ${a.currency}` : "—"}
                    </span>{" "}
                    • {a.frequency.replace(/_/g, " ")}
                    {a.duration_years ? ` • ${a.duration_years} yrs` : ""}
                  </div>
                  {a.need_vs_merit && a.need_vs_merit !== "unspecified" && (
                    <div>Need vs merit: {a.need_vs_merit.replace(/_/g, " ")}</div>
                  )}
                  {a.renewal_criteria && <div>Renewal: {a.renewal_criteria}</div>}
                  {a.min_gpa != null && <div>Min GPA: {a.min_gpa}</div>}
                </div>
              </div>
              <div className="flex items-center gap-1 shrink-0">
                {a.verification_level === "self_reported" && (
                  <button
                    onClick={() => verMut.mutate({ id: a.id, level: "document_verified" })}
                    className="text-[10px] font-semibold text-primary px-2 py-1 rounded hover:bg-primary/10"
                    title="Mark document-verified after uploading a supporting letter"
                  >
                    Mark verified
                  </button>
                )}
                <button
                  onClick={() => setEditing(a)}
                  className="p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-secondary"
                >
                  <Pencil className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => delMut.mutate(a.id)}
                  className="p-1.5 rounded-lg text-muted-foreground hover:text-destructive hover:bg-destructive/10"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {editing && (
        <AwardEditor
          initial={editing}
          currency={currency}
          onClose={() => setEditing(null)}
          onSave={(input) => saveMut.mutate(input)}
          saving={saveMut.isPending}
        />
      )}
    </SectionCard>
  );
}

function AwardEditor({
  initial,
  currency,
  onClose,
  onSave,
  saving,
}: {
  initial: Partial<StudentAward>;
  currency: string;
  onClose: () => void;
  onSave: (input: Partial<StudentAward>) => void;
  saving: boolean;
}) {
  const [name, setName] = useState(initial.award_name ?? "");
  const [type, setType] = useState<AwardType>((initial.award_type as AwardType) ?? "scholarship");
  const [amount, setAmount] = useState(initial.amount != null ? String(initial.amount) : "");
  const [cur, setCur] = useState(initial.currency ?? currency);
  const [frequency, setFrequency] = useState<AwardFrequency>(
    (initial.frequency as AwardFrequency) ?? "annual_renewable",
  );
  const [duration, setDuration] = useState(
    initial.duration_years != null ? String(initial.duration_years) : "",
  );
  const [renewal, setRenewal] = useState(initial.renewal_criteria ?? "");
  const [minGpa, setMinGpa] = useState(initial.min_gpa != null ? String(initial.min_gpa) : "");
  const [needMerit, setNeedMerit] = useState(initial.need_vs_merit ?? "unspecified");

  const submit = () => {
    if (!name.trim()) {
      toast.error("Award name is required.");
      return;
    }
    onSave({
      id: initial.id,
      offer_id: initial.offer_id,
      award_name: name,
      award_type: type,
      amount: amount ? Number(amount) : null,
      currency: cur,
      frequency,
      duration_years: duration ? Number(duration) : null,
      renewal_criteria: renewal || null,
      min_gpa: minGpa ? Number(minGpa) : null,
      need_vs_merit: needMerit as StudentAward["need_vs_merit"],
      verification_level: initial.verification_level ?? "self_reported",
    });
  };

  return (
    <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-card border border-border rounded-2xl shadow-xl w-full max-w-lg p-6 space-y-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between">
          <h3 className="font-display font-bold text-lg text-foreground">
            {initial.id ? "Edit award" : "Add award"}
          </h3>
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-muted-foreground hover:bg-secondary"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div>
          <label className={labelCls}>Award name</label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. Merit Excellence Award"
            className={inputCls}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Type</label>
            <select
              value={type}
              onChange={(e) => setType(e.target.value as AwardType)}
              className={inputCls}
            >
              {AWARD_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t.replace(/_/g, " ")}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelCls}>Need vs merit</label>
            <select
              value={needMerit}
              onChange={(e) => setNeedMerit(e.target.value)}
              className={inputCls}
            >
              <option value="unspecified">Unspecified</option>
              <option value="need_based">Need-based</option>
              <option value="merit_based">Merit-based</option>
              <option value="hybrid">Hybrid</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Amount</label>
            <input
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              type="number"
              placeholder="0"
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Currency</label>
            <input value={cur} onChange={(e) => setCur(e.target.value)} className={inputCls} />
          </div>
          <div>
            <label className={labelCls}>Frequency</label>
            <select
              value={frequency}
              onChange={(e) => setFrequency(e.target.value as AwardFrequency)}
              className={inputCls}
            >
              {AWARD_FREQUENCIES.map((f) => (
                <option key={f} value={f}>
                  {f.replace(/_/g, " ")}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Duration (years)</label>
            <input
              value={duration}
              onChange={(e) => setDuration(e.target.value)}
              type="number"
              placeholder="e.g. 4"
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Min GPA</label>
            <input
              value={minGpa}
              onChange={(e) => setMinGpa(e.target.value)}
              type="number"
              step="0.1"
              placeholder="e.g. 3.5"
              className={inputCls}
            />
          </div>
        </div>

        <div>
          <label className={labelCls}>Renewal criteria</label>
          <textarea
            value={renewal}
            onChange={(e) => setRenewal(e.target.value)}
            placeholder="e.g. Maintain 3.0 GPA, full-time enrollment"
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
            {saving ? "Saving…" : "Save award"}
          </Button>
        </div>
      </div>
    </div>
  );
}
