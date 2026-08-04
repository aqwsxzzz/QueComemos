import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseMutationResult,
  type UseQueryResult,
} from "@tanstack/react-query";

import { useAuthStore } from "@/features/auth/store/auth-store";

import type { Cook } from "@/features/recipe/types/recipe-types";

import {
  addFavorite,
  createComment,
  fetchComments,
  fetchCook,
  fetchFavorites,
  fetchFollowStatus,
  fetchFollowers,
  fetchFollowing,
  follow,
  removeFavorite,
  unfollow,
} from "./social-api";
import type {
  CommentPage,
  CookPage,
  FavoritePage,
  FollowStatus,
  NewComment,
} from "../types/social-types";

export const socialKeys = {
  cook: (cookId: string) => ["social", "cook", cookId] as const,
  follow: (cookId: string) => ["social", "follow", cookId] as const,
  following: (page: number) => ["social", "following", page] as const,
  followers: (page: number) => ["social", "followers", page] as const,
  favorites: (page: number) => ["social", "favorites", page] as const,
  comments: (recipeId: string) => ["social", "comments", recipeId] as const,
};

function useToken(): string {
  return useAuthStore((state) => state.tokens?.access_token) ?? "";
}

export function useCook(cookId: string): UseQueryResult<Cook> {
  return useQuery({
    queryKey: socialKeys.cook(cookId),
    queryFn: () => fetchCook(cookId),
  });
}

export function useFollowing(page: number): UseQueryResult<CookPage> {
  const token = useToken();
  return useQuery({
    queryKey: socialKeys.following(page),
    queryFn: () => fetchFollowing(page, token),
    enabled: Boolean(token),
  });
}

export function useFollowers(page: number): UseQueryResult<CookPage> {
  const token = useToken();
  return useQuery({
    queryKey: socialKeys.followers(page),
    queryFn: () => fetchFollowers(page, token),
    enabled: Boolean(token),
  });
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
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: socialKeys.follow(cookId) });
      // The "Siguiendo" list is derived from the same edge — leaving it cached
      // shows someone you just unfollowed.
      await queryClient.invalidateQueries({ queryKey: ["social", "following"] });
    },
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
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["social", "favorites"] });
      // Saving moves `favorites_count`, which every recipe payload carries, so
      // the pool and the detail page would otherwise show a stale number.
      await queryClient.invalidateQueries({ queryKey: ["recipes"] });
    },
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
