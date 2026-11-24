// Public URLs for the per-university and per-country pages. Slugs come from the names the
// site shows ("University of Toronto" -> university-of-toronto), so a URL reads like the
// search it answers. Used by the pages, their links, the sitemap and the structured data.

export function slugify(name: string): string {
  return name
    .normalize("NFKD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/&/g, " and ")
    .replace(/['’]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export const universityPath = (name: string) => `/universities/${slugify(name)}`;
export const countryCostPath = (country: string) => `/study-in/${slugify(country)}/cost`;
