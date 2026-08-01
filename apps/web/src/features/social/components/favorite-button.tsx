import { Bookmark } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";

import { useToggleFavorite } from "../api/social-queries";

interface FavoriteButtonProps {
  recipeId: string;
  /** Whether it is already saved, when the caller knows. */
  initiallySaved?: boolean;
}

export function FavoriteButton({
  recipeId,
  initiallySaved = false,
}: FavoriteButtonProps): React.JSX.Element {
  const [saved, setSaved] = useState(initiallySaved);
  const { mutate: toggle, isPending } = useToggleFavorite(recipeId);

  return (
    <Button
      variant={saved ? "secondary" : "default"}
      size="sm"
      disabled={isPending}
      aria-pressed={saved}
      onClick={() => {
        // The endpoint is idempotent both ways, so flipping optimistically is
        // safe: a failed call re-renders from the server on the next fetch.
        toggle(saved);
        setSaved(!saved);
      }}
    >
      <Bookmark className="size-4" />
      {saved ? "Guardada" : "Guardar"}
    </Button>
  );
}
