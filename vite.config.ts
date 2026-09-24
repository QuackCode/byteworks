import { defineConfig } from "vitest/config";
import preact from "@preact/preset-vite";

// A new id for every build: written into the game and into version.json (see src/engine/update.ts)
const BUILD_ID = Date.now().toString(36);

// base "./" lets the built site work from any GitHub Pages sub-path.
export default defineConfig({
  base: "./",
  plugins: [
    preact(),
    {
      name: "byteworks-version-file",
      generateBundle() {
        this.emitFile({ type: "asset", fileName: "version.json", source: JSON.stringify({ id: BUILD_ID }) });
      },
    },
  ],
  define: { __BUILD_ID__: JSON.stringify(BUILD_ID) },
  worker: { format: "es" },
  // Cross-origin isolation (SharedArrayBuffer) for live pacing and the Stop button.
  // GitHub Pages can't set headers, so public/coi-serviceworker.min.js adds them there.
  server: { headers: { "Cross-Origin-Opener-Policy": "same-origin", "Cross-Origin-Embedder-Policy": "require-corp" } },
  preview: { headers: { "Cross-Origin-Opener-Policy": "same-origin", "Cross-Origin-Embedder-Policy": "require-corp" } },
  // CodeMirror + 30 lessons make one ~600 kB bundle (200 kB gzipped). That's fine for this app.
  build: { chunkSizeWarningLimit: 800 },
  test: { include: ["tests/**/*.test.ts"] },
});
