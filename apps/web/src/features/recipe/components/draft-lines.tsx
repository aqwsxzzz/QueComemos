import { Trash2 } from "lucide-react";
import type { Dispatch } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

import type { DraftAction } from "../hooks/use-recipe-draft";

interface DraftLinesProps {
  list: "ingredients" | "steps";
  legend: string;
  hint: string;
  values: string[];
  dispatch: Dispatch<DraftAction>;
  addLabel: string;
  multiline?: boolean;
}

export function DraftLines({
  list,
  legend,
  hint,
  values,
  dispatch,
  addLabel,
  multiline = false,
}: DraftLinesProps): React.JSX.Element {
  const Control = multiline ? Textarea : Input;

  return (
    <fieldset className="space-y-3">
      <legend className="text-lg font-medium">{legend}</legend>
      <p className="text-sm text-muted-foreground">{hint}</p>

      {values.map((value, index) => (
        // Index keys are correct here: rows have no stable identity until
        // saved, and reordering is not supported in this form.
        <div key={index} className="flex items-start gap-2">
          <span className="w-6 shrink-0 pt-2.5 text-sm text-muted-foreground">{index + 1}</span>
          <Control
            value={value}
            aria-label={`${legend} ${index + 1}`}
            onChange={(event: { target: { value: string } }) => {
              dispatch({ type: "line", list, index, value: event.target.value });
            }}
          />
          <Button
            type="button"
            variant="ghost"
            size="icon"
            aria-label={`Quitar ${legend.toLowerCase()} ${index + 1}`}
            disabled={values.length === 1}
            onClick={() => {
              dispatch({ type: "remove", list, index });
            }}
          >
            <Trash2 className="size-4" />
          </Button>
        </div>
      ))}

      <Button
        type="button"
        variant="secondary"
        onClick={() => {
          dispatch({ type: "add", list });
        }}
      >
        {addLabel}
      </Button>
    </fieldset>
  );
}
