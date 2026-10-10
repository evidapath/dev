// SEO helpers driven by the production site URL.
// VITE_SITE_URL is a publishable value (the public canonical origin) and is
// safe to ship to the client bundle. It carries no secrets.

const SITE_URL = (import.meta.env.VITE_SITE_URL ?? "").replace(/\/+$/, "");

/**
 * Return the absolute canonical URL for a given site path.
 * Falls back to an empty-string origin if VITE_SITE_URL is unset (dev), so the
 * helpers never throw during SSR.
 */
export function canonicalUrl(path = "/"): string {
  if (!SITE_URL) return path;
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${SITE_URL}${normalized}`;
}

/** A `<link rel="canonical">` object for a route `head().links` array. */
export function canonicalLink(path = "/") {
  return { rel: "canonical", href: canonicalUrl(path) };
}

/** An `og:url` meta object for a route `head().meta` array. */
export function ogUrlMeta(path = "/") {
  return { property: "og:url", content: canonicalUrl(path) };
}
