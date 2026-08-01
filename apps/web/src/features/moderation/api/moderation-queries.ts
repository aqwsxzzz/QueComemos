import { useMutation, type UseMutationResult } from "@tanstack/react-query";

import { useAuthStore } from "@/features/auth/store/auth-store";

import { blockUser, createReport, type NewReport } from "./moderation-api";

function useToken(): string {
  return useAuthStore((state) => state.tokens?.access_token) ?? "";
}

export function useReport(): UseMutationResult<unknown, Error, NewReport> {
  const token = useToken();
  return useMutation({ mutationFn: (payload: NewReport) => createReport(payload, token) });
}

export function useBlockUser(): UseMutationResult<unknown, Error, string> {
  const token = useToken();
  return useMutation({ mutationFn: (blockedId: string) => blockUser(blockedId, token) });
}
