import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";

import { useRecipe, useRecipePhotos } from "../api/recipe-queries";
import { RecipeSteps } from "./recipe-steps";
import { SourceLink } from "./source-link";

export function RecipeDetail({ recipeId }: { recipeId: string }): React.JSX.Element {
  const { data: recipe, isPending, isError } = useRecipe(recipeId);
  const { data: photos } = useRecipePhotos(recipeId);

  if (isPending) {
    return <Skeleton className="h-96 w-full" />;
  }
  if (isError) {
    return (
      <p role="alert" className="text-destructive">
        No encontramos esta receta.
      </p>
    );
  }

  const allPhotos = photos ?? [];
  const cover = allPhotos.find((photo) => photo.step_id === null);

  return (
    <article className="space-y-8">
      <header className="space-y-3">
        <h1 className="text-3xl font-semibold tracking-tight">{recipe.title}</h1>
        <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
          <span>Por {recipe.author.display_name}</span>
          {recipe.minutes ? <Badge variant="secondary">{recipe.minutes} min</Badge> : null}
          {recipe.servings ? <Badge variant="secondary">{recipe.servings} porciones</Badge> : null}
        </div>
        {recipe.intro ? <p className="whitespace-pre-line">{recipe.intro}</p> : null}
        {recipe.source_url ? <SourceLink url={recipe.source_url} /> : null}
      </header>

      {cover ? (
        <img
          src={cover.urls.full}
          alt={cover.alt_text ?? recipe.title}
          width={cover.width}
          height={cover.height}
          className="w-full rounded-xl border border-border object-cover"
        />
      ) : null}

      <section className="space-y-3">
        <h2 className="text-xl font-medium">Ingredientes</h2>
        <ul className="space-y-1">
          {recipe.ingredients.map((ingredient) => (
            // raw_text is always what the author typed — never reconstructed
            // from quantity + unit + canonical name.
            <li key={ingredient.id} className="border-b border-border/60 py-1.5">
              {ingredient.raw_text}
            </li>
          ))}
        </ul>
      </section>

      <Separator />

      <section className="space-y-4">
        <h2 className="text-xl font-medium">Preparación</h2>
        <RecipeSteps steps={recipe.steps} photos={allPhotos} />
      </section>
    </article>
  );
}
