// Facts used by the legal pages (privacy, terms, cookies) and the sign-up age check.
// Every item here describes what the code actually does; when the code changes (a new
// form, a new provider, a new browser-storage key), update this file and the pages follow.
// Research, sources and open items: fact-checks/legal/2026-11-19-legal-review.md

export const LEGAL_UPDATED = "25 November 2026";
export const PRIVACY_EMAIL = "evidapath@gmail.com";

// EvidaPath isn't a registered company yet; it is run by its two founders. Replace this when
// a company is formed (name, registration number, registered address).
export const OPERATOR =
  "EvidaPath, a project run by its founders, Subhan and Suhail (not yet a registered company)";

// Placeholder: the founders haven't chosen the governing law yet (lawyer to decide).
export const GOVERNING_LAW: string | null = null;

/** Minimum age to create an account, and the age below which a parent must agree. */
export const MIN_AGE = 13;
export const ADULT_AGE = 18;

/** Services that receive personal data, what they get, and why. Matches the code. */
export const PROCESSORS = [
  {
    name: "Supabase",
    what: "Your account (email, sign-in), profile answers, saved universities, and Offer Vault records and uploaded documents.",
    why: "Database, sign-in and private file storage.",
    where: "Hosted in the United States (AWS us-east-1).",
  },
  {
    name: "HighLevel (LeadConnector)",
    what: "What you send in our forms (counseling waitlist, deadline reminders, university and course requests, feedback, parent agreement), and, for signed-in students who finish Find My Path, their email and answers.",
    why: "Our contact records, so the team can reply, add the universities you ask for and send the reminders you switch on.",
    where: "May be processed outside your country, including the United States.",
  },
  {
    name: "Anthropic (Claude API)",
    what: "Only when you ask for an AI fit check: your Find My Path answers (curriculum, grade band, subject, budget, citizenship, study languages) and the matching programmes. Not your name or email.",
    why: "Writes the AI fit explanation you asked for.",
    where: "May be processed outside your country, including the United States.",
  },
  {
    name: "Cloudflare",
    what: "Technical request data such as your IP address, browser and the pages you open. For visit statistics (Cloudflare Web Analytics): the pages viewed and the site that linked you here. Cloudflare states it uses no cookies or browser storage for this and doesn't fingerprint visitors.",
    why: "Hosting and security of the website, and counting visits so we know which pages help students and where visitors come from.",
    where: "Global network.",
  },
  {
    name: "Google (only if you choose Google sign-in)",
    what: "If you sign in with Google, Google confirms your email to us.",
    why: "Optional sign-in.",
    where: "May be processed outside your country, including the United States.",
  },
] as const;

/** Everything the site stores in your browser. Keys match the code. */
export const STORAGE = [
  {
    name: "sb-…-auth-token (cookie)",
    purpose: "Keeps you signed in. Set only when you sign in.",
    kind: "Strictly necessary",
    lasts: "Until you sign out or the session ends",
  },
  {
    name: "evidapath.pendingSaves",
    purpose: "Remembers universities you saved before signing in, so they move to your account.",
    kind: "Strictly necessary (your selections)",
    lasts: "Until moved to your account",
  },
  {
    name: "evidapath.qualification, evidapath.ukHome, evidapath.languages",
    purpose: "Remembers the qualification, UK-home-fee answer and study languages you chose.",
    kind: "Strictly necessary (your selections)",
    lasts: "Until you clear it",
  },
  {
    name: "evidapath.plan.done, evidapath.plan.university, evidapath.docs.done",
    purpose:
      "Remembers the plan steps and documents you ticked off, and the university you filtered by.",
    kind: "Strictly necessary (your selections)",
    lasts: "Until you clear it",
  },
  {
    name: "evidapath.reminders, evidapath.reminders.sent",
    purpose: "Remembers that you switched on deadline reminders and which dates were last sent.",
    kind: "Strictly necessary (your selections)",
    lasts: "Until you clear it",
  },
  {
    name: "evidapath-theme, evidapath.currency",
    purpose: "Remembers light or dark mode and the currency you chose to see prices in.",
    kind: "Preferences (site appearance)",
    lasts: "Until you clear it",
  },
  {
    name: "ep-feedback-prompt",
    purpose: "Remembers that you answered or closed the feedback survey, so it doesn't ask again.",
    kind: "Preferences (site appearance)",
    lasts: "180 days after sending, 60 days after closing",
  },
] as const;

/** Browser-storage keys a visitor can clear from the Cookies page (not the sign-in cookie). */
export const CLEARABLE_KEYS = [
  "evidapath.pendingSaves",
  "evidapath.qualification",
  "evidapath.ukHome",
  "evidapath.languages",
  "evidapath.plan.done",
  "evidapath.plan.university",
  "evidapath.docs.done",
  "evidapath.reminders",
  "evidapath.reminders.sent",
  "evidapath-theme",
  "evidapath.currency",
  "ep-feedback-prompt",
];
