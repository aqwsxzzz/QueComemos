import { z } from "zod";

import { cookSchema } from "@/features/recipe/types/recipe-types";
import { request } from "@/lib/api-client";

/** The API embeds the blocked cook so the list can show a name, not a UUID. */
export const blockSchema = z.object({
  id: z.string(),
  blocked_id: z.string(),
  blocked: cookSchema,
  created_at: z.string(),
});

export type Block = z.infer<typeof blockSchema>;

export const REPORT_REASONS = [
  { value: "spam", label: "Spam o publicidad" },
  { value: "abuse", label: "Agresión o acoso" },
  { value: "sexual", label: "Contenido sexual" },
  { value: "not_a_recipe", label: "No es una receta" },
  { value: "other", label: "Otra cosa" },
] as const;

export type ReportReason = (typeof REPORT_REASONS)[number]["value"];
export type ReportTarget = "recipe" | "comment" | "user";

export interface NewReport {
  target_type: ReportTarget;
  target_id: string;
  reason: ReportReason;
  note?: string | undefined;
}

export function createReport(payload: NewReport, token: string): Promise<unknown> {
  return request("/reports", z.unknown(), { method: "POST", body: payload, token });
}

export function blockUser(blockedId: string, token: string): Promise<unknown> {
  return request("/blocks", z.unknown(), {
    method: "POST",
    body: { blocked_id: blockedId },
    token,
  });
}

export function fetchBlocks(token: string): Promise<Block[]> {
  return request("/blocks", z.array(blockSchema), { token });
}

export function unblockUser(blockedId: string, token: string): Promise<void> {
  return request(`/blocks/${blockedId}`, z.void(), { method: "DELETE", token });
}
