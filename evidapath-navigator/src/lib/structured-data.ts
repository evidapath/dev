// schema.org JSON-LD for answer engines and search (docs/aeo-plan.md, Phase 2).
// Built from the same records the page renders, so markup and page can't disagree.
// Only stored values go in: a field that is empty, unpublished or not yet re-checked
// against the official page is left out, never filled in.

import type { ProgramView, University } from "./mock-data";
import { canonicalUrl } from "./seo";
import { coursePath, universityPath } from "./paths";

type Json = Record<string, unknown>;

/** A head() script entry carrying JSON-LD. "<" is escaped so data can't close the tag. */
export function jsonLdScript(data: Json) {
  return {
    type: "application/ld+json",
    children: JSON.stringify(data).replace(/</g, "\\u003c"),
  };
}

/** EvidaPath itself, on every page. */
export function siteJsonLd(): Json {
  const url = canonicalUrl("/");
  return {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Organization",
        "@id": `${url}#organization`,
        name: "EvidaPath",
        url,
        description:
          "Education decision intelligence for international students: tuition, living costs and entry requirements from universities' own published sources.",
      },
      {
        "@type": "WebSite",
        "@id": `${url}#website`,
        name: "EvidaPath",
        url,
        publisher: { "@id": `${url}#organization` },
      },
    ],
  };
}

/** Years as an ISO 8601 duration: 4 → "P4Y", 3.5 → "P3Y6M". */
export function isoYears(years: number): string | undefined {
  if (!(years > 0)) return undefined;
  const whole = Math.floor(years);
  const months = Math.round((years - whole) * 12);
  return `P${whole ? `${whole}Y` : ""}${months ? `${months}M` : ""}`;
}

/** Yearly tuition per fee group; nothing when the cost isn't re-checked or isn't priced. */
export function tuitionOffers(p: ProgramView): Json[] {
  const offer = (amount: number, currency: string, who?: string): Json => ({
    "@type": "Offer",
    category: who ? `Tuition per year, ${who}` : "Tuition per year",
    price: amount,
    priceCurrency: currency,
  });
  if (p.costs.notChecked) return [];
  if (p.costTiers?.length)
    return p.costTiers
      .filter((t) => t.costs.tuitionPerYear != null && t.costs.currency)
      .map((t) => offer(t.costs.tuitionPerYear as number, t.costs.currency, t.label));
  if (p.costs.tuitionPerYear == null || !p.costs.currency) return [];
  return [offer(p.costs.tuitionPerYear, p.costs.currency, p.costLabel)];
}

function programJsonLd(p: ProgramView, providerId: string): Json {
  const offers = tuitionOffers(p);
  const time = isoYears(p.durationYears);
  return {
    "@type": "EducationalOccupationalProgram",
    name: p.degree ? `${p.name} (${p.degree})` : p.name,
    provider: { "@id": providerId },
    ...(p.degree ? { educationalCredentialAwarded: p.degree } : {}),
    ...(time ? { timeToComplete: time } : {}),
    ...(offers.length ? { offers } : {}),
  };
}

/** One id per university, at its own page, shared by every page that describes it. */
const universityId = (u: University) => `${canonicalUrl(universityPath(u.name))}#university`;

function collegeJsonLd(u: University): Json {
  return {
    "@type": "CollegeOrUniversity",
    "@id": universityId(u),
    name: u.name,
    url: canonicalUrl(universityPath(u.name)),
    ...(u.officialSourceUrl ? { sameAs: u.officialSourceUrl } : {}),
    ...(u.city || u.country
      ? {
          address: {
            "@type": "PostalAddress",
            ...(u.city ? { addressLocality: u.city } : {}),
            ...(u.country ? { addressCountry: u.country } : {}),
          },
        }
      : {}),
  };
}

/** A university's own page: the university and each of its programmes. */
export function universityJsonLd(u: University): Json {
  return {
    "@context": "https://schema.org",
    "@graph": [
      collegeJsonLd(u),
      ...(u.programDetails ?? []).map((p) => programJsonLd(p, universityId(u))),
    ],
  };
}

/** The /universities list: every university, each linking to its own page, where its
 *  programmes are described (universityJsonLd). */
export function universitiesJsonLd(universities: University[], pagePath: string): Json {
  const page = canonicalUrl(pagePath);
  return {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "ItemList",
        name: "Universities on EvidaPath",
        url: page,
        numberOfItems: universities.length,
        itemListElement: universities.map((u, i) => ({
          "@type": "ListItem",
          position: i + 1,
          item: {
            ...collegeJsonLd(u),
          },
        })),
      },
    ],
  };
}

/** One course's own page: the programme, its university, and where the page sits. */
export function courseJsonLd(u: University, p: ProgramView, slug: string): Json {
  const url = canonicalUrl(coursePath(u.name, slug));
  return {
    "@context": "https://schema.org",
    "@graph": [
      collegeJsonLd(u),
      { ...programJsonLd(p, universityId(u)), "@id": `${url}#programme`, url },
      {
        "@type": "BreadcrumbList",
        itemListElement: [
          {
            "@type": "ListItem",
            position: 1,
            name: "Universities",
            item: canonicalUrl("/universities"),
          },
          {
            "@type": "ListItem",
            position: 2,
            name: u.name,
            item: canonicalUrl(universityPath(u.name)),
          },
          { "@type": "ListItem", position: 3, name: p.name, item: url },
        ],
      },
    ],
  };
}
