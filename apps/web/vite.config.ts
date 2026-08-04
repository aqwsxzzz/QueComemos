import { fileURLToPath, URL } from "node:url";

import babel from "@rolldown/plugin-babel";
import tailwindcss from "@tailwindcss/vite";
import { tanstackRouter } from "@tanstack/router-plugin/vite";
import react, { reactCompilerPreset } from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import { VitePWA } from "vite-plugin-pwa";

import { pwaManifest } from "./pwa-manifest.ts";

export default defineConfig({
  plugins: [
    tanstackRouter({ target: "react", autoCodeSplitting: true }),
    react(),
    // React Compiler: no manual memoization anywhere in this app.
    babel({ presets: [reactCompilerPreset()] }),
    tailwindcss(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["favicon.svg"],
      manifest: pwaManifest,
      workbox: {
        globPatterns: ["**/*.{js,css,html,svg,png,woff2}"],
        // Recipe photos live in object storage; only the app shell is precached,
        // so the PWA opens offline even on a cold network.
        navigateFallback: "index.html",
      },
    }),
  ],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    // 5173 is Ovejitas and 5174 is DocTrack, so this project takes 5175 and all
    // three can run at once. strictPort makes a clash fail loudly instead of
    // drifting to another port and silently breaking the API's CORS allowlist.
    port: 5175,
    strictPort: true,
    // Bind every interface so the dev server is reachable from outside its
    // container; harmless when running on the host directly.
    host: true,
  },
});
