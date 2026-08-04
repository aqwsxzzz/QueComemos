import {
  useInfiniteQuery,
  useMutation,
  useQuery,
  useQueryClient,
  type UseInfiniteQueryResult,
  type UseMutationResult,
  type UseQueryResult,
} from "@tanstack/react-query";

import { useAuthStore } from "@/features/auth/store/auth-store";

import type {
  Photo,
  PoolQuery,
  Recipe,
  RecipeDraft,
  RecipePage,
} from "../types/recipe-types";
import {
  createRecipe,
  deleteRecipe,
  fetchPhotos,
  fetchPool,
  fetchRecipe,
  updateRecipe,
  uploadPhoto,
  type PhotoUpload,
} from "./recipe-api";

export const recipeKeys = {
  pool: (query: PoolQuery) => ["recipes", "pool", query] as const,
  detail: (id: string) => ["recipes", "detail", id] as const,
  photos: (id: string) => ["recipes", "photos", id] as const,
};

function useToken(): string {
  return useAuthStore((state) => state.tokens?.access_token) ?? "";
}

/**
 * The pool is paginated server-side and always can grow, so it is fetched a
 * page at a time. Filtering and search are query params, never a client-side
 * pass over an in-memory list.
 */
export function usePool(query: PoolQuery): UseInfiniteQueryResult<{ pages: RecipePage[] }> {
  return useInfiniteQuery({
    queryKey: recipeKeys.pool(query),
    queryFn: ({ pageParam }) => fetchPool(query, pageParam),
    initialPageParam: 1,
    getNextPageParam: (lastPage) => (lastPage.meta.has_next ? lastPage.meta.page + 1 : undefined),
  });
}

export function useRecipe(recipeId: string): UseQueryResult<Recipe> {
  return useQuery({
    queryKey: recipeKeys.detail(recipeId),
    queryFn: () => fetchRecipe(recipeId),
  });
}

export function useRecipePhotos(recipeId: string): UseQueryResult<Photo[]> {
  return useQuery({
    queryKey: recipeKeys.photos(recipeId),
    queryFn: () => fetchPhotos(recipeId),
  });
}

export function useCreateRecipe(): UseMutationResult<Recipe, Error, RecipeDraft> {
  const token = useToken();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (draft: RecipeDraft) => createRecipe(draft, token),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["recipes", "pool"] }),
  });
}

export function useUpdateRecipe(
  recipeId: string,
): UseMutationResult<Recipe, Error, Partial<RecipeDraft>> {
  const token = useToken();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (draft: Partial<RecipeDraft>) => updateRecipe(recipeId, draft, token),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["recipes"] }),
  });
}

export function useDeleteRecipe(): UseMutationResult<void, Error, string> {
  const token = useToken();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (recipeId: string) => deleteRecipe(recipeId, token),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["recipes"] }),
  });
}

export function useUploadPhoto(): UseMutationResult<Photo, Error, PhotoUpload> {
  const token = useToken();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (upload: PhotoUpload) => uploadPhoto(upload, token),
    onSuccess: (_, upload) =>
      queryClient.invalidateQueries({ queryKey: recipeKeys.photos(upload.recipeId) }),
  });
}
