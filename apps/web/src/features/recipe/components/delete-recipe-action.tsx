import { useNavigate } from "@tanstack/react-router";
import { useState } from "react";

import { Button } from "@/components/ui/button";

import { useDeleteRecipe } from "../api/recipe-queries";

/**
 * Deleting is irreversible from the author's side, so it asks first rather
 * than firing on a single tap — easy to hit by accident on a phone.
 */
export function DeleteRecipeAction({ recipeId }: { recipeId: string }): React.JSX.Element {
  const navigate = useNavigate();
  const [confirming, setConfirming] = useState(false);
  const { mutate: deleteRecipe, isPending } = useDeleteRecipe();

  if (!confirming) {
    return (
      <Button
        variant="ghost"
        size="sm"
        onClick={() => {
          setConfirming(true);
        }}
      >
        Borrar esta receta
      </Button>
    );
  }

  return (
    <div className="space-y-3 rounded-lg border border-border p-4">
      <p className="text-sm font-medium">¿Borrar la receta?</p>
      <p className="text-sm text-muted-foreground">
        Deja de estar en el pool y no la vas a poder recuperar.
      </p>
      <div className="flex flex-wrap gap-2">
        <Button
          variant="destructive"
          size="sm"
          disabled={isPending}
          onClick={() => {
            deleteRecipe(recipeId, {
              onSuccess: () => {
                void navigate({ to: "/recetas" });
              },
            });
          }}
        >
          {isPending ? "Borrando…" : "Sí, borrarla"}
        </Button>
        <Button
          variant="ghost"
          size="sm"
          disabled={isPending}
          onClick={() => {
            setConfirming(false);
          }}
        >
          Cancelar
        </Button>
      </div>
    </div>
  );
}
