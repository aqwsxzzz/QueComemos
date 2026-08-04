import type { ManifestOptions } from "vite-plugin-pwa";

/** Spanish-first install metadata. The product is the PWA — see PRODUCT.md. */
export const pwaManifest: Partial<ManifestOptions> = {
  name: "Que Comemos?",
  short_name: "Que Comemos",
  description: "Recetas caseras compartidas entre personas que cocinan de verdad.",
  lang: "es",
  dir: "ltr",
  start_url: "/",
  scope: "/",
  display: "standalone",
  orientation: "portrait",
  background_color: "#ffffff",
  theme_color: "#c2410c",
  icons: [
    { src: "/icons/icon-192.png", sizes: "192x192", type: "image/png" },
    { src: "/icons/icon-512.png", sizes: "512x512", type: "image/png" },
    {
      src: "/icons/icon-512-maskable.png",
      sizes: "512x512",
      type: "image/png",
      purpose: "maskable",
    },
  ],
};
