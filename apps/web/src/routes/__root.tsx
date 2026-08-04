import { createRootRoute, Outlet } from "@tanstack/react-router";

import { AppNav } from "@/components/app-nav";

export const Route = createRootRoute({
  // A no-op loader is what makes pending UI fire for every descendant route —
  // without it, slow navigations leave the previous page frozen.
  loader: () => null,
  component: RootLayout,
});

function RootLayout() {
  return (
    <div className="bg-background text-foreground">
      <AppNav />
      {/* Padding clears the fixed nav — bottom bar on phones, top bar from sm up.
          Children stretch with flex-1 instead of their own min-h-dvh, which
          would overflow by exactly the height of this padding. */}
      <div className="flex min-h-dvh flex-col pb-20 sm:pb-0 sm:pt-16">
        <Outlet />
      </div>
    </div>
  );
}
