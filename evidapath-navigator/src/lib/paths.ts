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

/** One slug per programme at a university: its name, plus the degree when two share a name
 *  (Psychology BA and BSc). Same order as the list given. */
export function courseSlugs(programmes: { name: string; degree: string }[]): string[] {
  const count = new Map<string, number>();
  for (const p of programmes) count.set(slugify(p.name), (count.get(slugify(p.name)) ?? 0) + 1);
  return programmes.map((p) =>
    (count.get(slugify(p.name)) ?? 0) > 1 ? slugify(`${p.name} ${p.degree}`) : slugify(p.name),
  );
}

export const coursePath = (university: string, courseSlug: string) =>
  `${universityPath(university)}/${courseSlug}`;
