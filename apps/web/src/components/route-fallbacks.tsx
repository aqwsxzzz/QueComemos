import { Link } from "@tanstack/react-router";

import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

interface ErrorFallbackProps {
  error: Error;
  reset: () => void;
}

/** Shown when a route throws. `reset` retries the boundary without a reload. */
export function RouteError({ error, reset }: ErrorFallbackProps): React.JSX.Element {
  return (
    <main className="mx-auto flex flex-1 max-w-md flex-col justify-center gap-4 px-6 text-center">
      <h1 className="text-2xl font-semibold tracking-tight">Se nos quemó algo</h1>
      <p className="text-muted-foreground">
        No pudimos cargar esta página. Puede ser algo momentáneo.
      </p>
      {/* The message, not the stack: it can carry internals a cook should not see. */}
      <p className="text-sm text-muted-foreground">{error.message}</p>
      <div className="flex justify-center gap-2">
        <Button onClick={reset}>Reintentar</Button>
        <Button asChild variant="secondary">
          <Link to="/recetas">Ir a las recetas</Link>
        </Button>
      </div>
    </main>
  );
}

export function RouteNotFound(): React.JSX.Element {
  return (
    <main className="mx-auto flex flex-1 max-w-md flex-col justify-center gap-4 px-6 text-center">
      <h1 className="text-2xl font-semibold tracking-tight">Esto no existe</h1>
      <p className="text-muted-foreground">
        La página que buscás no está acá. Quizá cambió de lugar.
      </p>
      <div className="flex justify-center">
        <Button asChild>
          <Link to="/recetas">Ver las recetas</Link>
        </Button>
      </div>
    </main>
  );
}

/**
 * Sized like a real page rather than a centred spinner, so the swap to content
 * does not shift the layout.
 */
export function RouteSkeleton(): React.JSX.Element {
  return (
    <div className="mx-auto w-full max-w-3xl space-y-6 px-4 py-8" aria-busy="true">
      <Skeleton className="h-9 w-2/3" />
      <Skeleton className="h-5 w-full" />
      <div className="grid gap-4 sm:grid-cols-2">
        {["a", "b", "c", "d"].map((key) => (
          <Skeleton key={key} className="h-40 w-full" />
        ))}
      </div>
    </div>
  );
}
