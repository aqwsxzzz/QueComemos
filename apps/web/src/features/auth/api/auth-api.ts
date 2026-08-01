import { z } from "zod";

import { request } from "@/lib/api-client";

import {
  authSessionSchema,
  tokenPairSchema,
  userSchema,
  type AuthSession,
  type Credentials,
  type Registration,
  type TokenPair,
  type User,
} from "../types/auth-types";

export function register(payload: Registration): Promise<AuthSession> {
  return request("/auth/register", authSessionSchema, { method: "POST", body: payload });
}

export function login(payload: Credentials): Promise<AuthSession> {
  return request("/auth/login", authSessionSchema, { method: "POST", body: payload });
}

export function refresh(refreshToken: string): Promise<TokenPair> {
  return request("/auth/refresh", tokenPairSchema, {
    method: "POST",
    body: { refresh_token: refreshToken },
  });
}

export function logout(refreshToken: string): Promise<void> {
  return request("/auth/logout", z.void(), {
    method: "POST",
    body: { refresh_token: refreshToken },
  });
}

export function readMe(token: string): Promise<User> {
  return request("/users/me", userSchema, { token });
}
