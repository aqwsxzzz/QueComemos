import { z } from "zod";

export const cookSchema = z.object({
  id: z.string(),
  display_name: z.string(),
  bio: z.string().nullable(),
  created_at: z.string(),
});

export const recipeIngredientSchema = z.object({
  id: z.string(),
  /** Always what we render. The structured fields are for machine features. */
  raw_text: z.string(),
  quantity: z.number().nullable(),
  unit: z.string().nullable(),
  ingredient_id: z.string().nullable(),
  position: z.number(),
});

export const recipeStepSchema = z.object({
  id: z.string(),
  position: z.number(),
  text: z.string(),
});

export const recipeSummarySchema = z.object({
  id: z.string(),
  title: z.string(),
  intro: z.string().nullable(),
  servings: z.number().nullable(),
  minutes: z.number().nullable(),
  published_at: z.string().nullable(),
  author: cookSchema,
});

export const recipeSchema = recipeSummarySchema.extend({
  source_url: z.string().nullable(),
  ingredients: z.array(recipeIngredientSchema),
  steps: z.array(recipeStepSchema),
});

export const photoSchema = z.object({
  id: z.string(),
  step_id: z.string().nullable(),
  alt_text: z.string().nullable(),
  width: z.number(),
  height: z.number(),
  position: z.number(),
  urls: z.object({ thumb: z.string(), card: z.string(), full: z.string() }),
});

export const pageMetaSchema = z.object({
  page: z.number(),
  page_size: z.number(),
  total: z.number(),
  has_next: z.boolean(),
});

export const recipePageSchema = z.object({
  data: z.array(recipeSummarySchema),
  meta: pageMetaSchema,
});

export type Cook = z.infer<typeof cookSchema>;
export type RecipeIngredient = z.infer<typeof recipeIngredientSchema>;
export type RecipeStep = z.infer<typeof recipeStepSchema>;
export type RecipeSummary = z.infer<typeof recipeSummarySchema>;
export type Recipe = z.infer<typeof recipeSchema>;
export type Photo = z.infer<typeof photoSchema>;
export type RecipePage = z.infer<typeof recipePageSchema>;

export interface RecipeDraft {
  title: string;
  intro: string | null;
  servings: number | null;
  minutes: number | null;
  source_url: string | null;
  ingredients: { raw_text: string }[];
  steps: { text: string }[];
}

export interface PoolQuery {
  q?: string | undefined;
  author_id?: string | undefined;
  max_minutes?: number | undefined;
}
