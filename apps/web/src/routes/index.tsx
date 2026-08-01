import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  component: HomePage,
});

function HomePage() {
  return (
    <main className="mx-auto flex min-h-dvh max-w-2xl flex-col justify-center gap-4 px-6 py-12">
      <h1 className="text-3xl font-semibold tracking-tight">Que Comemos?</h1>
      <p className="text-muted-foreground">
        Recetas caseras compartidas entre personas que cocinan de verdad.
      </p>
    </main>
  );
}
