import { Link } from "@tanstack/react-router";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

import type { RecipeSummary } from "../types/recipe-types";

export function RecipeCard({ recipe }: { recipe: RecipeSummary }): React.JSX.Element {
  return (
    <Card className="transition-colors hover:border-primary/40">
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
          <span>{recipe.author.display_name}</span>
          {recipe.minutes ? <Badge variant="secondary">{recipe.minutes} min</Badge> : null}
          {recipe.servings ? <Badge variant="secondary">{recipe.servings} porciones</Badge> : null}
        </div>
      </CardContent>
    </Card>
  );
}
