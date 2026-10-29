import { useState } from "react";
import { CheckCircle2, MessageCircle } from "lucide-react";
import { toast } from "sonner";
import { Button } from "./ui/button";
import { inputCls, labelCls } from "./offer-vault/shared";
import { submitGhlForm } from "../lib/ghl";

// Counseling waitlist. Submits to GHL (contact + Activity entry) and only shows
// "You're on the list" after GHL confirms receipt. The student's shortlist is
// attached so a counselor sees it without asking.

const INTAKES = ["Sept 2027", "Jan / Feb 2028", "Sept 2028", "Later / not sure"];

export function CounselingWaitlist({
  defaultEmail,
  shortlist = [],
  source,
}: {
  defaultEmail?: string | undefined;
  shortlist?: string[];
  source: string;
}) {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState(defaultEmail ?? "");
  const [phone, setPhone] = useState("");
  const [intake, setIntake] = useState<string>(INTAKES[0] ?? "");
  const [help, setHelp] = useState("");
  const [sending, setSending] = useState(false);
  const [done, setDone] = useState(false);

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    setSending(true);
    submitGhlForm("counseling-waitlist", "Counseling Waitlist", {
      first_name: { label: "First Name", value: firstName },
      last_name: { label: "Last Name", value: lastName },
      email: { label: "Email Address", value: email },
      phone: { label: "Phone / WhatsApp", value: phone },
      target_intake: { label: "Target Intake", value: intake },
      help_needed: { label: "What They Need Help With", value: help },
      shortlist: { label: "Saved Universities", value: shortlist.join("; ") },
      waitlist_source: { label: "Joined From", value: source },
    })
      .then(() => setDone(true))
      .catch((err: Error) => {
        console.error("[counseling-waitlist] GHL submit failed:", err);
        toast.error("Could not join the waitlist — please check your connection and try again.");
      })
      .finally(() => setSending(false));
  };

  if (done) {
    return (
      <div className="rounded-2xl border border-primary/30 bg-primary/5 p-6 flex items-start gap-3">
        <CheckCircle2 className="w-5 h-5 text-primary shrink-0 mt-0.5" />
        <div className="space-y-1">
          <p className="font-semibold text-sm text-foreground">
            You're on the counseling waitlist.
          </p>
          <p className="text-xs text-muted-foreground">
            The EvidaPath team will be in touch at {email}.
          </p>
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={submit} className="rounded-2xl border border-border bg-card p-6 space-y-4">
      <div className="flex items-start gap-3">
        <MessageCircle className="w-5 h-5 text-primary shrink-0 mt-0.5" />
        <div className="space-y-1">
          <h3 className="font-display font-bold text-base text-foreground">
            Talk to a counselor about your options
          </h3>
          <p className="text-xs text-muted-foreground">
            Join the waitlist for one-to-one counseling.
            {shortlist.length > 0 &&
              ` Your ${shortlist.length} saved universit${shortlist.length === 1 ? "y is" : "ies are"} shared with the counselor so you don't have to repeat yourself.`}
          </p>
        </div>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
          <label className={labelCls} htmlFor="wl-first">
            First name
          </label>
          <input
            id="wl-first"
            required
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
            className={inputCls}
          />
        </div>
        <div>
          <label className={labelCls} htmlFor="wl-last">
            Last name
          </label>
          <input
            id="wl-last"
            required
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
            className={inputCls}
          />
        </div>
        <div>
          <label className={labelCls} htmlFor="wl-email">
            Email
          </label>
          <input
            id="wl-email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className={inputCls}
          />
        </div>
        <div>
          <label className={labelCls} htmlFor="wl-phone">
            Phone / WhatsApp (optional)
          </label>
          <input
            id="wl-phone"
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="+971 …"
            className={inputCls}
          />
        </div>
        <div>
          <label className={labelCls} htmlFor="wl-intake">
            Target intake
          </label>
          <select
            id="wl-intake"
            value={intake}
            onChange={(e) => setIntake(e.target.value)}
            className={inputCls}
          >
            {INTAKES.map((i) => (
              <option key={i}>{i}</option>
            ))}
          </select>
        </div>
        <div className="sm:col-span-2">
          <label className={labelCls} htmlFor="wl-help">
            What do you need help with? (optional)
          </label>
          <textarea
            id="wl-help"
            rows={2}
            maxLength={1000}
            value={help}
            onChange={(e) => setHelp(e.target.value)}
            placeholder="e.g. Choosing between UK and Netherlands, scholarship options"
            className={inputCls}
          />
        </div>
      </div>
      <Button type="submit" disabled={sending} className="text-sm">
        {sending ? "Joining…" : "Join the counseling waitlist"}
      </Button>
    </form>
  );
}
