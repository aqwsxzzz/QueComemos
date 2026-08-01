import { useNavigate } from "@tanstack/react-router";
import { useActionState } from "react";

import { Button } from "@/components/ui/button";
import { ApiError } from "@/lib/api-client";

import { useCreateRecipe } from "../api/recipe-queries";
import { toPayload, useRecipeDraft } from "../hooks/use-recipe-draft";
import { DraftLines } from "./draft-lines";
import { RecipeBasics } from "./recipe-basics";

interface FormState {
  error: string | null;
}

const EMPTY: FormState = { error: null };

/**
 * Authoring is the one flow that has to be comfortable on a large screen, so
 * the whole recipe is one page rather than a mobile-style wizard. It stays
 * usable on a phone because the sections simply stack.
 */
export function RecipeForm(): React.JSX.Element {
  const navigate = useNavigate();
  const [draft, dispatch] = useRecipeDraft();
  const { mutateAsync } = useCreateRecipe();

  const [state, submit, pending] = useActionState<FormState>(async () => {
    const payload = toPayload(draft);
    if (payload.ingredients.length === 0 || payload.steps.length === 0) {
      return { error: "Hace falta al menos un ingrediente y un paso." };
    }
    try {
      const recipe = await mutateAsync(payload);
      await navigate({ to: "/recetas/$recipeId", params: { recipeId: recipe.id } });
      return EMPTY;
    } catch (error) {
      if (error instanceof ApiError) {
        return { error: error.message };
      }
      return { error: "No pudimos guardar la receta. Probá de nuevo." };
    }
  }, EMPTY);

  return (
    <form action={submit} className="space-y-10">
      <RecipeBasics draft={draft} dispatch={dispatch} />

      <DraftLines
        list="ingredients"
        legend="Ingredientes"
        hint="Escribilos como los dirías: “2 tomates”, “sal a gusto”, “media taza de harina”."
        values={draft.ingredients}
        dispatch={dispatch}
        addLabel="Agregar ingrediente"
      />

      <DraftLines
        list="steps"
        legend="Pasos"
        hint="Un paso por renglón. Después vas a poder subirle una foto a cada uno."
        values={draft.steps}
        dispatch={dispatch}
        addLabel="Agregar paso"
        multiline
      />

      {state.error ? (
        <p role="alert" className="text-sm text-destructive">
          {state.error}
        </p>
      ) : null}

      <Button type="submit" size="lg" disabled={pending}>
        {pending ? "Publicando…" : "Publicar receta"}
      </Button>
    </form>
  );
}
