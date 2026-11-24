import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  Outlet,
  Link,
  createRootRouteWithContext,
  useRouter,
  HeadContent,
  Scripts,
} from "@tanstack/react-router";
import { useEffect, type ReactNode } from "react";

import appCss from "../styles.css?url";
import { reportVibeError } from "../lib/vibe-error-reporting";
import { getSession } from "../lib/auth.functions";
import type { RouterContext } from "../router";
import { AuthContextProvider } from "../components/AuthContext";
import { THEME_BOOT } from "../components/ThemeToggle";

function NotFoundComponent() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="max-w-md text-center">
        <h1 className="text-7xl font-bold text-foreground">404</h1>
        <h2 className="mt-4 text-xl font-semibold text-foreground">Page not found</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <div className="mt-6">
          <Link
            to="/"
            className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
          >
            Go home
          </Link>
        </div>
      </div>
    </div>
  );
}

function ErrorComponent({ error, reset }: { error: Error; reset: () => void }) {
  console.error(error);
  const router = useRouter();
  useEffect(() => {
    reportVibeError(error, { boundary: "tanstack_root_error_component" });
  }, [error]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="max-w-md text-center">
        <h1 className="text-xl font-semibold tracking-tight text-foreground">
          This page didn't load
        </h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Something went wrong on our end. You can try refreshing or head back home.
        </p>
        <div className="mt-6 flex flex-wrap justify-center gap-2">
          <button
            onClick={() => {
              router.invalidate();
              reset();
            }}
            className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
          >
            Try again
          </button>
          <a
            href="/"
            className="inline-flex items-center justify-center rounded-md border border-input bg-background px-4 py-2 text-sm font-medium text-foreground transition-colors hover:bg-accent"
          >
            Go home
          </a>
        </div>
      </div>
    </div>
  );
}

export const Route = createRootRouteWithContext<RouterContext>()({
  beforeLoad: async ({ context }) => {
    // Validate the session server-side on every navigation/SSR. The session is
    // read via the request-scoped Supabase server client (cookie-based), so no
    // service-role key is needed here. Protected routes can read context.auth.
    if (context.auth.user === null) {
      // context.auth is the placeholder { user: null } from router.tsx on the
      // first SSR pass; resolve the real session here.
      const session = cachedSession() ?? (await getSession());
      rememberSession(session);
      return { auth: session };
    }
    return { auth: context.auth };
  },
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { title: "EvidaPath: University Fees and Entry Grades Abroad" },
      {
        name: "description",
        content:
          "Tuition, living costs, entry grades and deadlines for universities abroad, taken from each university's own pages. Not published? We say so.",
      },
      { name: "author", content: "EvidaPath" },
      { property: "og:title", content: "EvidaPath: University Fees and Entry Grades Abroad" },
      {
        property: "og:description",
        content:
          "Tuition, living costs, entry grades and deadlines for universities abroad, taken from each university's own pages. Not published? We say so.",
      },
      { property: "og:type", content: "website" },
      { property: "og:site_name", content: "EvidaPath" },
      { property: "og:image", content: canonicalUrl("/og-image.jpg") },
      { property: "og:image:width", content: "1200" },
      { property: "og:image:height", content: "630" },
      {
        property: "og:image:alt",
        content: "EvidaPath: university fees and entry grades abroad, from official pages.",
      },
      { name: "twitter:card", content: "summary_large_image" },
      { name: "twitter:image", content: canonicalUrl("/og-image.jpg") },
    ],
    scripts: [jsonLdScript(siteJsonLd())],
    links: [
      {
        rel: "icon",
        type: "image/png",
        href: "/brand/favicon-48.png",
      },
      {
        rel: "apple-touch-icon",
        href: "/brand/apple-touch-icon.png",
      },
      { rel: "preconnect", href: "https://fonts.googleapis.com" },
      { rel: "preconnect", href: "https://fonts.gstatic.com", crossOrigin: "anonymous" },
      {
        rel: "stylesheet",
        href: "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Newsreader:ital,opsz,wght@1,6..72,400;1,6..72,500&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap",
      },
      {
        rel: "stylesheet",
        href: appCss,
      },
    ],
  }),
  shellComponent: RootShell,
  component: RootComponent,
  notFoundComponent: NotFoundComponent,
  errorComponent: ErrorComponent,
});

function RootShell({ children }: { children: ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_BOOT }} />
        <HeadContent />
      </head>
      <body>
        {children}
        <Scripts />
      </body>
    </html>
  );
}

import { Header } from "../components/Header";
import { Footer } from "../components/Footer";
import { PendingSavesSync } from "../components/PendingSavesSync";
import { jsonLdScript, siteJsonLd } from "../lib/structured-data";
import { canonicalUrl } from "../lib/seo";
import { FeedbackPrompt } from "../components/FeedbackPrompt";
import { cachedSession, rememberSession } from "../lib/session-cache";

function RootComponent() {
  const { queryClient, auth } = Route.useRouteContext();
  return (
    <QueryClientProvider client={queryClient}>
      <AuthContextProvider initialSession={auth}>
        <PendingSavesSync />
        <div className="flex min-h-screen flex-col bg-background text-foreground antialiased selection:bg-primary/20 selection:text-foreground">
          <Header />
          <main className="flex-1">
            {/* Required: nested routes render here. Removing <Outlet /> breaks all child routes. */}
            {/* Page changes cross-fade via View Transitions (see router.tsx). */}
            <Outlet />
          </main>
          <Footer />
        </div>
        <FeedbackPrompt />
      </AuthContextProvider>
    </QueryClientProvider>
  );
}
