import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseMutationResult,
  type UseQueryResult,
} from "@tanstack/react-query";

import { useAuthStore } from "@/features/auth/store/auth-store";

import {
  addFavorite,
  createComment,
  fetchComments,
  fetchFavorites,
  fetchFollowStatus,
  follow,
  removeFavorite,
  unfollow,
} from "./social-api";
import type { CommentPage, FavoritePage, FollowStatus, NewComment } from "../types/social-types";

export const socialKeys = {
  follow: (cookId: string) => ["social", "follow", cookId] as const,
  favorites: (page: number) => ["social", "favorites", page] as const,
  comments: (recipeId: string) => ["social", "comments", recipeId] as const,
};

function useToken(): string {
  return useAuthStore((state) => state.tokens?.access_token) ?? "";
}

export function useFollowStatus(cookId: string): UseQueryResult<FollowStatus> {
  const token = useToken();
  return useQuery({
    queryKey: socialKeys.follow(cookId),
    queryFn: () => fetchFollowStatus(cookId, token),
    enabled: Boolean(token),
  });
}

export function useToggleFollow(cookId: string): UseMutationResult<void, Error, boolean> {
  const token = useToken();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (isFollowed: boolean) =>
      isFollowed ? unfollow(cookId, token) : follow(cookId, token),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: socialKeys.follow(cookId) }),
  });
}

export function useFavorites(page: number): UseQueryResult<FavoritePage> {
  const token = useToken();
  return useQuery({
    queryKey: socialKeys.favorites(page),
    queryFn: () => fetchFavorites(page, token),
    enabled: Boolean(token),
  });
}

export function useToggleFavorite(recipeId: string): UseMutationResult<void, Error, boolean> {
  const token = useToken();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (isSaved: boolean) =>
      isSaved ? removeFavorite(recipeId, token) : addFavorite(recipeId, token),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["social", "favorites"] }),
  });
}

export function useComments(recipeId: string): UseQueryResult<CommentPage> {
  return useQuery({
    queryKey: socialKeys.comments(recipeId),
    queryFn: () => fetchComments(recipeId, 1),
  });
}

export function useCreateComment(recipeId: string): UseMutationResult<unknown, Error, NewComment> {
  const token = useToken();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: NewComment) => createComment(recipeId, payload, token),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: socialKeys.comments(recipeId) }),
  });
}
