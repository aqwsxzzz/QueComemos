import { Link } from "@tanstack/react-router";

import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import type { Cook } from "@/features/recipe/types/recipe-types";

interface CookListProps {
  cooks: Cook[] | undefined;
  isPending: boolean;
  isError: boolean;
  emptyMessage: string;
}

/** Renders a page of cooks, each linking to their profile. */
export function CookList({
  cooks,
  isPending,
  isError,
  emptyMessage,
}: CookListProps): React.JSX.Element {
  if (isPending) {
    return <Skeleton className="h-24 w-full" />;
  }

  if (isError) {
    return (
      <p role="alert" className="text-destructive">
        No pudimos cargar esta lista.
      </p>
    );
  }

  if (!cooks || cooks.length === 0) {
    return <p className="text-muted-foreground">{emptyMessage}</p>;
  }

  return (
    <ul className="grid gap-3 sm:grid-cols-2">
      {cooks.map((cook) => (
        <li key={cook.id}>
          <Card className="transition-colors hover:border-primary/40">
            <CardContent className="pt-6">
              <Link
                to="/cocineros/$cookId"
                params={{ cookId: cook.id }}
                className="font-medium hover:underline"
              >
                {cook.display_name}
              </Link>
              {cook.bio ? (
                <p className="line-clamp-2 text-sm text-muted-foreground">{cook.bio}</p>
              ) : null}
            </CardContent>
          </Card>
        </li>
      ))}
    </ul>
  );
}
