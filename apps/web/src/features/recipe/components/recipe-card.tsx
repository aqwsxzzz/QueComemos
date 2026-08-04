import { Link } from "@tanstack/react-router";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

import type { RecipeSummary } from "../types/recipe-types";

export function RecipeCard({ recipe }: { recipe: RecipeSummary }): React.JSX.Element {
  return (
    // `relative` is load-bearing: the title link below paints an overlay with
    // after:inset-0, and without a positioned ancestor that overlay resolves
    // against the viewport and swallows every click on the page.
    <Card className="relative transition-colors hover:border-primary/40">
      <CardHeader>
        <CardTitle className="text-lg leading-snug">
          <Link
            to="/recetas/$recipeId"
            params={{ recipeId: recipe.id }}
            className="after:absolute after:inset-0"
          >
            {recipe.title}
          </Link>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {recipe.intro ? (
          <p className="line-clamp-2 text-sm text-muted-foreground">{recipe.intro}</p>
        ) : null}
        <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
          {/* `relative` lifts the author link above the title's click overlay,
              so it stays independently clickable inside the card. */}
          <Link
            to="/cocineros/$cookId"
            params={{ cookId: recipe.author.id }}
            className="relative hover:text-foreground hover:underline"
          >
            {recipe.author.display_name}
          </Link>
          {recipe.minutes ? <Badge variant="secondary">{recipe.minutes} min</Badge> : null}
          {recipe.servings ? <Badge variant="secondary">{recipe.servings} porciones</Badge> : null}
          {/* Hidden at zero: "0 guardados" on every card is noise, not signal. */}
          {recipe.favorites_count > 0 ? (
            <Badge variant="secondary">
              {recipe.favorites_count === 1
                ? "1 guardado"
                : `${String(recipe.favorites_count)} guardados`}
            </Badge>
          ) : null}
        </div>
      </CardContent>
    </Card>
  );
}
