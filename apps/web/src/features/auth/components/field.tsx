import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface FieldProps {
  name: string;
  label: string;
  type?: "text" | "email" | "password";
  autoComplete?: string;
  required?: boolean;
  hint?: string;
  error?: string | undefined;
}

export function Field({
  name,
  label,
  type = "text",
  autoComplete,
  required,
  hint,
  error,
}: FieldProps): React.JSX.Element {
  const messageId = `${name}-message`;
  const message = error ?? hint;

  return (
    <div className="space-y-2">
      <Label htmlFor={name}>{label}</Label>
      <Input
        id={name}
        name={name}
        type={type}
        autoComplete={autoComplete}
        required={required}
        aria-invalid={error ? true : undefined}
        aria-describedby={message ? messageId : undefined}
      />
      {message ? (
        <p
          id={messageId}
          className={error ? "text-sm text-destructive" : "text-sm text-muted-foreground"}
        >
          {message}
        </p>
      ) : null}
    </div>
  );
}
