import { createFileRoute, notFound } from "@tanstack/react-router";
import { CourseExplorer } from "../components/CourseExplorer";
import { coursePath, courseSlugs, slugify } from "../lib/paths";
import { canonicalLink, ogUrlMeta } from "../lib/seo";
import { courseJsonLd, jsonLdScript } from "../lib/structured-data";
import { loadUniversities } from "../lib/use-live-data";

// One page per course (/universities/<uni>/<course>): the university page with that course
// selected, so each course has its own address, title and search-engine labels.
export const Route = createFileRoute("/universities_/$slug_/$course")({
  loader: async ({ params }) => {
    const d = await loadUniversities();
    const u =
      d.source === "sanity" ? d.universities.find((x) => slugify(x.name) === params.slug) : null;
    if (!u) throw notFound();
    const slugs = courseSlugs(u.programDetails ?? []);
    const index = slugs.indexOf(params.course);
    if (index < 0) throw notFound();
    return { u, index, slugs };
  },
  head: ({ loaderData: d }) => {
    const p = d?.u.programDetails?.[d.index];
    if (!d || !p) return {};
    const { u } = d;
    const path = coursePath(u.name, d.slugs[d.index]!);
    const name = `${p.name}${p.degree ? ` (${p.degree})` : ""}`;
    const title = `${name} at ${u.name}: Fees and Entry Requirements | EvidaPath`;
    const length = p.durationYears > 0 ? `${p.durationYears} years. ` : "";
    const description = `${name} at ${u.name}, ${u.city}, ${u.country}. ${length}Tuition, living costs and entry requirements by qualification, taken from the university's own pages.`;
    return {
      meta: [
        { title },
        { name: "description", content: description },
        { property: "og:title", content: title },
        { property: "og:description", content: description },
        ogUrlMeta(path),
      ],
      links: [canonicalLink(path)],
      scripts: [jsonLdScript(courseJsonLd(u, p, d.slugs[d.index]!))],
    };
  },
  component: CoursePage,
});

function CoursePage() {
  const { u, index, slugs } = Route.useLoaderData();
  return <CourseExplorer u={u} index={index} slugs={slugs} />;
}
