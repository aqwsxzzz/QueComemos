import type { ReactNode } from "react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface AuthFormShellProps {
  title: string;
  description: string;
  children: ReactNode;
  footer: ReactNode;
}

/** Shared chrome for the two auth screens, so they stay visually identical. */
export function AuthFormShell({
  title,
  description,
  children,
  footer,
}: AuthFormShellProps): React.JSX.Element {
  return (
    <main className="flex min-h-dvh items-center justify-center px-4 py-10">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle className="text-2xl">{title}</CardTitle>
          <CardDescription>{description}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {children}
          <p className="text-center text-sm text-muted-foreground">{footer}</p>
        </CardContent>
      </Card>
    </main>
  );
}
