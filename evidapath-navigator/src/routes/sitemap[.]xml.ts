import { createFileRoute } from "@tanstack/react-router";
import { getAnswers } from "../lib/answers.functions";
import { countryCostPath, coursePath, courseSlugs, universityPath } from "../lib/paths";
import { canonicalUrl } from "../lib/seo";
import { getUniversities } from "../lib/universities.functions";

// /sitemap.xml, built from the live data so every university, course and country page is listed.
// University and country pages appear only when the data comes from Sanity (never the
// illustrative fallback set). Static pages carry the date their content last changed.
const STATIC_UPDATED = "2026-11-24";
const STATIC: [string, number][] = [
  ["/", 1.0],
  ["/find-my-path", 1.0],
  ["/universities", 0.9],
  ["/answers", 0.9],
  ["/scholarships", 0.8],
  ["/discover", 0.8],
  ["/compare", 0.7],
  ["/careers", 0.6],
  ["/intelligence", 0.6],
  ["/features", 0.8],
  ["/example/fit-check", 0.6],
  ["/about", 0.6],
  ["/privacy", 0.3],
  ["/terms", 0.3],
  ["/cookies", 0.3],
];

const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

export const Route = createFileRoute("/sitemap.xml")({
  server: {
    handlers: {
      GET: async () => {
        const [u, a] = await Promise.all([getUniversities(), getAnswers()]);
        const urls = STATIC.map(
          ([p, pr]) =>
            `<url><loc>${esc(canonicalUrl(p))}</loc><lastmod>${STATIC_UPDATED}</lastmod><priority>${pr}</priority></url>`,
        );
        const countries = new Set(a?.data.costs.map((c) => c.country) ?? []);
        for (const c of countries)
          urls.push(
            `<url><loc>${esc(canonicalUrl(countryCostPath(c)))}</loc><priority>0.8</priority></url>`,
          );
        if (u.source === "sanity")
          for (const x of u.universities)
            urls.push(
              `<url><loc>${esc(canonicalUrl(universityPath(x.name)))}</loc><priority>0.8</priority></url>`,
              ...courseSlugs(x.programDetails ?? []).map(
                (s) =>
                  `<url><loc>${esc(canonicalUrl(coursePath(x.name, s)))}</loc><priority>0.7</priority></url>`,
              ),
            );
        const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.join("\n")}\n</urlset>\n`;
        return new Response(xml, {
          headers: {
            "content-type": "application/xml; charset=utf-8",
            "cache-control": "public, max-age=3600",
          },
        });
      },
    },
  },
});
