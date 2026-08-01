import { createFileRoute, Link } from "@tanstack/react-router";

import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { useRecipe } from "@/features/recipe/api/recipe-queries";
import { PhotoUploader } from "@/features/recipe/components/photo-uploader";
import { RecipeDetail } from "@/features/recipe/components/recipe-detail";

export const Route = createFileRoute("/recetas/$recipeId")({
  component: RecipeDetailPage,
});

function RecipeDetailPage() {
  const { recipeId } = Route.useParams();
  const currentUserId = useAuthStore((state) => state.user?.id);
  const { data: recipe } = useRecipe(recipeId);
  const isAuthor = Boolean(recipe && currentUserId && recipe.author.id === currentUserId);

  return (
    <main className="mx-auto w-full max-w-2xl space-y-8 px-4 py-8">
      <Button asChild variant="ghost" size="sm">
        <Link to="/recetas">← Volver a las recetas</Link>
      </Button>

      <RecipeDetail recipeId={recipeId} />

      {isAuthor && recipe ? <PhotoUploader recipeId={recipeId} steps={recipe.steps} /> : null}
    </main>
  );
}
