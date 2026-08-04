import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

import { usePool } from "../api/recipe-queries";
import type { PoolQuery } from "../types/recipe-types";
import { RecipeCard } from "./recipe-card";

interface RecipeGridProps {
  query: PoolQuery;
  /** Shown when the query is valid but nothing came back. Wording is caller-specific. */
  emptyMessage: string;
}

/**
 * Renders one paginated pool query: loading, error, empty and "load more".
 *
 * Filtering lives in the query object, which goes to the server as params —
 * this component never slices an in-memory list.
 */
export function RecipeGrid({ query, emptyMessage }: RecipeGridProps): React.JSX.Element {
  const { data, isPending, isError, fetchNextPage, hasNextPage, isFetchingNextPage } =
    usePool(query);

  const recipes = data?.pages.flatMap((page) => page.data) ?? [];
  const total = data?.pages[0]?.meta.total ?? 0;

  if (isPending) {
    return (
      <div className="grid gap-4 sm:grid-cols-2">
        {[0, 1, 2, 3].map((key) => (
          <Skeleton key={key} className="h-40 w-full" />
        ))}
      </div>
    );
  }

  if (isError) {
    return (
      <p role="alert" className="text-destructive">
        No pudimos cargar las recetas.
      </p>
    );
  }

  if (recipes.length === 0) {
    return <p className="text-muted-foreground">{emptyMessage}</p>;
  }

  return (
    <div className="space-y-6">
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
