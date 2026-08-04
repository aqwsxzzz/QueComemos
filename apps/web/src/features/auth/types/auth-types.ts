import { z } from "zod";

export const userSchema = z.object({
  id: z.string(),
  email: z.string(),
  display_name: z.string(),
  bio: z.string().nullable(),
  is_maintainer: z.boolean(),
  created_at: z.string(),
});

export const tokenPairSchema = z.object({
  access_token: z.string(),
  refresh_token: z.string(),
  token_type: z.string(),
});

export const authSessionSchema = z.object({
  user: userSchema,
  tokens: tokenPairSchema,
});

export type User = z.infer<typeof userSchema>;
export type TokenPair = z.infer<typeof tokenPairSchema>;
export type AuthSession = z.infer<typeof authSessionSchema>;

export interface Credentials {
  email: string;
  password: string;
}

export interface Registration extends Credentials {
  display_name: string;
}
