import { useState } from "react";

import { Button } from "@/components/ui/button";

/**
 * External links never navigate directly: the host is shown first and the user
 * confirms. User prose is never linkified — only this structured field exists.
 */
export function SourceLink({ url }: { url: string }): React.JSX.Element {
  const [confirming, setConfirming] = useState(false);
  const host = URL.canParse(url) ? new URL(url).hostname.replace(/^www\./, "") : url;

  if (!confirming) {
    return (
      <Button
        variant="secondary"
        size="sm"
        onClick={() => {
          setConfirming(true);
        }}
      >
        Ver la receta original
      </Button>
    );
  }

  return (
    <div className="space-y-2 rounded-lg border border-border bg-muted/40 p-4">
      <p className="text-sm">
        Vas a salir de Que Comemos? hacia <span className="font-medium">{host}</span>.
      </p>
      <div className="flex gap-2">
        <Button asChild size="sm">
          <a href={url} target="_blank" rel="noreferrer noopener nofollow ugc">
            Continuar
          </a>
        </Button>
        <Button
          variant="secondary"
          size="sm"
          onClick={() => {
            setConfirming(false);
          }}
        >
          Quedarme
        </Button>
      </div>
    </div>
  );
}
