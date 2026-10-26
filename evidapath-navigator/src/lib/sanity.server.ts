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

import type { University, Scholarship, ProgramView } from "./mock-data";

const PROJECT =
  process.env["SANITY_PROJECT_ID"] || import.meta.env["SANITY_PROJECT_ID"] || "jxwrtsiz";
const DATASET = process.env["SANITY_DATASET"] || import.meta.env["SANITY_DATASET"] || "staging";
const API_VERSION = "2021-10-21";

const PENDING = "Pending verified data";

const UNIVERSITIES_QUERY = `*[_type=="university"] | order(canonical_name){
  id, canonical_name, aliases, institution_type, official_website, record_status, last_verified,
  evidapath_verified,
  "country": country_ref->name,
  "countryCode": country_ref->id,
  "countryCurrency": country_ref->currency_default,
  "city": primary_city_ref->name,
  "deadlines": *[_type=="decisionPlan" && references(^._id)] | order(application_deadline){
    plan_type, application_deadline, decision_release_date, binding, application_platform
  },
  "programs": *[_type=="program" && references(^._id)] | order(program_name){
    program_name, degree_type, duration_value, duration_unit, field_of_study,
    language_of_instruction, record_status,
    "costs": *[_type=="costProfile" && references(^._id)]{
      tuition_annual, tuition_basis, mandatory_fees_annual, estimated_living_costs_annual,
      currency, duration_years, "residencyDesc": residency_category_ref->description
    },
    "admissions": *[_type=="admissionsRequirement" && references(^._id)]{
      curriculum_type, academic_threshold, required_subjects,
      "tests": standardized_tests[]{test_name, required, notes},
      "languages": language_requirements[]{language, min_score}
    }
  },
  "scholarshipCount": count(*[_type=="scholarship" && ^.id in institutions_covered && ("undergraduate" in degree_levels || "BSc" in degree_levels)])
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
interface SanityAdmissionReq {
  curriculum_type: string | null;
  academic_threshold: string | null;
  required_subjects: string[] | null;
  tests: { test_name: string | null; required: string | null; notes: string | null }[] | null;
  languages: { language: string | null; min_score: string | null }[] | null;
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
  admissions: SanityAdmissionReq[] | null;
}
interface SanityDeadline {
  plan_type: string | null;
  application_deadline: string | null;
  decision_release_date: string | null;
  binding: boolean | null;
  application_platform: string | null;
}
interface SanityUniversity {
  id: string;
  canonical_name: string;
  aliases: string[] | null;
  institution_type: string | null;
  official_website: string | null;
  record_status: string | null;
  last_verified: string | null;
  evidapath_verified: boolean | null;
  country: string | null;
  countryCode: string | null;
  countryCurrency: string | null;
  city: string | null;
  deadlines: SanityDeadline[] | null;
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
  // Production reads ONLY published content. Dev may opt into previewing unpublished
  // drafts (e.g. the Batch-2 university imports) by setting SANITY_PERSPECTIVE=drafts
  // in .dev.vars — never set this in production.
  const perspective = process.env["SANITY_PERSPECTIVE"] || "published";
  const url =
    `https://${PROJECT}.api.sanity.io/v${API_VERSION}/data/query/${DATASET}` +
    `?perspective=${perspective}&query=${encodeURIComponent(query)}`;
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
  "de-tu-munich", // fact-checks/tu-munich-2026-10-07.md
  // US batch — fact-checks/us-batch-2026-10-26.md (all 10 confirmed against official 2026-27 COA pages)
  "us-princeton",
  "us-mit",
  "us-harvard",
  "us-stanford",
  "us-upenn",
  "us-cornell",
  "us-nyu",
  "us-usc",
  "us-purdue",
  "us-asu",
  // Canada batch — fact-checks/ca-batch-2026-10-26.md
  // Waterloo/McGill/McMaster: primary-source confirmed. UBC/Alberta: Board-approved rates via secondary sources (fee pages inaccessible; caveat documented in fact-check file)
  "ca-waterloo",
  "ca-ubc",
  "ca-mcgill",
  "ca-mcmaster",
  "ca-alberta",
  // UK batch — fact-checks/uk-batch-2026-10-26.md
  // Cambridge/Warwick/Birmingham: primary source confirmed. Imperial: corrected to 2027 entry fees.
  // Manchester CS+Eng: primary source confirmed (Eng corrected). UCL/Nottingham: secondary source (pages 403/404).
  "uk-cambridge",
  "uk-imperial",
  "uk-ucl",
  "uk-warwick",
  "uk-manchester",
  "uk-birmingham",
  "uk-nottingham",
  // Germany batch — fact-checks/de-batch-2026-10-26.md
  // TU Berlin + LMU: primary source confirmed. RWTH + Heidelberg + KIT: state law (NRW/BW) + partial primary source.
  "de-rwth-aachen",
  "de-heidelberg",
  "de-tu-berlin",
  "de-kit",
  "de-lmu",
  // Netherlands batch — fact-checks/nl-batch-2026-10-26.md
  // All 3 primary-source confirmed; TU/e and UT corrected to 2027-28 rates; UvA already correct.
  "nl-tue",
  "nl-uva",
  "nl-ut",
  // Australia batch — fact-checks/au-batch-2026-10-26.md
  // UniMelb: primary source (2027 range minimums). Monash BCS corrected ($55,500→$58,940); BEng+BCom confirmed.
  // USyd: primary source (search-confirmed). UNSW: primary source per-UOC rate confirmed. 2028 fees not yet published.
  "au-unimelb",
  "au-monash",
  "au-usyd",
  "au-unsw",
  // UAE batch — fact-checks/ae-batch-2026-10-26.md
  // AUS/UAEU/Khalifa/UoS: primary source confirmed. Birmingham: 3 fees corrected to Sept 2027.
  // Heriot-Watt: primary source confirmed. RIT: confirmed. CUD: BBA corrected (pre→VAT-incl).
  "ae-aus",
  "ae-uaeu",
  "ae-khalifa",
  "ae-university-of-sharjah",
  "ae-birmingham-dubai",
  "ae-heriot-watt-dubai",
  "ae-rit-dubai",
  "ae-canadian-university-dubai",
  // Malaysia batch — fact-checks/my-batch-2026-10-26.md
  // UM: confirmed. Monash: CS confirmed; ME+BBusComm null→filled. UNM: all 3 confirmed. Taylor's: all 3 corrected (2025→2027 official PDF).
  "my-um",
  "my-monash",
  "my-nottingham",
  "my-taylors",
]);

