import { Flag } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { ApiError } from "@/lib/api-client";

import { REPORT_REASONS, type ReportReason, type ReportTarget } from "../api/moderation-api";
import { useReport } from "../api/moderation-queries";

interface ReportActionProps {
  targetType: ReportTarget;
  targetId: string;
  /** Offered alongside reporting, since one usually follows the other. */
  authorId?: string | undefined;
  onBlock?: (() => void) | undefined;
}

/** Every user-authored surface needs a reachable report action. */
export function ReportAction({
  targetType,
  targetId,
  authorId,
  onBlock,
}: ReportActionProps): React.JSX.Element {
  const [open, setOpen] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { mutateAsync, isPending } = useReport();

  async function send(reason: ReportReason): Promise<void> {
    setError(null);
    try {
      await mutateAsync({ target_type: targetType, target_id: targetId, reason });
      setDone(true);
      setOpen(false);
    } catch (reportError) {
      setError(
        reportError instanceof ApiError ? reportError.message : "No pudimos enviar el reporte.",
      );
    }
  }

  if (done) {
    return <p className="text-sm text-muted-foreground">Gracias. Lo vamos a revisar.</p>;
  }

  if (!open) {
    return (
      <Button
        variant="ghost"
        size="sm"
        onClick={() => {
          setOpen(true);
        }}
      >
        <Flag className="size-4" />
        Reportar
      </Button>
    );
  }

  return (
    <div className="space-y-2 rounded-lg border border-border p-3">
      <p className="text-sm font-medium">¿Qué pasa con esto?</p>
      <div className="flex flex-wrap gap-2">
        {REPORT_REASONS.map((reason) => (
          <Button
            key={reason.value}
            variant="secondary"
            size="sm"
            disabled={isPending}
            onClick={() => {
              void send(reason.value);
            }}
          >
            {reason.label}
          </Button>
        ))}
      </div>
      {error ? (
        <p role="alert" className="text-sm text-destructive">
          {error}
        </p>
      ) : null}
      <div className="flex gap-2">
        {authorId && onBlock ? (
          <Button variant="ghost" size="sm" onClick={onBlock}>
            Bloquear a esta persona
          </Button>
        ) : null}
        <Button
          variant="ghost"
          size="sm"
          onClick={() => {
            setOpen(false);
          }}
        >
          Cancelar
        </Button>
      </div>
    </div>
  );
}
