// Server-only Sanity read layer. Named *.server.ts so the TanStack Start import
// guard keeps it (and the read token) out of client bundles.
//
// Reads the PUBLISHED perspective of the Sanity dataset (default: staging) with
// a read-only token. We publish the five-school data into staging via
// sanity-studio/scripts/publish_to_sanity.py so references (city, country, cost
// profile, scholarships) resolve. No @sanity/client dependency: a read-only GROQ
// query is a plain authenticated GET.
//
// Honesty rules baked into the adapter (EvidaPath core principle — show
// uncertainty, never manufacture certainty):
//   - record_status drives the confidence label; only NYUAD is "verified".
//   - a cost TOTAL is emitted ONLY when tuition + fees + living are all known;
//     otherwise it stays null ("pending") rather than showing a partial total.
//   - any field with no verified value stays null / "Pending verified data".

import type { University, Scholarship } from "./mock-data";

const PROJECT =
  process.env["SANITY_PROJECT_ID"] || import.meta.env["SANITY_PROJECT_ID"] || "jxwrtsiz";
const DATASET = process.env["SANITY_DATASET"] || import.meta.env["SANITY_DATASET"] || "staging";
const API_VERSION = "2021-10-21";

const PENDING = "Pending verified data";

const UNIVERSITIES_QUERY = `*[_type=="university"] | order(canonical_name){
  id, canonical_name, aliases, institution_type, official_website, record_status, last_verified,
  "country": country_ref->name,
  "countryCode": country_ref->id,
  "countryCurrency": country_ref->currency_default,
  "city": primary_city_ref->name,
  "programs": *[_type=="program" && references(^._id)]{
    program_name, degree_type, duration_value, duration_unit, field_of_study,
    language_of_instruction, record_status,
    "costs": *[_type=="costProfile" && references(^._id)]{
      tuition_annual, tuition_basis, mandatory_fees_annual, estimated_living_costs_annual,
      currency, duration_years, "residencyDesc": residency_category_ref->description
    }
  },
  "scholarshipCount": count(*[_type=="scholarship" && ^.id in institutions_covered])
}`;

interface SanityCost {
  tuition_annual: number | null;
  tuition_basis: string | null;
  mandatory_fees_annual: number | null;
  estimated_living_costs_annual: number | null;
  currency: string | null;
  duration_years: number | null;
  residencyDesc: string | null;
}
interface SanityProgram {
  program_name: string | null;
  degree_type: string | null;
  duration_value: number | null;
  duration_unit: string | null;
  field_of_study: string | null;
  language_of_instruction: string[] | null;
  record_status: string | null;
  costs: SanityCost[] | null;
}
interface SanityUniversity {
  id: string;
  canonical_name: string;
  aliases: string[] | null;
  institution_type: string | null;
  official_website: string | null;
  record_status: string | null;
  last_verified: string | null;
  country: string | null;
  countryCode: string | null;
  countryCurrency: string | null;
  city: string | null;
  programs: SanityProgram[] | null;
  scholarshipCount: number | null;
}

async function sanityQuery<T>(query: string): Promise<T> {
  // Secret: read from process.env ONLY (never import.meta.env), so it is never
  // serialized into the client bundle — same guard as SUPABASE_SERVICE_ROLE_KEY.
  const token = process.env["SANITY_READ_TOKEN"];
  if (!token) {
    throw new Error(
      "SANITY_READ_TOKEN is not configured (add it to .dev.vars locally / Cloudflare env in prod).",
    );
  }
  const url =
    `https://${PROJECT}.api.sanity.io/v${API_VERSION}/data/query/${DATASET}` +
    `?perspective=published&query=${encodeURIComponent(query)}`;
  const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) {
    throw new Error(`Sanity query failed: ${res.status} ${await res.text()}`);
  }
  const json = (await res.json()) as { result: T };
  return json.result;
}

// ── helpers ────────────────────────────────────────────────────────────────

function flagEmoji(cc: string | null): string {
  if (!cc || cc.length !== 2) return "";
  return String.fromCodePoint(...[...cc.toUpperCase()].map((c) => 0x1f1e6 - 65 + c.charCodeAt(0)));
}

function durationYears(p: SanityProgram | undefined): number {
  if (!p || p.duration_value == null) return p?.costs?.[0]?.duration_years ?? 0;
  const unit = (p.duration_unit || "").toLowerCase();
  return unit.startsWith("semester") ? p.duration_value / 2 : p.duration_value;
}

