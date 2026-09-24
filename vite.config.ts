import { defineConfig } from "vitest/config";
import preact from "@preact/preset-vite";

// base "./" lets the built site work from any GitHub Pages sub-path.
export default defineConfig({
  base: "./",
  plugins: [preact()],
  worker: { format: "es" },
  // CodeMirror + 30 lessons make one ~600 kB bundle (200 kB gzipped). That's fine for this app.
  build: { chunkSizeWarningLimit: 800 },
  test: { include: ["tests/**/*.test.ts"] },
});
