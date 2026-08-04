import { createFileRoute, redirect } from "@tanstack/react-router";

import { useAuthStore } from "@/features/auth/store/auth-store";
import { useFollowers, useFollowing } from "@/features/social/api/social-queries";
import { CookList } from "@/features/social/components/cook-list";

export const Route = createFileRoute("/comunidad")({
  beforeLoad: () => {
    if (!useAuthStore.getState().tokens) {
      throw redirect({ to: "/entrar" });
    }
  },
  component: CommunityPage,
});

function CommunityPage() {
  const following = useFollowing(1);
  const followers = useFollowers(1);

  return (
    <main className="mx-auto w-full max-w-3xl space-y-10 px-4 py-8">
      <h1 className="text-2xl font-semibold tracking-tight">Tu comunidad</h1>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold tracking-tight">Seguís a</h2>
        <CookList
          cooks={following.data?.data}
          isPending={following.isPending}
          isError={following.isError}
          emptyMessage="Todavía no seguís a nadie. Entrá a una receta y seguí a quien la cocinó."
        />
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold tracking-tight">Te siguen</h2>
        <CookList
          cooks={followers.data?.data}
          isPending={followers.isPending}
          isError={followers.isError}
          emptyMessage="Todavía no te sigue nadie."
        />
      </section>
    </main>
  );
}
