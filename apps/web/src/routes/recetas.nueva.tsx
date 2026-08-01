import { createFileRoute, redirect } from "@tanstack/react-router";

import { useAuthStore } from "@/features/auth/store/auth-store";
import { RecipeForm } from "@/features/recipe/components/recipe-form";

export const Route = createFileRoute("/recetas/nueva")({
  beforeLoad: () => {
    if (!useAuthStore.getState().tokens) {
      throw redirect({ to: "/entrar" });
    }
  },
  component: NewRecipePage,
});

function NewRecipePage() {
  return (
    <main className="mx-auto w-full max-w-2xl space-y-6 px-4 py-8">
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold tracking-tight">Subir una receta</h1>
        <p className="text-muted-foreground">
          Como la hacés vos. Sin fotos de estudio ni ingredientes imposibles.
        </p>
      </header>
      <RecipeForm />
    </main>
  );
}
