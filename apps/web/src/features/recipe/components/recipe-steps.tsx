import type { Photo, RecipeStep } from "../types/recipe-types";

interface RecipeStepsProps {
  steps: RecipeStep[];
  photos: Photo[];
}

/** Process photos hang off the step they illustrate — that is the whole point. */
export function RecipeSteps({ steps, photos }: RecipeStepsProps): React.JSX.Element {
  return (
    <ol className="space-y-6">
      {steps.map((step, index) => {
        const stepPhotos = photos.filter((photo) => photo.step_id === step.id);
        return (
          <li key={step.id} className="space-y-3">
            <div className="flex gap-3">
              <span className="flex size-7 shrink-0 items-center justify-center rounded-full bg-primary text-sm font-medium text-primary-foreground">
                {index + 1}
              </span>
              <p className="whitespace-pre-line pt-0.5">{step.text}</p>
            </div>
            {stepPhotos.length > 0 ? (
              <div className="grid gap-2 pl-10 sm:grid-cols-2">
                {stepPhotos.map((photo) => (
                  <img
                    key={photo.id}
                    src={photo.urls.card}
                    alt={photo.alt_text ?? `Paso ${index + 1}`}
                    width={photo.width}
                    height={photo.height}
                    loading="lazy"
                    className="w-full rounded-lg border border-border object-cover"
                  />
                ))}
              </div>
            ) : null}
          </li>
        );
      })}
    </ol>
  );
}
