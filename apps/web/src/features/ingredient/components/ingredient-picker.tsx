import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import { useIngredientSearch } from "../api/ingredient-queries";
import type { Ingredient } from "../types/ingredient-types";

interface IngredientPickerProps {
  selected: Ingredient | null;
  onSelect: (ingredient: Ingredient | null) => void;
}

/**
 * Picks one canonical ingredient to filter the pool by.
 *
 * Matching is server-side over names and regional aliases, so "palta" and
 * "aguacate" both resolve to the same id.
 */
export function IngredientPicker({
  selected,
  onSelect,
}: IngredientPickerProps): React.JSX.Element {
  const [term, setTerm] = useState("");
  const { data, isPending } = useIngredientSearch(term.trim());

  if (selected) {
    return (
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-sm text-muted-foreground">Con este ingrediente:</span>
        <Badge variant="secondary">{selected.name}</Badge>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => {
            setTerm("");
            onSelect(null);
          }}
        >
          Quitar filtro
        </Button>
      </div>
    );
  }

  const matches = data?.data ?? [];
  const searching = term.trim().length >= 2;

  return (
    <div className="space-y-2">
      <Input
        value={term}
        onChange={(event) => {
          setTerm(event.target.value);
        }}
        placeholder="Filtrar por ingrediente: pollo, palta, lentejas…"
        aria-label="Filtrar por ingrediente"
      />

      {searching && isPending ? (
        <p className="text-sm text-muted-foreground">Buscando ingredientes…</p>
      ) : null}

      {searching && !isPending && matches.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          No tenemos ese ingrediente todavía. Probá con otro nombre.
        </p>
      ) : null}

      <div className="flex flex-wrap gap-2">
        {matches.map((ingredient) => (
          <Button
            key={ingredient.id}
            variant="secondary"
            size="sm"
            onClick={() => {
              onSelect(ingredient);
            }}
          >
            {ingredient.name}
          </Button>
        ))}
      </div>
    </div>
  );
}
