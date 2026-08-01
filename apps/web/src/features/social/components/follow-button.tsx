import { Button } from "@/components/ui/button";

import { useFollowStatus, useToggleFollow } from "../api/social-queries";

export function FollowButton({ cookId }: { cookId: string }): React.JSX.Element | null {
  const { data: status, isPending } = useFollowStatus(cookId);
  const { mutate: toggle, isPending: saving } = useToggleFollow(cookId);

  if (isPending || !status) {
    return null;
  }

  return (
    <Button
      variant={status.is_followed ? "secondary" : "default"}
      size="sm"
      disabled={saving}
      onClick={() => {
        toggle(status.is_followed);
      }}
    >
      {status.is_followed ? "Siguiendo" : "Seguir"}
    </Button>
  );
}
