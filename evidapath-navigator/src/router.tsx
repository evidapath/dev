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
    defaultPreloadStaleTime: 0,
  });

  return router;
};
