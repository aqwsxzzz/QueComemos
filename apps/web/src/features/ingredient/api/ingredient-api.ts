import { request } from "@/lib/api-client";

import { ingredientPageSchema, type IngredientPage } from "../types/ingredient-types";

/** Enough to fill the picker; the pool filters by one id at a time. */
const PAGE_SIZE = 10;

export function searchIngredients(term: string): Promise<IngredientPage> {
  const params = new URLSearchParams({ page: "1", page_size: String(PAGE_SIZE) });
  if (term) params.set("q", term);
  return request(`/ingredients?${params.toString()}`, ingredientPageSchema);
}
