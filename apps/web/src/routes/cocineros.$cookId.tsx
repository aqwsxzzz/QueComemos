import { createFileRoute } from "@tanstack/react-router";

import { useAuthStore } from "@/features/auth/store/auth-store";
import { RecipeGrid } from "@/features/recipe/components/recipe-grid";
import { CookProfile } from "@/features/social/components/cook-profile";

export const Route = createFileRoute("/cocineros/$cookId")({
  component: CookPage,
});

function CookPage() {
  const { cookId } = Route.useParams();
  const currentUserId = useAuthStore((state) => state.user?.id);

  return (
    <main className="mx-auto w-full max-w-3xl space-y-8 px-4 py-8">
      <CookProfile cookId={cookId} currentUserId={currentUserId} />

      <section className="space-y-4">
        <h2 className="text-xl font-semibold tracking-tight">Sus recetas</h2>
        {/* Filtered server-side by author — never the whole pool sliced here. */}
        <RecipeGrid
          query={{ author_id: cookId }}
          emptyMessage="Todavía no publicó ninguna receta."
        />
      </section>
    </main>
  );
}
