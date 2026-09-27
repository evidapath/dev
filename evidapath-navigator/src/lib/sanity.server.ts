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

import type { University } from "./mock-data";

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
    "cost": *[_type=="costProfile" && references(^._id)][0]{
      tuition_annual, mandatory_fees_annual, estimated_living_costs_annual, currency, duration_years
    }
  },
  "scholarshipCount": count(*[_type=="scholarship" && ^.id in institutions_covered])
}`;

interface SanityCost {
  tuition_annual: number | null;
  mandatory_fees_annual: number | null;
  estimated_living_costs_annual: number | null;
  currency: string | null;
  duration_years: number | null;
}
interface SanityProgram {
  program_name: string | null;
  degree_type: string | null;
  duration_value: number | null;
  duration_unit: string | null;
  field_of_study: string | null;
  language_of_instruction: string[] | null;
  record_status: string | null;
  cost: SanityCost | null;
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
  if (!p || p.duration_value == null) return p?.cost?.duration_years ?? 0;
  const unit = (p.duration_unit || "").toLowerCase();
  return unit.startsWith("semester") ? p.duration_value / 2 : p.duration_value;
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
const FACT_CHECKED = new Set<string>(["ae-nyu-abu-dhabi"]);

// Student-facing confidence label. "Verified" requires BOTH an EvidaPath
// primary-source fact-check AND a VERIFIED-or-higher Sanity record_status.
// Everything else is honestly "verification in progress".
function confidenceLabel(universityId: string, status: string | null): string {
  const verifiedStatus = status === "VERIFIED" || status === "APPROVED" || status === "PUBLISHED";
  if (FACT_CHECKED.has(universityId) && verifiedStatus) {
    return "Verified against official sources";
  }
  return "Verification in progress";
}

function adapt(u: SanityUniversity): University {
  const program = (u.programs || [])[0];
  const cost = program?.cost || null;

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
    evidenceConfidence: confidenceLabel(u.id, u.record_status),
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
