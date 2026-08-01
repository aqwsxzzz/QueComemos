import { useNavigate } from "@tanstack/react-router";
import { useActionState } from "react";

import { Button } from "@/components/ui/button";
import { ApiError } from "@/lib/api-client";
import { readField } from "@/lib/form-data";

import { useRegister } from "../api/auth-queries";
import { Field } from "./field";

interface FormState {
  error: string | null;
  fieldErrors: Record<string, string>;
}

const EMPTY: FormState = { error: null, fieldErrors: {} };

function toFieldErrors(error: ApiError): Record<string, string> {
  return Object.fromEntries(error.fieldErrors.map(({ field, message }) => [field, message]));
}

export function RegisterForm(): React.JSX.Element {
  const navigate = useNavigate();
  const { mutateAsync } = useRegister();

  const [state, submit, pending] = useActionState<FormState, FormData>(async (_, formData) => {
    try {
      await mutateAsync({
        email: readField(formData, "email"),
        password: readField(formData, "password"),
        display_name: readField(formData, "display_name"),
      });
      await navigate({ to: "/" });
      return EMPTY;
    } catch (error) {
      if (error instanceof ApiError) {
        return { error: error.message, fieldErrors: toFieldErrors(error) };
      }
      return { error: "No pudimos conectarnos. Revisá tu conexión.", fieldErrors: {} };
    }
  }, EMPTY);

  return (
    <form action={submit} className="space-y-4">
      <Field
        name="display_name"
        label="Cómo te llamás"
        autoComplete="nickname"
        required
        error={state.fieldErrors["display_name"]}
      />
      <Field
        name="email"
        label="Email"
        type="email"
        autoComplete="email"
        required
        error={state.fieldErrors["email"]}
      />
      <Field
        name="password"
        label="Contraseña"
        type="password"
        autoComplete="new-password"
        required
        hint="Mínimo 8 caracteres"
        error={state.fieldErrors["password"]}
      />
      {state.error ? (
        <p role="alert" className="text-sm text-destructive">
          {state.error}
        </p>
      ) : null}
      <Button type="submit" className="w-full" disabled={pending}>
        {pending ? "Creando cuenta…" : "Crear cuenta"}
      </Button>
    </form>
  );
}