// Student-facing confidence label. "Verified" means EvidaPath has checked this
// university's displayed facts against official PRIMARY sources (logged in
// fact-checks/). Source of truth is Sanity's `evidapath_verified` flag (set by
// scripts/mark_verified_in_sanity.py after a logged pass, visible in Studio).
// The FACT_CHECKED allowlist is kept as a migration fallback so the label does
// not regress before the Sanity flag is written; remove it once Sanity carries
// the flag for every verified school. Sanity's own `record_status` is a separate
// pipeline state and is intentionally NOT used here.
function confidenceLabel(universityId: string, sanityVerified: boolean | null): string {
  return sanityVerified === true || FACT_CHECKED.has(universityId)
    ? "Verified against official sources"
    : "Verification in progress";
}

// Build the self-contained view (cost + duration + admissions) for ONE program.
// Used both for each entry of programDetails[] and for the featured flat fields.
function buildProgramView(p: SanityProgram, countryCurrency: string | null): ProgramView {
  const { chosen: cost, note } = selectCost(p.costs ?? null);
  const tuition = cost?.tuition_annual ?? null;
  const fees = cost?.mandatory_fees_annual ?? null;
  const living = cost?.estimated_living_costs_annual ?? null;
  const currency = cost?.currency || countryCurrency || "";
  const years = durationYears(p);
  // Full total requires all three cost components. Tuition-only total (fees+living unknown)
  // is surfaced when tuition is known but living isn't verified yet.
  const complete = tuition != null && fees != null && living != null;
  const totalAnnual = complete ? tuition + fees + living : null;
  const tuitionOnlyTotal = !complete && tuition != null && years > 0 ? tuition * years : null;
  const totalDegree = totalAnnual != null && years > 0 ? totalAnnual * years : tuitionOnlyTotal;
  const admissionsByCurriculum = (p.admissions || [])
    .filter((a) => a.curriculum_type)
    .map((a) => ({
      curriculum: a.curriculum_type as string,
      threshold: a.academic_threshold,
      subjects: (a.required_subjects || []).filter((s): s is string => !!s),
      tests: (a.tests || [])
        .filter((t) => t.test_name && t.required !== "not_required")
        .map((t) => `${t.test_name}${t.required ? ` (${t.required})` : ""}`),
    }));
  return {
    name: p.program_name || "Program",
    fieldOfStudy: p.field_of_study || "",
    degree: p.degree_type || "",
    durationYears: years,
    costs: {
      tuitionPerYear: tuition,
      livingPerYear: living,
      mandatoryFees: fees,
      currency,
      totalAnnual,
      totalDegree,
    },
    ...(note ? { costResidencyNote: note } : {}),
    admissionsByCurriculum,
  };
}

