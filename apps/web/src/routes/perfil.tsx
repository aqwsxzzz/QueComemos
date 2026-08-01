import { createFileRoute, redirect } from "@tanstack/react-router";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useLogout, useMe } from "@/features/auth/api/auth-queries";
import { useAuthStore } from "@/features/auth/store/auth-store";

export const Route = createFileRoute("/perfil")({
  beforeLoad: () => {
    if (!useAuthStore.getState().tokens) {
      throw redirect({ to: "/entrar" });
    }
  },
  component: ProfilePage,
});

function ProfilePage() {
  const { data: user, isPending, isError } = useMe();
  const { mutate: signOut, isPending: signingOut } = useLogout();

  return (
    <main className="mx-auto w-full max-w-2xl px-4 py-10">
      <Card>
        <CardHeader>
          <CardTitle>Tu perfil</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {isPending ? <p className="text-muted-foreground">Cargando…</p> : null}
          {isError ? (
            <p role="alert" className="text-destructive">
              No pudimos cargar tu perfil.
            </p>
          ) : null}
          {user ? (
            <dl className="space-y-2">
              <div>
                <dt className="text-sm text-muted-foreground">Nombre</dt>
                <dd className="text-lg">{user.display_name}</dd>
              </div>
              <div>
                <dt className="text-sm text-muted-foreground">Email</dt>
                <dd>{user.email}</dd>
              </div>
            </dl>
          ) : null}
          <Button
            variant="secondary"
            onClick={() => {
              signOut();
            }}
            disabled={signingOut}
          >
            Cerrar sesión
          </Button>
        </CardContent>
      </Card>
    </main>
  );
}
