import { useQuery, type UseQueryResult } from "@tanstack/react-query";

import type { IngredientPage } from "../types/ingredient-types";
import { searchIngredients } from "./ingredient-api";

export const ingredientKeys = {
  search: (term: string) => ["ingredients", "search", term] as const,
};

/**
 * Matching happens server-side against names and regional aliases, so "palta"
 * and "aguacate" both find the same row. Never a filter over a loaded list.
 */
export function useIngredientSearch(term: string): UseQueryResult<IngredientPage> {
  return useQuery({
    queryKey: ingredientKeys.search(term),
    queryFn: () => searchIngredients(term),
    enabled: term.length >= 2,
  });
}
