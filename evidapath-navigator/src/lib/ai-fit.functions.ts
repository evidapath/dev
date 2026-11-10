// EXPERIMENTAL (AI fit): server functions. Both return nothing useful unless the
// signed-in user's email is in AI_FIT_ALLOWLIST and ANTHROPIC_API_KEY is set.

import { createServerFn } from "@tanstack/react-start";
import { z } from "zod";
import { aiFitUser, runAiFit, type FitResult } from "./ai-fit.server";

export const getAiFitAccess = createServerFn({ method: "GET" }).handler(async () => {
  try {
    return { enabled: !!(await aiFitUser()) };
  } catch {
    return { enabled: false };
  }
});

const InputSchema = z.object({
  curriculum: z.string().min(1).max(120),
  gradeBand: z.string().min(1).max(200),
  subject: z.string().min(1).max(120),
  budgetUsd: z.number().min(0).max(10_000_000),
  citizenship: z.string().max(120),
  languages: z.array(z.string().max(8)).max(10).optional(),
  ukHome: z.boolean().optional(),
});

export const getAiFit = createServerFn({ method: "POST" })
  .validator((data) => InputSchema.parse(data))
  .handler(async ({ data }): Promise<FitResult> => {
    const user = await aiFitUser();
    if (!user) throw new Error("AI fit isn't available for this account.");
    return runAiFit(user.id, data as Parameters<typeof runAiFit>[1]);
  });
