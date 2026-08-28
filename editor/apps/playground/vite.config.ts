import react from "@vitejs/plugin-react";
import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";

export default defineConfig({
  cacheDir: "../../.vite/playground",
  plugins: [react()],
  resolve: {
    alias: {
      "@ova/portable-text-editor-core": fileURLToPath(
        new URL("../../packages/editor-core/src/index.ts", import.meta.url)
      ),
      "@ova/portable-text-editor-react": fileURLToPath(
        new URL("../../packages/editor-react/src/index.ts", import.meta.url)
      )
    }
  },
  server: {
    port: 5173
  }
});
