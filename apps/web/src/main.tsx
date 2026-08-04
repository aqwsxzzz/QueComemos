import { QueryClientProvider } from "@tanstack/react-query";
import { createRouter, RouterProvider } from "@tanstack/react-router";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { RouteError, RouteNotFound, RouteSkeleton } from "@/components/route-fallbacks";
import { createQueryClient } from "@/lib/query-client";
import { routeTree } from "@/routeTree.gen";

import "./index.css";

const queryClient = createQueryClient();

const router = createRouter({
  routeTree,
  defaultPreload: "intent",
  // TanStack Query owns caching; this stops the router's own preload cache
  // from competing with it.
  defaultPreloadStaleTime: 0,
  // Set here so no route can ship without pending, error and not-found UI.
  defaultPendingComponent: RouteSkeleton,
  defaultErrorComponent: RouteError,
  defaultNotFoundComponent: RouteNotFound,
});

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}

const container = document.getElementById("root");
if (!container) {
  throw new Error("Falta el elemento #root en index.html");
}

createRoot(container).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </StrictMode>,
);
