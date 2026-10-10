import { useState } from "react";
import { useServerFn } from "@tanstack/react-start";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { GraduationCap } from "lucide-react";
import { Button } from "../ui/button";
import { recordEnrollmentDecision } from "../../lib/offer-vault.functions";
import type { StudentEnrollmentDecision } from "../../lib/offer-vault.types";
import { ENROLLMENT_DECISIONS } from "../../lib/offer-vault.types";
import { SectionCard, inputCls, labelCls } from "./shared";

export function EnrollmentSection({
  offerId,
  currency,
  enrollment,
  onMutated,
}: {
  offerId: string;
  currency: string;
  enrollment: StudentEnrollmentDecision | null;
  onMutated: () => void;
}) {
  const recordFn = useServerFn(recordEnrollmentDecision);
  const [decision, setDecision] = useState<StudentEnrollmentDecision["decision"]>(
    enrollment?.decision ?? "accepted",
  );
  const [term, setTerm] = useState(enrollment?.enrollment_term ?? "");
  const [finalAward, setFinalAward] = useState(
    enrollment?.final_award_accepted != null ? String(enrollment.final_award_accepted) : "",
  );
  const [efc, setEfc] = useState(
    enrollment?.expected_first_year_family_contribution != null
      ? String(enrollment.expected_first_year_family_contribution)
      : "",
  );

  const mut = useMutation({
    mutationFn: () =>
      recordFn({
        data: {
          offer_id: offerId,
          decision,
          enrollment_term: term || null,
          final_award_accepted: finalAward ? Number(finalAward) : null,
          expected_first_year_family_contribution: efc ? Number(efc) : null,
        },
      }),
    onSuccess: () => {
      onMutated();
      toast.success("Enrollment decision recorded.");
    },
    onError: (e: Error) => toast.error(e.message || "Could not record decision."),
  });

  return (
    <SectionCard
      title="Enrollment decision"
      subtitle="Record your decision after the response deadline. Supports future outcome tracking."
    >
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className={labelCls}>Decision</label>
          <select
            value={decision}
            onChange={(e) => setDecision(e.target.value as StudentEnrollmentDecision["decision"])}
            className={inputCls}
          >
            {ENROLLMENT_DECISIONS.map((d) => (
              <option key={d} value={d}>
                {d.replace(/_/g, " ")}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className={labelCls}>Enrollment term</label>
          <input
            value={term}
            onChange={(e) => setTerm(e.target.value)}
            placeholder="e.g. Fall 2026"
            className={inputCls}
          />
        </div>
        <div>
          <label className={labelCls}>Final award accepted ({currency})</label>
          <input
            value={finalAward}
            onChange={(e) => setFinalAward(e.target.value)}
            type="number"
            className={inputCls}
          />
        </div>
        <div>
          <label className={labelCls}>Expected first-year family contribution ({currency})</label>
          <input
            value={efc}
            onChange={(e) => setEfc(e.target.value)}
            type="number"
            className={inputCls}
          />
        </div>
      </div>
      <div className="flex justify-end">
        <Button
          onClick={() => mut.mutate()}
          disabled={mut.isPending}
          className="bg-primary hover:bg-primary/90 text-primary-foreground text-sm font-semibold flex items-center gap-1.5"
        >
          <GraduationCap className="w-4 h-4" />
          {mut.isPending ? "Saving…" : enrollment ? "Update decision" : "Record decision"}
        </Button>
      </div>
    </SectionCard>
  );
}
