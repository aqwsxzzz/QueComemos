import { Link } from "@tanstack/react-router";
import { Bookmark, CookingPot, PlusCircle, User } from "lucide-react";
import type { ComponentType } from "react";

import { useAuthStore } from "@/features/auth/store/auth-store";

interface NavItem {
  to: string;
  label: string;
  icon: ComponentType<{ className?: string }>;
}

const PUBLIC_ITEMS: NavItem[] = [
  { to: "/recetas", label: "Recetas", icon: CookingPot },
  { to: "/entrar", label: "Entrar", icon: User },
];

const SIGNED_IN_ITEMS: NavItem[] = [
  { to: "/recetas", label: "Recetas", icon: CookingPot },
  { to: "/recetas/nueva", label: "Subir", icon: PlusCircle },
  { to: "/guardadas", label: "Guardadas", icon: Bookmark },
  { to: "/perfil", label: "Perfil", icon: User },
];

/**
 * Bottom bar on phones, top bar from `sm` up. Mobile is the primary surface, so
 * the controls sit in thumb reach rather than in a header nobody can stretch to.
 */
export function AppNav(): React.JSX.Element {
  const isSignedIn = Boolean(useAuthStore((state) => state.tokens));
  const items = isSignedIn ? SIGNED_IN_ITEMS : PUBLIC_ITEMS;

  return (
    <nav
      aria-label="Principal"
      className="fixed inset-x-0 bottom-0 z-50 border-t border-border bg-background/95 backdrop-blur sm:bottom-auto sm:top-0 sm:border-b sm:border-t-0"
    >
      <div className="mx-auto flex max-w-3xl items-stretch justify-around gap-1 px-2 pb-[env(safe-area-inset-bottom)] sm:justify-start sm:px-4 sm:pb-0">
        <Link
          to="/"
          className="hidden items-center pr-4 text-base font-semibold tracking-tight sm:flex"
        >
          Que Comemos?
        </Link>
        {items.map((item) => (
          <NavLink key={item.to} item={item} />
        ))}
      </div>
    </nav>
  );
}

function NavLink({ item }: { item: NavItem }): React.JSX.Element {
  const Icon = item.icon;
  return (
    <Link
      to={item.to}
      // min-h-11 is a 44px touch target — the whole point of thumb reach.
      className="flex min-h-11 flex-1 flex-col items-center justify-center gap-0.5 rounded-md px-2 py-2 text-xs text-muted-foreground transition-colors hover:text-foreground sm:min-h-0 sm:max-w-fit sm:flex-none sm:flex-row sm:gap-2 sm:py-3 sm:text-sm"
      activeProps={{ className: "text-primary font-medium" }}
    >
      <Icon className="size-5 sm:size-4" />
      {item.label}
    </Link>
  );
}
