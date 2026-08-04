import { createFileRoute, Link } from "@tanstack/react-router";

import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { RecipePool } from "@/features/recipe/components/recipe-pool";

export const Route = createFileRoute("/recetas/")({
  component: PoolPage,
});

function PoolPage() {
  const isSignedIn = Boolean(useAuthStore((state) => state.tokens));

  return (
    <main className="mx-auto w-full max-w-3xl space-y-6 px-4 py-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold tracking-tight">Recetas</h1>
        {isSignedIn ? (
          <Button asChild>
            <Link to="/recetas/nueva">Subir una receta</Link>
          </Button>
        ) : (
          <Button asChild variant="secondary">
            <Link to="/entrar">Entrar para publicar</Link>
          </Button>
        )}
      </div>
      <RecipePool />
    </main>
  );
}
