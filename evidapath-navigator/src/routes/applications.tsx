import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { useServerFn } from "@tanstack/react-start";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  ClipboardList,
  Plus,
  Trash2,
  Pencil,
  X,
  ArrowRight,
  ShieldCheck,
  Inbox,
} from "lucide-react";
import { requireAuth } from "../lib/route-guard";
import { Button } from "../components/ui/button";
import {
  listApplications,
  upsertApplication,
  deleteApplication,
} from "../lib/offer-vault.functions";
import { UNIVERSITIES_DATA } from "../lib/mock-data";
import type { ApplicationStatus, StudentApplication } from "../lib/offer-vault.types";
import { APPLICATION_STATUSES } from "../lib/offer-vault.types";
import {
  EmptyState,
  IllustrativePreviewLabel,
  SectionCard,
  inputCls,
  labelCls,
} from "../components/offer-vault/shared";

export const Route = createFileRoute("/applications")({
  head: () => ({
    meta: [
      { title: "Applications — EvidaPath" },
      {
        name: "description",
        content:
          "Track the universities you're applying to and update the status as decisions arrive.",
      },
      { property: "og:title", content: "Applications — EvidaPath" },
      {
        property: "og:description",
        content: "Track university applications and admission decisions.",
      },
    ],
  }),
  beforeLoad: ({ context, location }) => requireAuth(context, location.pathname),
  component: ApplicationsPage,
});

const STATUS_STYLE: Record<ApplicationStatus, string> = {
  planning: "bg-secondary text-muted-foreground",
  started: "bg-secondary text-foreground",
  submitted: "bg-primary/10 text-primary",
  in_review: "bg-primary/10 text-primary",
  waitlisted: "bg-bronze/10 text-bronze",
  admitted: "bg-primary/15 text-primary",
  rejected: "bg-destructive/10 text-destructive",
  withdrawn: "bg-secondary text-muted-foreground",
};

function ApplicationsPage() {
  const qc = useQueryClient();
  const listFn = useServerFn(listApplications);
  const upsertFn = useServerFn(upsertApplication);
  const deleteFn = useServerFn(deleteApplication);

  const { data: applications = [] } = useQuery({
    queryKey: ["applications"],
    queryFn: () => listFn(),
  });

  const [editing, setEditing] = useState<Partial<StudentApplication> | null>(null);

  const upsertMut = useMutation({
    mutationFn: (input: Partial<StudentApplication>) => upsertFn({ data: input }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["applications"] });
      qc.invalidateQueries({ queryKey: ["offer-composites"] });
      qc.invalidateQueries({ queryKey: ["verified-awards"] });
      setEditing(null);
      toast.success("Application saved.");
    },
    onError: (e: Error) => toast.error(e.message || "Could not save application."),
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => deleteFn({ data: { id } }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["applications"] });
      qc.invalidateQueries({ queryKey: ["offer-composites"] });
      toast.success("Application removed.");
    },
    onError: (e: Error) => toast.error(e.message || "Could not remove application."),
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <div className="max-w-3xl space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold">
          <ClipboardList className="w-3.5 h-3.5" />
          <span>My EvidaPath • Applications</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-display font-extrabold text-foreground">
          Applications
        </h1>
        <p className="text-sm sm:text-base text-muted-foreground leading-relaxed">
          Track the universities you're applying to and update the status as decisions arrive. When
          you're admitted, create an offer in the Offer Vault to see what it actually means
          financially.
        </p>
        <IllustrativePreviewLabel text="Private to your account. Application records are stored under Row Level Security and visible only to you." />
      </div>

      <div className="flex items-center justify-between">
        <h2 className="font-display font-bold text-lg text-foreground">Your applications</h2>
        <Button
          onClick={() =>
            setEditing({
              sanity_university_id: UNIVERSITIES_DATA[0].id,
              university_name: UNIVERSITIES_DATA[0].name,
              status: "planning",
            })
          }
          className="bg-primary hover:bg-primary/90 text-primary-foreground text-sm font-semibold flex items-center gap-1.5"
        >
          <Plus className="w-4 h-4" /> Add Application
        </Button>
      </div>

      {applications.length === 0 && !editing && (
        <EmptyState
          icon={Inbox}
          title="No applications yet"
          description="Track the universities you're applying to and update the status as decisions arrive. Add your first application to begin."
          action={
            <Button
              onClick={() =>
                setEditing({
                  sanity_university_id: UNIVERSITIES_DATA[0].id,
                  university_name: UNIVERSITIES_DATA[0].name,
                  status: "planning",
                })
              }
              className="bg-primary hover:bg-primary/90 text-primary-foreground text-sm font-semibold mt-2"
            >
              <Plus className="w-4 h-4" /> Add your first application
            </Button>
          }
        />
      )}

      <div className="space-y-3">
        {applications.map((app) => (
          <SectionCard key={app.id}>
            <div className="flex flex-col sm:flex-row items-start justify-between gap-4">
              <div className="space-y-1.5">
                <div className="flex items-center gap-2 flex-wrap">
                  <h3 className="font-display font-bold text-base text-foreground">
                    {app.university_name}
                  </h3>
                  <span
                    className={`text-[10px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded ${STATUS_STYLE[app.status]}`}
                  >
                    {app.status.replace(/_/g, " ")}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground">
                  {app.program_name ?? "Program not specified"}
                  {app.application_cycle ? ` • ${app.application_cycle}` : ""}
                  {app.decision_plan ? ` • ${app.decision_plan}` : ""}
                </p>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                {app.status === "admitted" && (
                  <Link to="/offer-vault">
                    <Button
                      variant="outline"
                      size="sm"
                      className="text-xs font-semibold flex items-center gap-1.5"
                    >
                      Add offer <ArrowRight className="w-3 h-3" />
                    </Button>
                  </Link>
                )}
                <button
                  onClick={() => setEditing(app)}
                  className="p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors"
                  aria-label="Edit application"
                >
                  <Pencil className="w-4 h-4" />
                </button>
                <button
                  onClick={() => deleteMut.mutate(app.id)}
                  className="p-2 rounded-lg text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
                  aria-label="Delete application"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          </SectionCard>
        ))}
      </div>

      {editing && (
        <ApplicationEditor
          initial={editing}
          onClose={() => setEditing(null)}
          onSave={(input) => upsertMut.mutate(input)}
          saving={upsertMut.isPending}
        />
      )}

      <div className="flex items-center gap-2 text-[11px] text-muted-foreground border-t border-border pt-6">
        <ShieldCheck className="w-3.5 h-3.5 text-primary shrink-0" />
        <span>
          Your application data is accessed only through your authenticated session and is subject
          to Row Level Security. EvidaPath never uses the service-role key for student access.
        </span>
      </div>
    </div>
  );
}