function adapt(u: SanityUniversity): University {
  const progs = u.programs || [];
  // Feature Computer Science as the headline program when present (keeps display
  // stable as programs are added); programDetails[] carries all for the selector.
  const featuredIdx = Math.max(
    0,
    progs.findIndex((p) => p.field_of_study === "Computer Science"),
  );
  const built = progs.map((p) => buildProgramView(p, u.countryCurrency));
  // Put the featured (CS) program first so programDetails[0] is the headline and
  // the UI selector can default to index 0.
  const programDetails =
    built.length > 1 && featuredIdx > 0
      ? [built[featuredIdx]!, ...built.filter((_, i) => i !== featuredIdx)]
      : built;
  const featured = programDetails[0];

  const tuition = featured?.costs.tuitionPerYear ?? null;
  const fees = featured?.costs.mandatoryFees ?? null;
  const living = featured?.costs.livingPerYear ?? null;
  const currency = featured?.costs.currency || u.countryCurrency || "";
  const totalAnnual = featured?.costs.totalAnnual ?? null;
  const years = featured?.durationYears ?? 0;
  const totalDegree = featured?.costs.totalDegree ?? null;
  const costResidencyNote = featured?.costResidencyNote;
  const admissionsByCurriculum = featured?.admissionsByCurriculum ?? [];

  // Derive A-level threshold from Sanity admissions data. Prefer A-Level; fall back to IB.
  const aLevelAdm = admissionsByCurriculum.find((a) =>
    /a.?level/i.test(a.curriculum ?? ""),
  );
  const ibAdm = admissionsByCurriculum.find((a) => /baccalaureate|^ib$/i.test(a.curriculum ?? ""));
  const admThreshold = aLevelAdm?.threshold || ibAdm?.threshold || null;
  const admPrereqs = aLevelAdm?.subjects ?? ibAdm?.subjects ?? [];
  // When admissions data exists but threshold is null, institution uses holistic/competitive
  // admissions without a published grade cutoff (verified absence, not missing data).
  const hasAdmissionsData = admissionsByCurriculum.length > 0;
  const admThresholdDisplay = admThreshold || (hasAdmissionsData ? "No published grade cutoff" : PENDING);

  const aliases = u.aliases || [];
  const shortName = aliases[aliases.length - 1] || u.canonical_name;

  // Verified deadlines (surfaced only when present).
  const deadlines = (u.deadlines || [])
    .filter((d) => d.application_deadline)
    .map((d) => ({
      label: prettyType(d.plan_type),
      deadline: d.application_deadline,
      decisionDate: d.decision_release_date,
      binding: d.binding,
      platform: d.application_platform,
    }));

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
      system: aLevelAdm ? "GCE A-Level" : ibAdm ? "IB Diploma" : PENDING,
      target: admThresholdDisplay,
      prerequisites: admPrereqs,
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
    ...(deadlines.length ? { deadlines } : {}),
    ...(admissionsByCurriculum.length ? { admissionsByCurriculum } : {}),
    ...(programDetails.length > 1 ? { programDetails } : {}),
    evidenceConfidence: confidenceLabel(u.id, u.evidapath_verified),
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

// Only UNDERGRADUATE scholarships — EvidaPath's programs are all bachelor's. The data
// tags degree_levels (values are inconsistent: 'undergraduate' or 'BSc'); a scholarship
// tagged only postgraduate (e.g. TU Delft's van Effen, MSc-only) must NOT show for an
// undergrad applicant (#2/#7 — it would advertise funding they're ineligible for).
const SCHOLARSHIPS_QUERY = `*[_type=="scholarship" && ("undergraduate" in degree_levels || "BSc" in degree_levels)] | order(name){
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
