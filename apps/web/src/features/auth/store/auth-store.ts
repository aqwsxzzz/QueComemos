import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { AuthSession, TokenPair, User } from "../types/auth-types";

interface AuthState {
  user: User | null;
  tokens: TokenPair | null;
  setSession: (session: AuthSession) => void;
  setTokens: (tokens: TokenPair) => void;
  setUser: (user: User) => void;
  clear: () => void;
}

/**
 * Persisted so an installed PWA does not ask for a password on every cold
 * start. The access token is short-lived (15 min) and the refresh token is
 * revocable server-side, which is what actually ends a session.
 */
export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      tokens: null,
      setSession: (session) => {
        set({ user: session.user, tokens: session.tokens });
      },
      setTokens: (tokens) => {
        set({ tokens });
      },
      setUser: (user) => {
        set({ user });
      },
      clear: () => {
        set({ user: null, tokens: null });
      },
    }),
    { name: "quecomemos-auth" },
  ),
);

export function getAccessToken(): string | null {
  return useAuthStore.getState().tokens?.access_token ?? null;
}
