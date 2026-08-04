import { createFileRoute, redirect, useNavigate } from "@tanstack/react-router";

import { Skeleton } from "@/components/ui/skeleton";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { useRecipe, useUpdateRecipe } from "@/features/recipe/api/recipe-queries";
import { DeleteRecipeAction } from "@/features/recipe/components/delete-recipe-action";
import { RecipeForm } from "@/features/recipe/components/recipe-form";
import { toDraftState } from "@/features/recipe/hooks/use-recipe-draft";

// The trailing underscore on `$recipeId_` opts this route out of nesting under
// the detail route — without it, `recetas.$recipeId.tsx` silently becomes a
// layout that needs an <Outlet />, and the detail page renders blank.
export const Route = createFileRoute("/recetas/$recipeId_/editar")({
  beforeLoad: () => {
    if (!useAuthStore.getState().tokens) {
      throw redirect({ to: "/entrar" });
    }
  },
  component: EditRecipePage,
});

function EditRecipePage() {
  const { recipeId } = Route.useParams();
  const navigate = useNavigate();
  const currentUserId = useAuthStore((state) => state.user?.id);
  const { data: recipe, isPending, isError } = useRecipe(recipeId);
  const { mutateAsync: updateRecipe } = useUpdateRecipe(recipeId);

  if (isPending) {
    return (
      <main className="mx-auto w-full max-w-2xl px-4 py-8">
        <Skeleton className="h-96 w-full" />
      </main>
    );
  }

  if (isError) {
    return (
      <main className="mx-auto w-full max-w-2xl px-4 py-8">
        <p role="alert" className="text-destructive">
          No pudimos cargar esta receta.
        </p>
      </main>
    );
  }

  // Authorship is enforced by the API on PATCH and DELETE; this only keeps the
  // form from being shown to someone who cannot save it.
  if (recipe.author.id !== currentUserId) {
    return (
      <main className="mx-auto w-full max-w-2xl px-4 py-8">
        <p role="alert" className="text-destructive">
          Esta receta no es tuya.
        </p>
      </main>
    );
  }

  return (
    <main className="mx-auto w-full max-w-2xl space-y-8 px-4 py-8">
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold tracking-tight">Editar receta</h1>
        <p className="text-muted-foreground">Cambiá lo que haga falta y guardá.</p>
      </header>

      {/* `key` remounts the editor if the identity changes, so the draft never
          carries another recipe's text. */}
      <RecipeForm
        key={recipe.id}
        initial={toDraftState(recipe)}
        submitLabel="Guardar cambios"
        pendingLabel="Guardando…"
        onSave={async (payload) => {
          await updateRecipe(payload);
          await navigate({ to: "/recetas/$recipeId", params: { recipeId } });
        }}
      />

      <DeleteRecipeAction recipeId={recipeId} />
    </main>
  );
}
