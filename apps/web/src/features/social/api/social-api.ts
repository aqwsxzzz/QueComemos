import { z } from "zod";

import { request } from "@/lib/api-client";

import {
  commentPageSchema,
  favoritePageSchema,
  followStatusSchema,
  type CommentPage,
  type FavoritePage,
  type FollowStatus,
  type NewComment,
} from "../types/social-types";

export function fetchFollowStatus(cookId: string, token: string): Promise<FollowStatus> {
  return request(`/cooks/${cookId}/follow`, followStatusSchema, { token });
}

export function follow(cookId: string, token: string): Promise<void> {
  return request(`/cooks/${cookId}/follow`, z.void(), { method: "PUT", token });
}

export function unfollow(cookId: string, token: string): Promise<void> {
  return request(`/cooks/${cookId}/follow`, z.void(), { method: "DELETE", token });
}

export function addFavorite(recipeId: string, token: string): Promise<void> {
  return request(`/recipes/${recipeId}/favorite`, z.void(), { method: "PUT", token });
}

export function removeFavorite(recipeId: string, token: string): Promise<void> {
  return request(`/recipes/${recipeId}/favorite`, z.void(), { method: "DELETE", token });
}

export function fetchFavorites(page: number, token: string): Promise<FavoritePage> {
  return request(`/me/favorites?page=${page}&page_size=12`, favoritePageSchema, { token });
}

export function fetchComments(recipeId: string, page: number): Promise<CommentPage> {
  return request(`/recipes/${recipeId}/comments?page=${page}&page_size=20`, commentPageSchema);
}

export function createComment(
  recipeId: string,
  payload: NewComment,
  token: string,
): Promise<unknown> {
  return request(`/recipes/${recipeId}/comments`, z.unknown(), {
    method: "POST",
    body: payload,
    token,
  });
}
