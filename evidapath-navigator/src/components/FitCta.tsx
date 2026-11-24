import { Link } from "@tanstack/react-router";

// The next step for a visitor who arrives from a search: check their own fit.
export function FitCta() {
  return (
    <div className="rounded-2xl border border-primary/30 bg-primary/5 p-5 flex flex-col sm:flex-row sm:items-center gap-3 justify-between">
      <p className="text-sm text-foreground">
        <span className="font-semibold">Which of these fit your grades and budget?</span> Answer 4
        questions and see the universities that match, with the same sourced figures. No sign-in
        needed.
      </p>
      <Link
        to="/find-my-path"
        className="inline-flex min-h-11 items-center justify-center rounded-xl bg-primary px-5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 shrink-0"
      >
        Find My Path
      </Link>
    </div>
  );
}
