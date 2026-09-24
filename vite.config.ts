import { defineConfig } from "vitest/config";
import preact from "@preact/preset-vite";

// base "./" lets the built site work from any GitHub Pages sub-path.
export default defineConfig({
  base: "./",
  plugins: [preact()],
  worker: { format: "es" },
  test: { include: ["tests/**/*.test.ts"] },
});
