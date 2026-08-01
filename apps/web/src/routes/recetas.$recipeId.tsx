import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { useBlockUser } from "@/features/moderation/api/moderation-queries";
import { ReportAction } from "@/features/moderation/components/report-action";
import { useRecipe } from "@/features/recipe/api/recipe-queries";
import { PhotoUploader } from "@/features/recipe/components/photo-uploader";
import { RecipeDetail } from "@/features/recipe/components/recipe-detail";
import { CommentThread } from "@/features/social/components/comment-thread";
import { FavoriteButton } from "@/features/social/components/favorite-button";
import { FollowButton } from "@/features/social/components/follow-button";

export const Route = createFileRoute("/recetas/$recipeId")({
  component: RecipeDetailPage,
});

function RecipeDetailPage() {
  const { recipeId } = Route.useParams();
  const currentUserId = useAuthStore((state) => state.user?.id);
  const { data: recipe } = useRecipe(recipeId);
  const [questionStepId, setQuestionStepId] = useState<string | undefined>(undefined);
  const { mutate: blockAuthor } = useBlockUser();

  const isSignedIn = Boolean(currentUserId);
  const isAuthor = Boolean(recipe && currentUserId && recipe.author.id === currentUserId);

  return (
    <main className="mx-auto w-full max-w-2xl space-y-8 px-4 py-8">
      <Button asChild variant="ghost" size="sm">
        <Link to="/recetas">← Volver a las recetas</Link>
      </Button>

      <RecipeDetail recipeId={recipeId} />

      {recipe && isSignedIn ? (
        <div className="flex flex-wrap gap-2">
          <FavoriteButton recipeId={recipeId} />
          {!isAuthor ? <FollowButton cookId={recipe.author.id} /> : null}
        </div>
      ) : null}

      {isAuthor && recipe ? <PhotoUploader recipeId={recipeId} steps={recipe.steps} /> : null}

      {recipe && isSignedIn && !isAuthor ? (
        <ReportAction
          targetType="recipe"
          targetId={recipeId}
          authorId={recipe.author.id}
          onBlock={() => {
            blockAuthor(recipe.author.id);
          }}
        />
      ) : null}

      {recipe ? (
        <>
          {isSignedIn && !isAuthor ? (
            <div className="flex flex-wrap gap-2">
              <span className="w-full text-sm text-muted-foreground">
                ¿Hay un paso que no se entiende?
              </span>
              {recipe.steps.map((step, index) => (
                <Button
                  key={step.id}
                  variant={questionStepId === step.id ? "default" : "secondary"}
                  size="sm"
                  onClick={() => {
                    setQuestionStepId(questionStepId === step.id ? undefined : step.id);
                  }}
                >
                  Preguntar sobre el paso {index + 1}
                </Button>
              ))}
            </div>
          ) : null}

          <CommentThread
            recipeId={recipeId}
            steps={recipe.steps}
            canPost={isSignedIn}
            questionStepId={questionStepId}
          />
        </>
      ) : null}
    </main>
  );
}
