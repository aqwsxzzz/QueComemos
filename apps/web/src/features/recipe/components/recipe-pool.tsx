import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";

import { usePool } from "../api/recipe-queries";
import { RecipeCard } from "./recipe-card";

export function RecipePool(): React.JSX.Element {
  const [term, setTerm] = useState("");
  const [query, setQuery] = useState<{ q?: string }>({});
  const { data, isPending, isError, fetchNextPage, hasNextPage, isFetchingNextPage } =
    usePool(query);

  const recipes = data?.pages.flatMap((page) => page.data) ?? [];
  const total = data?.pages[0]?.meta.total ?? 0;

  return (
    <div className="space-y-6">
      <form
        className="flex gap-2"
        onSubmit={(event) => {
          event.preventDefault();
          // Search is a server query param, never a filter over a loaded list.
          setQuery(term.trim() ? { q: term.trim() } : {});
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

      {isPending ? (
        <div className="grid gap-4 sm:grid-cols-2">
          {[0, 1, 2, 3].map((key) => (
            <Skeleton key={key} className="h-40 w-full" />
          ))}
        </div>
      ) : null}

      {isError ? (
        <p role="alert" className="text-destructive">
          No pudimos cargar las recetas.
        </p>
      ) : null}

      {!isPending && recipes.length === 0 ? (
        <p className="text-muted-foreground">
          {query.q ? "No encontramos nada con esa búsqueda." : "Todavía no hay recetas. Subí la primera."}
        </p>
      ) : null}

      <div className="grid gap-4 sm:grid-cols-2">
        {recipes.map((recipe) => (
          <RecipeCard key={recipe.id} recipe={recipe} />
        ))}
      </div>

      {hasNextPage ? (
        <Button
          variant="secondary"
          className="w-full"
          disabled={isFetchingNextPage}
          onClick={() => {
            void fetchNextPage();
          }}
        >
          {isFetchingNextPage ? "Cargando…" : `Ver más (${recipes.length} de ${total})`}
        </Button>
      ) : null}
    </div>
  );
}
