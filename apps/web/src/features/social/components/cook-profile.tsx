import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useBlockUser } from "@/features/moderation/api/moderation-queries";
import { ReportAction } from "@/features/moderation/components/report-action";

import { useCook } from "../api/social-queries";
import { FollowButton } from "./follow-button";

interface CookProfileProps {
  cookId: string;
  /** Undefined when signed out — no follow or report affordances then. */
  currentUserId: string | undefined;
}

/** The public header of a cook's page: who they are, plus follow and report. */
export function CookProfile({ cookId, currentUserId }: CookProfileProps): React.JSX.Element {
  const { data: cook, isPending, isError } = useCook(cookId);
  const { mutate: blockCook } = useBlockUser();

  if (isPending) {
    return <Skeleton className="h-32 w-full" />;
  }

  if (isError) {
    return (
      <p role="alert" className="text-destructive">
        No pudimos cargar este perfil.
      </p>
    );
  }

  const isSelf = currentUserId === cook.id;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-2xl">{cook.display_name}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {cook.bio ? <p className="text-muted-foreground">{cook.bio}</p> : null}

        {currentUserId && !isSelf ? (
          <div className="flex flex-wrap items-center gap-2">
            <FollowButton cookId={cook.id} />
            <ReportAction
              targetType="user"
              targetId={cook.id}
              authorId={cook.id}
              onBlock={() => {
                blockCook(cook.id);
              }}
            />
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
