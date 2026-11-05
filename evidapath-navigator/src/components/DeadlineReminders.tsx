import { BellRing, CalendarPlus } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { useAuth } from "./AuthContext";
import { submitGhlForm } from "../lib/ghl";
import { downloadIcs, type CalendarItem } from "../lib/ics";
import { fmtDate } from "../lib/decision-engine";

/**
 * Turn on once the GHL "Deadline Reminders" workflow is set up (see
 * docs/deadline-reminders-ghl.md). Until then only the calendar file is offered,
 * so nobody is told they'll get emails that aren't being sent.
 */
export const EMAIL_REMINDERS_LIVE = false;

const OPT_KEY = "evidapath.reminders";
const SENT_KEY = "evidapath.reminders.sent";

function read(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}
function write(key: string, v: string | null) {
  try {
    if (v == null) localStorage.removeItem(key);
    else localStorage.setItem(key, v);
  } catch {
    /* storage unavailable */
  }
}

/**
 * Two ways not to miss a deadline:
 *  - a calendar file with alerts 14, 3 and 1 day before (works right away);
 *  - email reminders: an opt-in that sends the student's next deadlines to the
 *    EvidaPath team's CRM (GHL "Deadline Reminders" form), where a workflow
 *    emails them before each date. Re-sent only when the deadlines change.
 */
export function DeadlineReminders({ items }: { items: CalendarItem[] }) {
  const { user } = useAuth();
  const [on, setOn] = useState(false);
  useEffect(() => setOn(read(OPT_KEY) === user?.email && !!user?.email), [user]);

  const upcoming = items.slice(0, 5);
  const sig = upcoming.map((i) => `${i.id}@${i.date}`).join("|");

  const send = (optIn: boolean) => {
    if (!user?.email) return Promise.reject(new Error("Not signed in"));
    const fields: Record<string, { label: string; value: string }> = {
      email: { label: "Email Address", value: user.email },
      reminders_opt_in: { label: "Deadline reminders", value: optIn ? "yes" : "no" },
    };
    if (optIn)
      upcoming.forEach((i, n) => {
        fields[`deadline_${n + 1}_date`] = { label: `Deadline ${n + 1} date`, value: i.date };
        fields[`deadline_${n + 1}_label`] = {
          label: `Deadline ${n + 1}`,
          value: `${i.uni}: ${i.title}`,
        };
      });
    return submitGhlForm("deadline-reminders", "Deadline Reminders", fields);
  };

  // Keep the CRM's dates current: re-send when the next deadlines change.
  useEffect(() => {
    if (!EMAIL_REMINDERS_LIVE || !on || !sig || read(SENT_KEY) === sig) return;
    send(true)
      .then(() => write(SENT_KEY, sig))
      .catch((err: Error) => console.error("[reminders] update failed:", err));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [on, sig]);

  const toggle = () => {
    if (!user?.email) {
      toast("Sign in to get email reminders.");
      return;
    }
    const next = !on;
    send(next)
      .then(() => {
        setOn(next);
        write(OPT_KEY, next ? user.email! : null);
        write(SENT_KEY, next ? sig : null);
        toast.success(
          next ? `We'll email ${user.email} before your deadlines.` : "Email reminders turned off.",
        );
      })
      .catch((err: Error) => {
        console.error("[reminders] toggle failed:", err);
        toast.error("Couldn't update reminders — please try again.");
      });
  };

  if (items.length === 0) return null;

  return (
    <div className="rounded-2xl border border-primary/20 bg-primary/5 p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div className="space-y-0.5">
        <p className="font-semibold text-sm text-foreground flex items-center gap-1.5">
          <BellRing className="w-4 h-4 text-primary" />
          Don't miss a deadline
        </p>
        <p className="text-xs text-muted-foreground">
          Next: {items[0]!.uni}, {fmtDate(items[0]!.date)}. Get reminders 14, 3 and 1 day before
          each one.
        </p>
      </div>
      <div className="flex flex-wrap gap-2 shrink-0">
        <button
          onClick={() => downloadIcs(items)}
          className="inline-flex items-center gap-1.5 h-9 px-3 rounded-lg border border-border bg-card text-xs font-semibold text-foreground hover:bg-secondary"
        >
          <CalendarPlus className="w-3.5 h-3.5" />
          Add to my calendar
        </button>
        {EMAIL_REMINDERS_LIVE && (
          <button
            onClick={toggle}
            aria-pressed={on}
            className={`inline-flex items-center gap-1.5 h-9 px-3 rounded-lg text-xs font-semibold ${
              on
                ? "bg-primary/15 text-primary border border-primary/30"
                : "bg-primary text-primary-foreground hover:bg-primary/90"
            }`}
          >
            <BellRing className="w-3.5 h-3.5" />
            {on ? "Email reminders on ✓" : "Email me reminders"}
          </button>
        )}
      </div>
    </div>
  );
}
