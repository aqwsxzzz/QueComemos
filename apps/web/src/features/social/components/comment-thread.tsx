import { useActionState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import type { RecipeStep } from "@/features/recipe/types/recipe-types";
import { ApiError } from "@/lib/api-client";
import { readField } from "@/lib/form-data";

import { useComments, useCreateComment } from "../api/social-queries";

interface CommentThreadProps {
  recipeId: string;
  steps: RecipeStep[];
  canPost: boolean;
  /** Pre-selects a step, which is how the "no entiendo este paso" flow starts. */
  questionStepId?: string | undefined;
}

interface FormState {
  error: string | null;
}

const EMPTY: FormState = { error: null };

export function CommentThread({
  recipeId,
  steps,
  canPost,
  questionStepId,
}: CommentThreadProps): React.JSX.Element {
  const { data, isPending } = useComments(recipeId);
  const { mutateAsync } = useCreateComment(recipeId);

  const [state, submit, pending] = useActionState<FormState, FormData>(async (_, formData) => {
    const body = readField(formData, "body").trim();
    if (!body) {
      return { error: "Escribí algo primero." };
    }
    try {
      await mutateAsync({
        body,
        kind: questionStepId ? "question" : "comment",
        step_id: questionStepId,
      });
      return EMPTY;
    } catch (error) {
      return {
        error: error instanceof ApiError ? error.message : "No pudimos publicar tu comentario.",
      };
    }
  }, EMPTY);

  const stepNumber = (stepId: string | null): number | null => {
    const index = steps.findIndex((step) => step.id === stepId);
    return index === -1 ? null : index + 1;
  };

  return (
    <section className="space-y-4">
      <h2 className="text-xl font-medium">Comentarios</h2>

      {canPost ? (
        <form action={submit} className="space-y-2">
          <Textarea
            name="body"
            rows={3}
            aria-label="Tu comentario"
            placeholder={
              questionStepId ? "¿Qué parte no se entiende?" : "Contá cómo te salió, qué cambiarías…"
            }
          />
          {state.error ? (
            <p role="alert" className="text-sm text-destructive">
              {state.error}
            </p>
          ) : null}
          <Button type="submit" size="sm" disabled={pending}>
            {pending ? "Publicando…" : questionStepId ? "Preguntar" : "Comentar"}
          </Button>
        </form>
      ) : null}

      {isPending ? <p className="text-muted-foreground">Cargando comentarios…</p> : null}

      {data?.data.length === 0 ? (
        <p className="text-muted-foreground">Todavía no hay comentarios.</p>
      ) : null}

      <ul className="space-y-4">
        {data?.data.map((comment) => (
          <li key={comment.id} className="space-y-1 border-b border-border/60 pb-3">
            <div className="flex flex-wrap items-center gap-2 text-sm">
              <span className="font-medium">{comment.author.display_name}</span>
              {comment.kind === "question" ? (
                <Badge variant="secondary">
                  Pregunta{stepNumber(comment.step_id) ? ` · paso ${stepNumber(comment.step_id)}` : ""}
                </Badge>
              ) : null}
            </div>
            {/* Plain text on purpose: user prose is never linkified. */}
            <p className="whitespace-pre-line">{comment.body}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
