import { z } from "zod";

import { request } from "@/lib/api-client";

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
