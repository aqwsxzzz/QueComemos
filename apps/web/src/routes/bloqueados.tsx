import { createFileRoute, redirect } from "@tanstack/react-router";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { useBlocks, useUnblockUser } from "@/features/moderation/api/moderation-queries";

export const Route = createFileRoute("/bloqueados")({
  beforeLoad: () => {
    if (!useAuthStore.getState().tokens) {
      throw redirect({ to: "/entrar" });
    }
  },
  component: BlockedPage,
});

function BlockedPage() {
  const { data: blocks, isPending, isError } = useBlocks();
  const { mutate: unblock, isPending: unblocking } = useUnblockUser();

  return (
    <main className="mx-auto w-full max-w-2xl space-y-6 px-4 py-8">
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold tracking-tight">Bloqueados</h1>
        <p className="text-muted-foreground">
          No ves sus recetas ni sus comentarios, y ellos no ven los tuyos.
        </p>
      </header>

      {isPending ? <Skeleton className="h-24 w-full" /> : null}

      {isError ? (
        <p role="alert" className="text-destructive">
          No pudimos cargar la lista.
        </p>
      ) : null}

      {blocks && blocks.length === 0 ? (
        <p className="text-muted-foreground">No bloqueaste a nadie.</p>
      ) : null}

      <ul className="space-y-3">
        {blocks?.map((block) => (
          <li key={block.id}>
            <Card>
              <CardContent className="flex flex-wrap items-center justify-between gap-3 pt-6">
                <span className="font-medium">{block.blocked.display_name}</span>
                <Button
                  variant="secondary"
                  size="sm"
                  disabled={unblocking}
                  onClick={() => {
                    unblock(block.blocked_id);
                  }}
                >
                  Desbloquear
                </Button>
              </CardContent>
            </Card>
          </li>
        ))}
      </ul>
    </main>
  );
}
