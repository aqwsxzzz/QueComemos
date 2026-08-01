import { useMutation, useQuery, type UseMutationResult, type UseQueryResult } from "@tanstack/react-query";

import { useAuthStore } from "../store/auth-store";
import type { AuthSession, Credentials, Registration, User } from "../types/auth-types";
import { login, logout, readMe, register } from "./auth-api";

export const authKeys = {
  me: ["auth", "me"] as const,
};

export function useRegister(): UseMutationResult<AuthSession, Error, Registration> {
  const setSession = useAuthStore((state) => state.setSession);
  return useMutation({
    mutationFn: register,
    onSuccess: setSession,
  });
}

export function useLogin(): UseMutationResult<AuthSession, Error, Credentials> {
  const setSession = useAuthStore((state) => state.setSession);
  return useMutation({
    mutationFn: login,
    onSuccess: setSession,
  });
}

export function useLogout(): UseMutationResult<void, Error, void> {
  const clear = useAuthStore((state) => state.clear);
  const refreshToken = useAuthStore((state) => state.tokens?.refresh_token);
  return useMutation({
    mutationFn: async () => {
      if (refreshToken) {
        await logout(refreshToken);
      }
    },
    // The local session is dropped either way: a failed revoke must not strand
    // the user in a half-logged-in state.
    onSettled: clear,
  });
}

export function useMe(): UseQueryResult<User> {
  const token = useAuthStore((state) => state.tokens?.access_token);
  return useQuery({
    queryKey: authKeys.me,
    queryFn: () => readMe(token as string),
    enabled: Boolean(token),
  });
}
