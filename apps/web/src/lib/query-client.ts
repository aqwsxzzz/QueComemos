import { QueryClient } from "@tanstack/react-query";

/** One client per app instance. Lists are server-paginated, so cached pages stay small. */
export function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 30_000,
        retry: 1,
        refetchOnWindowFocus: false,
      },
    },
  });
}
