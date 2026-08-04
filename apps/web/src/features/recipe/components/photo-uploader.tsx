import { useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { ApiError } from "@/lib/api-client";

import { useUploadPhoto } from "../api/recipe-queries";
import type { RecipeStep } from "../types/recipe-types";

interface PhotoUploaderProps {
  recipeId: string;
  steps: RecipeStep[];
}

/** Photos of the process, not just the finished plate — one per step if wanted. */
export function PhotoUploader({ recipeId, steps }: PhotoUploaderProps): React.JSX.Element {
  const inputRef = useRef<HTMLInputElement>(null);
  const [stepId, setStepId] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const { mutateAsync, isPending } = useUploadPhoto();

  async function handleFile(file: File): Promise<void> {
    setError(null);
    try {
      await mutateAsync({ recipeId, file, stepId: stepId || undefined });
      if (inputRef.current) inputRef.current.value = "";
    } catch (uploadError) {
      setError(
        uploadError instanceof ApiError ? uploadError.message : "No pudimos subir la foto.",
      );
    }
  }

  return (
    <div className="space-y-3 rounded-lg border border-border p-4">
      <p className="font-medium">Agregar una foto</p>

      <div className="flex flex-wrap gap-2">
        <Button
          type="button"
          variant={stepId === "" ? "default" : "secondary"}
          size="sm"
          onClick={() => {
            setStepId("");
          }}
        >
          Del plato
        </Button>
        {steps.map((step, index) => (
          <Button
            key={step.id}
            type="button"
            variant={stepId === step.id ? "default" : "secondary"}
            size="sm"
            onClick={() => {
              setStepId(step.id);
            }}
          >
            Paso {index + 1}
          </Button>
        ))}
      </div>

      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        disabled={isPending}
        aria-label="Elegir foto"
        className="block w-full text-sm file:mr-3 file:rounded-md file:border-0 file:bg-secondary file:px-3 file:py-2 file:text-secondary-foreground"
        onChange={(event) => {
          const file = event.target.files?.[0];
          if (file) void handleFile(file);
        }}
      />

      {isPending ? <p className="text-sm text-muted-foreground">Subiendo…</p> : null}
      {error ? (
        <p role="alert" className="text-sm text-destructive">
          {error}
        </p>
      ) : null}
    </div>
  );
}