// A program may have several cost profiles priced by residency (e.g. EU statutory
// vs non-EU institutional at Dutch universities). Show the HIGHEST tier: for
// EvidaPath's international audience that is their actual rate, and overstating
// cost is the safe error for a family's financial decision — never understate
// (#2, #7). Disclose the lower tier(s) in a note so it is never presented as the
// single universal price.
function selectCost(costs: SanityCost[] | null): { chosen: SanityCost | null; note?: string } {
  const priced = (costs || []).filter((c) => c.tuition_annual != null);
  if (priced.length === 0) return { chosen: (costs || [])[0] ?? null };
  const sorted = [...priced].sort((a, b) => (b.tuition_annual ?? 0) - (a.tuition_annual ?? 0));
  const chosen = sorted[0]!;
  if (sorted.length === 1) return { chosen };
  const lowest = sorted[sorted.length - 1]!;
  const cur = chosen.currency || "";
  const note =
    `Residency-based pricing: showing the highest tier (international / non-domestic students). ` +
    `Lower tiers pay from ${cur} ${(lowest.tuition_annual ?? 0).toLocaleString()}/yr.`;
  return { chosen, note };
}

function prettyType(t: string | null): string {
  if (!t) return PENDING;
  return t
    .split(/[-_]/)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

// EvidaPath-fact-checked institutions (checked against PRIMARY sources by us,
// not merely marked VERIFIED in Sanity by an earlier AI research run). Only these
// may read as "verified" to a student. Sanity's own record_status is NOT
// sufficient — the freeze report documents real coverage gaps on schools whose
// record_status is VERIFIED. Add a university id here only after a primary-source
// fact-check (see fact-checks/<school>-<date>.md).
const FACT_CHECKED = new Set<string>([
  "ae-nyu-abu-dhabi", // fact-checks/nyuad-2026-09-27.md
  "nl-tu-delft", // fact-checks/tu-delft-2026-10-03.md
  "ca-university-of-toronto", // fact-checks/toronto-2026-10-03.md
  "gb-university-of-oxford", // fact-checks/oxford-2026-10-03.md (resolved 2026-10-07)
]);

// Student-facing confidence label. "Verified" means EvidaPath has checked this
// university's displayed facts against official PRIMARY sources (logged in
// fact-checks/). The FACT_CHECKED allowlist IS that authority — Sanity's own
// record_status is a separate internal pipeline state and is intentionally NOT
// gated on here (a school can be STRUCTURED in Sanity yet fully primary-source
// verified by us, e.g. TU Delft). A school is added to FACT_CHECKED only after
// a logged primary-source pass, so the allowlist is the correct gate.
function confidenceLabel(universityId: string): string {
  return FACT_CHECKED.has(universityId)
    ? "Verified against official sources"
    : "Verification in progress";
}

function adapt(u: SanityUniversity): University {
  const program = (u.programs || [])[0];
  const { chosen: cost, note: costResidencyNote } = selectCost(program?.costs ?? null);

  const tuition = cost?.tuition_annual ?? null;
  const fees = cost?.mandatory_fees_annual ?? null;
  const living = cost?.estimated_living_costs_annual ?? null;
  const currency = cost?.currency || u.countryCurrency || "";

  // Only emit a total when the full cost picture is known (#7: no partial total
  // masquerading as complete). tuition may legitimately be 0 (tuition-free).
  const complete = tuition != null && fees != null && living != null;
  const totalAnnual = complete ? tuition + fees + living : null;
  const years = durationYears(program);
  const totalDegree = totalAnnual != null && years > 0 ? totalAnnual * years : null;

  const aliases = u.aliases || [];
  const shortName = aliases[aliases.length - 1] || u.canonical_name;

  return {
    id: u.id,
    name: u.canonical_name,
    shortName,
    country: u.country || PENDING,
    city: u.city || PENDING,
    flag: flagEmoji(u.countryCode),
    type: prettyType(u.institution_type),
    programs: (u.programs || []).map((p) => p.program_name || "").filter(Boolean),
    durationYears: years,
    academicRequirements: {
      // Admissions detail is the Analyze page's job; kept honest/pending here.
      system: PENDING,
      target: PENDING,
      prerequisites: [],
    },
    costs: {
      tuitionPerYear: tuition,
      livingPerYear: living,
      mandatoryFees: fees,
      currency,
      totalAnnual,
      totalDegree,
    },
    affordabilityIndex: {
      score: null,
      category: PENDING,
      notes:
        "Affordability is calculated against your budget in Discover and Analyze, not shown as a fixed score here.",
    },
    scholarshipsAvailable: u.scholarshipCount ?? null,
    scholarshipCoverageMax: null,
    ...(costResidencyNote ? { costResidencyNote } : {}),
    evidenceConfidence: confidenceLabel(u.id),
    lastVerified: u.last_verified || "Not yet verified",
    officialSourceUrl: u.official_website || "",
    alternativePathways: [],
    admissionsEvidence: {
      historicalBenchmark: PENDING,
      admitProfileDetail:
        "Admissions evidence will appear here once verified institutional benchmarks are connected.",
      uncertaintyNote:
        "Where official sources are incomplete or conflict, EvidaPath shows the uncertainty rather than inventing a number.",
    },
  };
}

/** Fetch the five-school set from Sanity and adapt to the app's University shape. */
export async function getUniversitiesFromSanity(): Promise<University[]> {
  const rows = await sanityQuery<SanityUniversity[]>(UNIVERSITIES_QUERY);
  return (rows || []).map(adapt);
}

// ── Scholarships ─────────────────────────────────────────────────────────────

const SCHOLARSHIPS_QUERY = `*[_type=="scholarship"] | order(name){
  id, name, provider, eligible_citizenships, residency_restrictions, academic_criteria,
  other_eligibility_criteria, award_amount, award_amount_currency, deadline_academic_year,
  renewable, renewal_conditions, duration, record_status, verification_status,
  official_source_url, last_checked, institutions_covered,
  "coveredUniversities": *[_type=="university" && id in ^.institutions_covered]{
    id, canonical_name, "country": country_ref->name
  }
}`;

interface SanityScholarship {
  id: string;
  name: string;
  provider: string | null;
  eligible_citizenships: string[] | null;
  residency_restrictions: string | null;
  academic_criteria: string | null;
  other_eligibility_criteria: string | null;
  award_amount: string | number | null;
  award_amount_currency: string | null;
  deadline_academic_year: string | null;
  renewable: boolean | null;
  renewal_conditions: string | null;
  duration: string | null;
  record_status: string | null;
  verification_status: string | null;
  official_source_url: string | null;
  last_checked: string | null;
  institutions_covered: string[] | null;
  coveredUniversities: { id: string; canonical_name: string; country: string | null }[] | null;
}

// Scholarship verification label. Honest about uncertainty (#7): an explicit
// source CONFLICT is surfaced, never resolved; only a scholarship whose covered
// university we have primary-source fact-checked AND that is VERIFIED may read
// "verified"; HUMAN_REVIEW reads "under review"; everything else "in progress".
function scholarshipConfidence(s: SanityScholarship): string {
  if (s.verification_status === "CONFLICT") {
    return "Sources conflict — shown, not resolved";
  }
  const covered = s.coveredUniversities || [];
  const factChecked = covered.some((u) => FACT_CHECKED.has(u.id));
  if (factChecked && s.record_status === "VERIFIED") {
    return "Verified against official sources";
  }
  if (s.record_status === "HUMAN_REVIEW") {
    return "Under review — see eligibility notes";
  }
  return "Verification in progress";
}

function adaptScholarship(s: SanityScholarship): Scholarship {
  const covered = s.coveredUniversities || [];
  const universitiesCovered = covered.map((u) => u.canonical_name).join(", ") || PENDING;
  const countriesOfStudy = Array.from(
    new Set(covered.map((u) => u.country).filter((c): c is string => !!c)),
  );

  const citizenship =
    s.residency_restrictions ||
    (s.eligible_citizenships || []).map((c) => c.toUpperCase()).join(", ") ||
    PENDING;

  // Award is heterogeneous (percent, income-banded, text, or a number). Show it
  // as sourced text; keep the numeric field null unless it is a clean number.
  const awardValue = typeof s.award_amount === "number" ? s.award_amount : null;
  const awardText =
    s.award_amount != null && String(s.award_amount).trim() !== ""
      ? `${s.award_amount}${s.award_amount_currency ? ` ${s.award_amount_currency}` : ""}`
      : undefined;

  const eligibilityParts = [s.residency_restrictions, s.other_eligibility_criteria].filter(Boolean);

  return {
    id: s.id,
    name: s.name,
    provider: s.provider || PENDING,
    universitiesCovered,
    citizenshipEligible: citizenship,
    countriesOfStudy,
    academicThreshold: s.academic_criteria || PENDING,
    awardValue,
    ...(awardText ? { awardSummary: awardText } : {}),
    awardFrequency: s.renewable ? "renewable" : s.duration || "",
    deadline: s.deadline_academic_year || PENDING,
    verificationStatus: scholarshipConfidence(s),
    lastChecked: s.last_checked || "Not yet verified",
    officialSource: s.official_source_url || "",
    eligibilitySummary: eligibilityParts.join(" ") || PENDING,
    renewalCriteria: s.renewal_conditions || "",
  };
}

/** Fetch scholarships from Sanity and adapt to the app's Scholarship shape. */
export async function getScholarshipsFromSanity(): Promise<Scholarship[]> {
  const rows = await sanityQuery<SanityScholarship[]>(SCHOLARSHIPS_QUERY);
  return (rows || []).map(adaptScholarship);
}
