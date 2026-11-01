import { QueryClient } from "@tanstack/react-query";
import { createRouter } from "@tanstack/react-router";
import { routeTree } from "./routeTree.gen";
import type { AuthSession } from "./lib/auth.functions";

export interface RouterContext {
  queryClient: QueryClient;
  auth: AuthSession;
}

export const getRouter = () => {
  const queryClient = new QueryClient();

  const router = createRouter({
    routeTree,
    context: {
      queryClient,
      // Placeholder; __root.tsx beforeLoad populates the real session.
      auth: { user: null },
    } satisfies RouterContext,
    scrollRestoration: true,
    // The page fades in; scrolling the old page up first looked jumpy.
    scrollRestorationBehavior: "instant",
    // Cross-fade between pages with the browser's View Transitions API (old page
    // snapshot → new page); browsers without it just swap instantly.
    defaultViewTransition: true,
    // Load a page's code when a link is hovered/touched, so the click is instant.
    defaultPreload: "intent",
    defaultPreloadStaleTime: 0,
  });

  return router;
};
