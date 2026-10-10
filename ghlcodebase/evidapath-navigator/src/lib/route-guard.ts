import { redirect } from "@tanstack/react-router";
import type { RouterContext } from "../router";

/**
 * Route-level auth guard for protected EvidaPath routes.
 *
 * Runs in beforeLoad, after the root beforeLoad has resolved the real session
 * into context.auth (via the user-scoped SSR client + request cookies, subject
 * to RLS — no service-role key). If there is no authenticated user, redirect to
 * /sign-in and preserve the intended destination through the `redirect` search
 * param so the user returns to the action they originally clicked.
 */
export function requireAuth(context: RouterContext, pathname: string) {
  if (!context.auth.user) {
    throw redirect({
      to: "/sign-in",
      search: { redirect: pathname },
    });
  }
}
