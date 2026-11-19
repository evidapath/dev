import { createServerFn } from "@tanstack/react-start";
import { getUniversities } from "./universities.functions";
import { getScholarships } from "./scholarships.functions";
import { homeStats, pickFeatured } from "./home";

// Just what the homepage shows above the fold (3 cards and the counts), rendered on the
// server so the hero card doesn't pop in after the page loads. The full data set for the
// sections further down still loads in the browser. Sanity results are cached server-side.
export const getHomeHero = createServerFn({ method: "GET" }).handler(async () => {
  const [u, s] = await Promise.all([getUniversities(), getScholarships()]);
  return {
    featured: pickFeatured(u.universities),
    stats: homeStats(u.universities, s.scholarships),
  };
});
