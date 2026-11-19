import { useEffect, useState } from "react";
import { Link } from "@tanstack/react-router";
import { CheckCircle2, PlusCircle } from "lucide-react";
import { toast } from "sonner";
import { Button } from "./ui/button";
import { inputCls, labelCls } from "./offer-vault/shared";
import { submitGhlForm } from "../lib/ghl";
import { useAuth } from "./AuthContext";

// "Missing a university or course?" Students tell the EvidaPath team which universities and
// courses to add next. Sent to GHL like the counseling waitlist; success is shown only after GHL
// confirms receipt. The email lets the team say when the course is added.

export function RequestUniversity({
  source,
  defaultUniversity = "",
}: {
  source: string;
  defaultUniversity?: string;
}) {
  const { user } = useAuth();
  const [university, setUniversity] = useState(defaultUniversity);
  const [country, setCountry] = useState("");
  const [courses, setCourses] = useState("");
  const [email, setEmail] = useState(user?.email ?? "");
  const [sending, setSending] = useState(false);
  const [done, setDone] = useState(false);

  // Follow the search box until the student types here themselves.
  const [touched, setTouched] = useState(false);
  useEffect(() => {
    if (!touched) setUniversity(defaultUniversity);
  }, [defaultUniversity, touched]);
  useEffect(() => {
    if (user?.email && !email) setEmail(user.email);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    setSending(true);
    submitGhlForm("course-request", "University / Course Request", {
      email: { label: "Email Address", value: email },
      requested_university: { label: "Requested University", value: university },
      requested_country: { label: "Country", value: country },
      requested_courses: { label: "Requested Course(s)", value: courses },
      request_source: { label: "Requested From", value: source },
    })
      .then(() => setDone(true))
      .catch((err: Error) => {
        console.error("[course-request] GHL submit failed:", err);
        toast.error("Could not send your request. Please check your connection and try again.");
      })
      .finally(() => setSending(false));
  };

  if (done) {
    return (
      <div className="rounded-2xl border border-primary/30 bg-primary/5 p-6 flex items-start gap-3">
        <CheckCircle2 className="w-5 h-5 text-primary shrink-0 mt-0.5" />
        <div className="space-y-1">
          <p className="font-semibold text-sm text-foreground">Thanks, request received.</p>
          <p className="text-xs text-muted-foreground">
            We add a course only after checking its fees and entry requirements on the university's
            own website. We'll email {email} when it's on EvidaPath.
          </p>
          <button
            type="button"
            onClick={() => {
              setDone(false);
              setTouched(true);
              setUniversity("");
              setCountry("");
              setCourses("");
            }}
            className="text-xs font-semibold text-primary hover:underline"
          >
            Request another
          </button>
        </div>
      </div>
    );
  }

  return (
    <form
      id="request-university"
      onSubmit={submit}
      className="scroll-mt-24 rounded-2xl border border-border bg-card p-6 space-y-4"
    >
      <div className="flex items-start gap-3">
        <PlusCircle className="w-5 h-5 text-primary shrink-0 mt-0.5" />
        <div className="space-y-1">
          <h3 className="font-display font-bold text-base text-foreground">
            Can't find your university or course?
          </h3>
          <p className="text-xs text-muted-foreground">
            We're still adding universities. Tell us which ones you're considering and we'll
            prioritise them.
          </p>
        </div>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
          <label className={labelCls} htmlFor="rq-uni">
            University
          </label>
          <input
            id="rq-uni"
            required
            maxLength={200}
            value={university}
            onChange={(e) => {
              setTouched(true);
              setUniversity(e.target.value);
            }}
            placeholder="e.g. University of Edinburgh"
            className={inputCls}
          />
        </div>
        <div>
          <label className={labelCls} htmlFor="rq-country">
            Country (optional)
          </label>
          <input
            id="rq-country"
            maxLength={100}
            value={country}
            onChange={(e) => setCountry(e.target.value)}
            placeholder="e.g. United Kingdom"
            className={inputCls}
          />
        </div>
        <div className="sm:col-span-2">
          <label className={labelCls} htmlFor="rq-courses">
            Course(s)
          </label>
          <input
            id="rq-courses"
            required
            maxLength={500}
            value={courses}
            onChange={(e) => setCourses(e.target.value)}
            placeholder="e.g. Psychology, Economics"
            className={inputCls}
          />
        </div>
        <div className="sm:col-span-2">
          <label className={labelCls} htmlFor="rq-email">
            Email (so we can tell you when it's added)
          </label>
          <input
            id="rq-email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className={inputCls}
          />
        </div>
      </div>
      <Button type="submit" disabled={sending} className="text-sm">
        {sending ? "Sending…" : "Request it"}
      </Button>
      <p className="text-[11px] text-muted-foreground">
        What you send goes to the EvidaPath team. We use it only to decide what to add and tell you
        when it's added. See our{" "}
        <Link to="/privacy" className="underline hover:text-foreground">
          Privacy Policy
        </Link>
        .
      </p>
    </form>
  );
}
