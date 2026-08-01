import { createFileRoute, Link } from "@tanstack/react-router";

import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/features/auth/store/auth-store";

export const Route = createFileRoute("/")({
  component: HomePage,
});

function HomePage() {
  const user = useAuthStore((state) => state.user);

  return (
    <main className="mx-auto flex min-h-dvh max-w-2xl flex-col justify-center gap-6 px-6 py-12">
      <div className="space-y-3">
        <h1 className="text-3xl font-semibold tracking-tight">Que Comemos?</h1>
        <p className="text-muted-foreground">
          Recetas caseras compartidas entre personas que cocinan de verdad.
        </p>
      </div>

      {user ? (
        <div className="space-y-3">
          <p>
            Hola, <span className="font-medium">{user.display_name}</span>.
          </p>
          <Button asChild>
            <Link to="/perfil">Ver tu perfil</Link>
          </Button>
        </div>
      ) : (
        <div className="flex flex-wrap gap-3">
          <Button asChild>
            <Link to="/crear-cuenta">Crear cuenta</Link>
          </Button>
          <Button asChild variant="secondary">
            <Link to="/entrar">Entrar</Link>
          </Button>
        </div>
      )}
    </main>
  );
}
