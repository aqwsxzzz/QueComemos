import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { IngredientPicker } from "@/features/ingredient/components/ingredient-picker";
import type { Ingredient } from "@/features/ingredient/types/ingredient-types";

import type { PoolQuery } from "../types/recipe-types";
import { RecipeGrid } from "./recipe-grid";

const NOTHING_FOUND = "No encontramos nada con esa búsqueda.";
const POOL_EMPTY = "Todavía no hay recetas. Subí la primera.";

/** The public pool: free-text search plus a canonical-ingredient filter. */
export function RecipePool(): React.JSX.Element {
  const [term, setTerm] = useState("");
  const [search, setSearch] = useState<string | undefined>(undefined);
  const [ingredient, setIngredient] = useState<Ingredient | null>(null);

  // Both filters are server query params — the grid re-fetches when they
  // change, it never slices a list it already loaded.
  const query: PoolQuery = {
    ...(search ? { q: search } : {}),
    ...(ingredient ? { ingredient_id: ingredient.id } : {}),
  };
  const isFiltered = Boolean(search ?? ingredient);

  return (
    <div className="space-y-6">
      <form
        className="flex gap-2"
        onSubmit={(event) => {
          event.preventDefault();
          setSearch(term.trim() || undefined);
        }}
      >
        <Input
          value={term}
          onChange={(event) => {
            setTerm(event.target.value);
          }}
          placeholder="Buscar recetas…"
          aria-label="Buscar recetas"
        />
        <Button type="submit" variant="secondary">
          Buscar
        </Button>
      </form>

      <IngredientPicker selected={ingredient} onSelect={setIngredient} />

      <RecipeGrid query={query} emptyMessage={isFiltered ? NOTHING_FOUND : POOL_EMPTY} />
    </div>
  );
}
