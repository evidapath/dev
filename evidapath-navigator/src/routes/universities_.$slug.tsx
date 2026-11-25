import { createFileRoute, notFound } from "@tanstack/react-router";
import { CourseExplorer } from "../components/CourseExplorer";
import { courseSlugs, slugify, universityPath } from "../lib/paths";
import { canonicalLink, ogUrlMeta } from "../lib/seo";
import { jsonLdScript, universityJsonLd } from "../lib/structured-data";
import { loadUniversities } from "../lib/use-live-data";

// One page per university, showing one course at a time (CourseExplorer). It opens on the
// headline course; each course also has its own page (universities_.$slug_.$course.tsx).
// Only verified records get a page; the illustrative fallback set never does.
export const Route = createFileRoute("/universities_/$slug")({
  loader: async ({ params }) => {
    const d = await loadUniversities();
    const u =
      d.source === "sanity" ? d.universities.find((x) => slugify(x.name) === params.slug) : null;
    if (!u) throw notFound();
    return u;
  },
  head: ({ loaderData: u }) => {
    if (!u) return {};
    const path = universityPath(u.name);
    const n = u.programDetails?.length ?? 0;
    const title = `${u.name}: Fees and Entry Requirements | EvidaPath`;
    const description = `Tuition, living costs, entry requirements and deadlines for ${n} ${n === 1 ? "programme" : "programmes"} at ${u.name}, ${u.city}, ${u.country}, taken from the university's own pages.`;
    return {
      meta: [
        { title },
        { name: "description", content: description },
        { property: "og:title", content: title },
        { property: "og:description", content: description },
        ogUrlMeta(path),
      ],
      links: [canonicalLink(path)],
      scripts: [jsonLdScript(universityJsonLd(u))],
    };
  },
  component: UniversityPage,
});

function UniversityPage() {
  const u = Route.useLoaderData();
  return <CourseExplorer u={u} index={0} slugs={courseSlugs(u.programDetails ?? [])} />;
}
