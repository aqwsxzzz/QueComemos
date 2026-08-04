import { createFileRoute, Link, redirect } from "@tanstack/react-router";

import { AuthFormShell } from "@/features/auth/components/auth-form-shell";
import { RegisterForm } from "@/features/auth/components/register-form";
import { useAuthStore } from "@/features/auth/store/auth-store";

export const Route = createFileRoute("/crear-cuenta")({
  beforeLoad: () => {
    if (useAuthStore.getState().tokens) {
      throw redirect({ to: "/" });
    }
  },
  component: RegisterPage,
});

function RegisterPage() {
  return (
    <AuthFormShell
      title="Crear cuenta"
      description="Para compartir lo que cocinás de verdad, un martes cualquiera."
      footer={
        <>
          ¿Ya tenés cuenta?{" "}
          <Link to="/entrar" className="text-primary underline-offset-4 hover:underline">
            Entrá
          </Link>
        </>
      }
    >
      <RegisterForm />
    </AuthFormShell>
  );
}
