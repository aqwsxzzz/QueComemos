import { z } from "zod";

import { cookSchema, pageMetaSchema, recipeSummarySchema } from "@/features/recipe/types/recipe-types";

export const followStatusSchema = cookSchema.extend({
  is_followed: z.boolean(),
});

export const commentSchema = z.object({
  id: z.string(),
  body: z.string(),
  kind: z.enum(["comment", "question"]),
  step_id: z.string().nullable(),
  created_at: z.string(),
  author: cookSchema,
});

export const commentPageSchema = z.object({
  data: z.array(commentSchema),
  meta: pageMetaSchema,
});

export const favoritePageSchema = z.object({
  data: z.array(recipeSummarySchema),
  meta: pageMetaSchema,
});

export const cookPageSchema = z.object({
  data: z.array(cookSchema),
  meta: pageMetaSchema,
});

export type FollowStatus = z.infer<typeof followStatusSchema>;
export type Comment = z.infer<typeof commentSchema>;
export type CommentPage = z.infer<typeof commentPageSchema>;
export type FavoritePage = z.infer<typeof favoritePageSchema>;
export type CookPage = z.infer<typeof cookPageSchema>;

export interface NewComment {
  body: string;
  kind: "comment" | "question";
  step_id?: string | undefined;
}
