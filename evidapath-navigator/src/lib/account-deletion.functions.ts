// Thin server-function wrappers for self-service account deletion.
// Safe to import anywhere. All logic lives in ./account-deletion.server.ts
// (server-only, RLS-scoped; service-role key used only for the final auth-user
// deletion inside the admin client).

import { createServerFn } from "@tanstack/react-start";
import { getDeletionSummarySvc, deleteAccountSvc } from "./account-deletion.server";

export const getDeletionSummary = createServerFn({ method: "GET" }).handler(async () => {
  return getDeletionSummarySvc();
});

export const deleteAccount = createServerFn({ method: "POST" }).handler(async () => {
  return deleteAccountSvc();
});
