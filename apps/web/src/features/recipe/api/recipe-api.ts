import { z } from "zod";

import { request, uploadFile } from "@/lib/api-client";

import {
  photoSchema,
  recipePageSchema,
  recipeSchema,
  type Photo,
  type PoolQuery,
  type Recipe,
  type RecipeDraft,
  type RecipePage,
} from "../types/recipe-types";

const PAGE_SIZE = 12;

/** Only the params that are actually set travel, per the tight-scoping rule. */
function poolSearchParams(query: PoolQuery, page: number): string {
  const params = new URLSearchParams({ page: String(page), page_size: String(PAGE_SIZE) });
  if (query.q) params.set("q", query.q);
  if (query.author_id) params.set("author_id", query.author_id);
  if (query.max_minutes !== undefined) params.set("max_minutes", String(query.max_minutes));
  return params.toString();
}

export function fetchPool(query: PoolQuery, page: number): Promise<RecipePage> {
  return request(`/recipes?${poolSearchParams(query, page)}`, recipePageSchema);
}

export function fetchRecipe(recipeId: string): Promise<Recipe> {
  return request(`/recipes/${recipeId}`, recipeSchema);
}

export function fetchPhotos(recipeId: string): Promise<Photo[]> {
  return request(`/recipes/${recipeId}/photos`, z.array(photoSchema));
}

export function createRecipe(draft: RecipeDraft, token: string): Promise<Recipe> {
  return request("/recipes", recipeSchema, { method: "POST", body: draft, token });
}

export function updateRecipe(
  recipeId: string,
  draft: Partial<RecipeDraft>,
  token: string,
): Promise<Recipe> {
  return request(`/recipes/${recipeId}`, recipeSchema, {
    method: "PATCH",
    body: draft,
    token,
  });
}

export function deleteRecipe(recipeId: string, token: string): Promise<void> {
  return request(`/recipes/${recipeId}`, z.void(), { method: "DELETE", token });
}

export interface PhotoUpload {
  recipeId: string;
  file: File;
  stepId?: string | undefined;
  altText?: string | undefined;
}

export function uploadPhoto(
  { recipeId, file, stepId, altText }: PhotoUpload,
  token: string,
): Promise<Photo> {
  const form = new FormData();
  form.append("file", file);
  if (stepId) form.append("step_id", stepId);
  if (altText) form.append("alt_text", altText);
  return uploadFile(`/recipes/${recipeId}/photos`, photoSchema, form, token);
}