function ApplicationEditor({
  initial,
  onClose,
  onSave,
  saving,
}: {
  initial: Partial<StudentApplication>;
  onClose: () => void;
  onSave: (input: Partial<StudentApplication>) => void;
  saving: boolean;
}) {
  const [univId, setUnivId] = useState(initial.sanity_university_id ?? UNIVERSITIES_DATA[0].id);
  const [programName, setProgramName] = useState(initial.program_name ?? "");
  const [cycle, setCycle] = useState(initial.application_cycle ?? "");
  const [decisionPlan, setDecisionPlan] = useState(initial.decision_plan ?? "");
  const [appDate, setAppDate] = useState(initial.application_date ?? "");
  const [status, setStatus] = useState<ApplicationStatus>(
    (initial.status as ApplicationStatus) ?? "planning",
  );

  const selectedUniv = UNIVERSITIES_DATA.find((u) => u.id === univId) ?? UNIVERSITIES_DATA[0];

  const submit = () => {
    onSave({
      id: initial.id,
      sanity_university_id: univId,
      university_name: selectedUniv.name,
      sanity_program_id: null,
      sanity_campus_id: null,
      program_name: programName || null,
      application_cycle: cycle || null,
      decision_plan: decisionPlan || null,
      application_date: appDate || null,
      status,
    });
  };

  return (
    <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-card border border-border rounded-2xl shadow-xl w-full max-w-lg p-6 space-y-5 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between">
          <h3 className="font-display font-bold text-lg text-foreground">
            {initial.id ? "Edit application" : "Add application"}
          </h3>
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-secondary"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div>
          <label className={labelCls}>University</label>
          <select value={univId} onChange={(e) => setUnivId(e.target.value)} className={inputCls}>
            {UNIVERSITIES_DATA.map((u) => (
              <option key={u.id} value={u.id}>
                {u.flag} {u.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className={labelCls}>Program / area of study</label>
          <input
            value={programName}
            onChange={(e) => setProgramName(e.target.value)}
            placeholder="e.g. Computer Science"
            className={inputCls}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Application cycle</label>
            <input
              value={cycle}
              onChange={(e) => setCycle(e.target.value)}
              placeholder="e.g. 2026 entry"
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Decision plan</label>
            <input
              value={decisionPlan}
              onChange={(e) => setDecisionPlan(e.target.value)}
              placeholder="e.g. Regular"
              className={inputCls}
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Application date</label>
            <input
              type="date"
              value={appDate ?? ""}
              onChange={(e) => setAppDate(e.target.value)}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Status</label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value as ApplicationStatus)}
              className={inputCls}
            >
              {APPLICATION_STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s.replace(/_/g, " ")}
                </option>
              ))}
            </select>
          </div>
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
            {saving ? "Saving…" : "Save application"}
          </Button>
        </div>
      </div>
    </div>
  );
}
