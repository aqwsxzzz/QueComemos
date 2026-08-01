import type { Dispatch } from "react";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

import type { DraftAction, DraftState } from "../hooks/use-recipe-draft";

interface RecipeBasicsProps {
  draft: DraftState;
  dispatch: Dispatch<DraftAction>;
}

export function RecipeBasics({ draft, dispatch }: RecipeBasicsProps): React.JSX.Element {
  return (
    <fieldset className="space-y-4">
      <legend className="text-lg font-medium">Lo básico</legend>

      <div className="space-y-2">
        <Label htmlFor="title">Título</Label>
        <Input
          id="title"
          value={draft.title}
          required
          onChange={(event) => {
            dispatch({ type: "field", field: "title", value: event.target.value });
          }}
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="intro">Contanos algo (opcional)</Label>
        <Textarea
          id="intro"
          rows={3}
          value={draft.intro}
          placeholder="Por qué la hacés, de dónde salió, qué le cambiás…"
          onChange={(event) => {
            dispatch({ type: "field", field: "intro", value: event.target.value });
          }}
        />
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="servings">Porciones</Label>
          <Input
            id="servings"
            type="number"
            min={1}
            value={draft.servings}
            onChange={(event) => {
              dispatch({ type: "field", field: "servings", value: event.target.value });
            }}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="minutes">Minutos</Label>
          <Input
            id="minutes"
            type="number"
            min={1}
            value={draft.minutes}
            onChange={(event) => {
              dispatch({ type: "field", field: "minutes", value: event.target.value });
            }}
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="sourceUrl">¿La sacaste de algún lado? (opcional)</Label>
        <Input
          id="sourceUrl"
          type="url"
          inputMode="url"
          value={draft.sourceUrl}
          placeholder="https://…"
          onChange={(event) => {
            dispatch({ type: "field", field: "sourceUrl", value: event.target.value });
          }}
        />
      </div>
    </fieldset>
  );
}
