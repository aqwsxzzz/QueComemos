import { z } from "zod";

import { pageMetaSchema } from "@/features/recipe/types/recipe-types";

/** The curated taxonomy. Users never create these — see docs/ingredients-model.md. */
export const ingredientSchema = z.object({
  id: z.string(),
  name: z.string(),
  category: z.string().nullable(),
});

export const ingredientPageSchema = z.object({
  data: z.array(ingredientSchema),
  meta: pageMetaSchema,
});

export type Ingredient = z.infer<typeof ingredientSchema>;
export type IngredientPage = z.infer<typeof ingredientPageSchema>;
