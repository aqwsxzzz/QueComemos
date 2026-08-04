import { createFileRoute, redirect } from "@tanstack/react-router";

import { Skeleton } from "@/components/ui/skeleton";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { RecipeCard } from "@/features/recipe/components/recipe-card";
import { useFavorites } from "@/features/social/api/social-queries";

export const Route = createFileRoute("/guardadas")({
  beforeLoad: () => {
    if (!useAuthStore.getState().tokens) {
      throw redirect({ to: "/entrar" });
    }
  },
  component: SavedPage,
});

function SavedPage() {
  const { data, isPending, isError } = useFavorites(1);

  return (
    <main className="mx-auto w-full max-w-3xl space-y-6 px-4 py-8">
      <h1 className="text-2xl font-semibold tracking-tight">Guardadas</h1>

      {isPending ? <Skeleton className="h-40 w-full" /> : null}
      {isError ? (
        <p role="alert" className="text-destructive">
          No pudimos cargar tus recetas guardadas.
        </p>
      ) : null}
      {data?.data.length === 0 ? (
        <p className="text-muted-foreground">Todavía no guardaste ninguna receta.</p>
      ) : null}

      <div className="grid gap-4 sm:grid-cols-2">
        {data?.data.map((recipe) => (
          <RecipeCard key={recipe.id} recipe={recipe} />
        ))}
      </div>
    </main>
  );
}
