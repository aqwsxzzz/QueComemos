import { createFileRoute, Link, redirect } from "@tanstack/react-router";

import { AuthFormShell } from "@/features/auth/components/auth-form-shell";
import { LoginForm } from "@/features/auth/components/login-form";
import { useAuthStore } from "@/features/auth/store/auth-store";

export const Route = createFileRoute("/entrar")({
  beforeLoad: () => {
    if (useAuthStore.getState().tokens) {
      throw redirect({ to: "/" });
    }
  },
  component: LoginPage,
});

function LoginPage() {
  return (
    <AuthFormShell
      title="Entrar"
      description="Volvé a tus recetas y a las de la gente que seguís."
      footer={
        <>
          ¿Todavía no tenés cuenta?{" "}
          <Link to="/crear-cuenta" className="text-primary underline-offset-4 hover:underline">
            Creá una
          </Link>
        </>
      }
    >
      <LoginForm />
    </AuthFormShell>
  );
}
