import { useNavigate } from "@tanstack/react-router";
import { useActionState } from "react";

import { Button } from "@/components/ui/button";
import { ApiError } from "@/lib/api-client";
import { readField } from "@/lib/form-data";

import { useLogin } from "../api/auth-queries";
import { Field } from "./field";

interface FormState {
  error: string | null;
}

const EMPTY: FormState = { error: null };

export function LoginForm(): React.JSX.Element {
  const navigate = useNavigate();
  const { mutateAsync } = useLogin();

  const [state, submit, pending] = useActionState<FormState, FormData>(async (_, formData) => {
    try {
      await mutateAsync({
        email: readField(formData, "email"),
        password: readField(formData, "password"),
      });
      await navigate({ to: "/" });
      return EMPTY;
    } catch (error) {
      if (error instanceof ApiError) {
        return { error: error.message };
      }
      return { error: "No pudimos conectarnos. Revisá tu conexión." };
    }
  }, EMPTY);

  return (
    <form action={submit} className="space-y-4">
      <Field name="email" label="Email" type="email" autoComplete="email" required />
      <Field
        name="password"
        label="Contraseña"
        type="password"
        autoComplete="current-password"
        required
      />
      {state.error ? (
        <p role="alert" className="text-sm text-destructive">
          {state.error}
        </p>
      ) : null}
      <Button type="submit" className="w-full" disabled={pending}>
        {pending ? "Entrando…" : "Entrar"}
      </Button>
    </form>
  );
}
