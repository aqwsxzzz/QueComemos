import { useReducer, type Dispatch } from "react";

import type { RecipeDraft } from "../types/recipe-types";

export interface DraftState {
  title: string;
  intro: string;
  servings: string;
  minutes: string;
  sourceUrl: string;
  ingredients: string[];
  steps: string[];
}

export type DraftAction =
  | { type: "field"; field: "title" | "intro" | "servings" | "minutes" | "sourceUrl"; value: string }
  | { type: "line"; list: "ingredients" | "steps"; index: number; value: string }
  | { type: "add"; list: "ingredients" | "steps" }
  | { type: "remove"; list: "ingredients" | "steps"; index: number };

export const EMPTY_DRAFT: DraftState = {
  title: "",
  intro: "",
  servings: "",
  minutes: "",
  sourceUrl: "",
  ingredients: ["", "", ""],
  steps: ["", ""],
};

function replaceAt(values: string[], index: number, value: string): string[] {
  return values.map((current, position) => (position === index ? value : current));
}

function reducer(state: DraftState, action: DraftAction): DraftState {
  switch (action.type) {
    case "field":
      return { ...state, [action.field]: action.value };
    case "line":
      return { ...state, [action.list]: replaceAt(state[action.list], action.index, action.value) };
    case "add":
      return { ...state, [action.list]: [...state[action.list], ""] };
    case "remove":
      return {
        ...state,
        [action.list]: state[action.list].filter((_, position) => position !== action.index),
      };
    default: {
      const exhaustive: never = action;
      return exhaustive;
    }
  }
}

function toNumber(value: string): number | null {
  const parsed = Number(value);
  return value.trim() === "" || Number.isNaN(parsed) ? null : parsed;
}

/** Drops blank lines: an empty row is scaffolding, not content. */
export function toPayload(state: DraftState): RecipeDraft {
  return {
    title: state.title.trim(),
    intro: state.intro.trim() || null,
    servings: toNumber(state.servings),
    minutes: toNumber(state.minutes),
    source_url: state.sourceUrl.trim() || null,
    ingredients: state.ingredients
      .map((raw_text) => raw_text.trim())
      .filter(Boolean)
      .map((raw_text) => ({ raw_text })),
    steps: state.steps
      .map((text) => text.trim())
      .filter(Boolean)
      .map((text) => ({ text })),
  };
}

export function useRecipeDraft(initial: DraftState = EMPTY_DRAFT): [
  DraftState,
  Dispatch<DraftAction>,
] {
  return useReducer(reducer, initial);
}
