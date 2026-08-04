import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseMutationResult,
  type UseQueryResult,
} from "@tanstack/react-query";

import { useAuthStore } from "@/features/auth/store/auth-store";

import {
  blockUser,
  createReport,
  fetchBlocks,
  unblockUser,
  type Block,
  type NewReport,
} from "./moderation-api";

export const moderationKeys = {
  blocks: () => ["moderation", "blocks"] as const,
};

function useToken(): string {
  return useAuthStore((state) => state.tokens?.access_token) ?? "";
}

export function useReport(): UseMutationResult<unknown, Error, NewReport> {
  const token = useToken();
  return useMutation({ mutationFn: (payload: NewReport) => createReport(payload, token) });
}

export function useBlockUser(): UseMutationResult<unknown, Error, string> {
  const token = useToken();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (blockedId: string) => blockUser(blockedId, token),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: moderationKeys.blocks() });
      // Blocking hides that cook's recipes and severs the follow edge in both
      // directions, so the pool and the follow lists are both stale now.
      await queryClient.invalidateQueries({ queryKey: ["recipes"] });
      await queryClient.invalidateQueries({ queryKey: ["social"] });
    },
  });
}

export function useBlocks(): UseQueryResult<Block[]> {
  const token = useToken();
  return useQuery({
    queryKey: moderationKeys.blocks(),
    queryFn: () => fetchBlocks(token),
    enabled: Boolean(token),
  });
}

export function useUnblockUser(): UseMutationResult<void, Error, string> {
  const token = useToken();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (blockedId: string) => unblockUser(blockedId, token),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: moderationKeys.blocks() });
      await queryClient.invalidateQueries({ queryKey: ["recipes"] });
    },
  });
}
