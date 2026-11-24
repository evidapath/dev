# Legal pages and checks, 2026-11-19

What the site needed legally, what was built, what each part rests on, and what is still open.
Not legal advice: a lawyer should review the pages before EvidaPath relies on them, especially once
a company is formed.

## Sources read (primary, saved under `.research-cache/pages/`)

| Source | What it says that matters here |
|---|---|
| GDPR, EUR-Lex (Regulation (EU) 2016/679), Art. 8, 13, 17 | Art. 13 lists what a privacy notice must give "at the time when personal data are obtained": controller identity and contact, purposes and legal basis, legitimate interests, recipients, transfers, retention, rights, right to complain. Art. 8: child consent age 16, member states may lower it, "not below 13 years"; controller "shall make reasonable efforts to verify" parental consent. |
| UK GDPR Art. 8, legislation.gov.uk | UK age: "at least 13 years old". (UK DPA 2018 s.9 was omitted 31.12.2020; the age now sits in UK GDPR Art. 8.) |
| PECR reg. 6 and Schedule A1, legislation.gov.uk (amended 05/02/2026) | Storage on a device needs consent unless an exception applies. Para 4: strictly necessary, including "automatically authenticating the identity of the subscriber or user" and "maintaining a record of selections made on a website". Para 6: storage to adapt "the way the website appears or functions ... to the preferences of the subscriber or user" is allowed if the user gets clear information and "a simple means of objecting, free of charge". |
| ePrivacy Directive 2002/58/EC Art. 5(3), EUR-Lex consolidated 2009 | Consent needed except storage "strictly necessary in order for the provider of an information society service explicitly requested by the subscriber or user to provide the service". |
| California AG, CCPA page | Applies to for-profit businesses meeting one of: "gross annual revenue of over $25 million"; buy, sell or share data of "100,000 or more California residents or households"; or 50% of revenue from selling data. EvidaPath meets none: not applicable now. |
| Google Fonts privacy FAQ | "the Google Fonts API does not set or log cookies"; Google "receives the website visitor's IP address". |
| COPPA, 16 CFR Part 312 (eCFR) | Saved (`62e76febd71b`). Accounts are 13+, so COPPA's under-13 rules are avoided as long as under-13s are turned away at sign-up (they are). |

## Blocked (bot checks, not bypassed)

- ico.org.uk (Cloudflare "Performing security verification"): the ICO's cookie guidance and the
  Age Appropriate Design Code ("Children's code") could not be read. The site's choices for
  under-18s (no ads, no tracking, no profiling for marketing, minimum data) were made on our own
  judgment, not as a claim of compliance with the code.
- uaelegislation.gov.ae (Cloudflare "Sorry, you have been blocked"): UAE PDPL (Federal Decree-Law
  45/2021) not read.
- meity.gov.in ("Access Denied"): India's DPDP Act 2023 and DPDP Rules 2025 not read. Search
  results (leads only, not sources) say the Act requires verifiable parental consent for anyone
  under 18 and that Rule 10 starts on 13 May 2027. **To check from the official Gazette.** If true,
  the sign-up declaration below is not enough for Indian under-18s from that date.

## What the code actually does (checked in this task)

- Supabase project `evidapath`, region us-east-1. All 8 student tables cascade-delete with the
  auth user (`pg_constraint` confdeltype `c`), and the deletion code also removes the user's files
  in the private `student-documents` bucket. So Account → Delete removes everything in Supabase.
- GHL receives: counseling waitlist, deadline reminders, course requests, feedback, parent
  agreement, and the readiness lead (signed-in student's email and Find My Path answers, sent
  automatically on first completion). Deleting an account doesn't delete GHL records.
- Anthropic receives only the AI fit inputs (curriculum, grade band, subject, budget,
  citizenship, languages) and candidate programmes; nothing stored, errors log the status only.
- Browser storage: one Supabase auth cookie and 12 localStorage keys (listed on /cookies).
  No sessionStorage, no analytics, no ad tags. The shadcn sidebar cookie exists in code but the
  component isn't used.

## Built

- `/privacy`, `/terms`, `/cookies` (facts in `src/lib/legal.ts`), linked from the footer and the
  sitemap. Footer "Privacy"/"Terms" were dead text; now links, plus "Delete your data".
- Sign-up: age group required. Under 13: no account. 13-17: parent or guardian email (must differ
  from the student's) and a confirmation that they agreed; stored in the account's metadata
  (`age_group`, `terms_accepted_at`, `parent_email`, `parent_agreed_at`) and sent to GHL as
  "Parent / Guardian Agreement". 18+: agree to Terms and Privacy. Google sign-up gets the same
  check. Magic links no longer create accounts (`shouldCreateUser: false`), so the check can't be
  skipped that way.
- Privacy notice under the counseling, course-request and feedback forms.
- Account page: lists Find My Path answers and saved universities among what is deleted, and says
  form submissions are kept separately (email to delete).
- /cookies: "Clear my saved choices" button (PECR Sch. A1 para 6 "simple means of objecting").

## Decisions made for you (change if you disagree)

- Contact records (GHL) kept no longer than 3 years after last contact.
- Readiness lead to GHL on "legitimate interests" with a right to object. Alternative: ask consent
  with a tick box before sending. For under-18s, consent is the safer choice.
- No cookie banner: everything stored is strictly necessary or a preference with an objection
  route (UK law read). Under EU law only "strictly necessary" is exempt; theme and currency are set
  by the user's own click, which we treat as part of the service they asked for. A lawyer may
  prefer a banner for EU visitors.

## Still open

1. Company: name, registration, address, and governing law (Terms section 11 is a placeholder).
2. Data processing terms: confirm accepted with Supabase, HighLevel, Anthropic, Cloudflare (the
   privacy policy says we rely on providers' data protection terms for transfers).
3. Parental consent is a declaration, not verified. Needs a real step (e.g. email to the parent
   with a confirm link) before relying on it, and before 13 May 2027 for India if that date holds.
4. Read the ICO Children's code, UAE PDPL and India DPDP Act/Rules from their official sites when
   they load (or from a lawyer).
5. Self-host the fonts so Google receives no visitor IPs (removes one third party).
6. Email notice to existing users about the new Terms and Privacy Policy.

## Update 2026-11-24: visit statistics

Subhan chose Cloudflare Web Analytics (cookieless). Sources read 2026-11-24 (saved in
`.research-cache/pages/`): cloudflare.com/web-analytics: "Cloudflare Web Analytics does not use
any client-side state, such as cookies or localStorage, to collect usage metrics." and "We also
don't “fingerprint” individuals via their IP address, User Agent string, or any other data for
the purpose of displaying analytics." developers.cloudflare.com/web-analytics/about: "Cloudflare
Web Analytics does not collect or use your visitors’ personal data." FAQ: "Currently, Cloudflare
Web Analytics do not log query strings" (so UTM tags are not recorded; referrers are).
/privacy, /cookies and the Cloudflare entry in `src/lib/legal.ts` now say this
(LEGAL_UPDATED 24 November 2026). It runs only once Subhan turns it on in the Cloudflare
dashboard (automatic setup for a proxied site). No storage is added, so no consent banner is
needed under PECR Sch. A1 as read on 19 Nov.
