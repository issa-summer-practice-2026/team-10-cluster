/// <reference types="vitest/config" />
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

// During `npm run dev`, Vite serves the SPA on :5173 and proxies API calls to
// the Flask backend on :8000 (override with API_TARGET). In production the built
// SPA is served by Flask itself, so no proxy is involved.
const API_TARGET = process.env.API_TARGET ?? "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": API_TARGET,
      "/health": API_TARGET,
      "/version": API_TARGET,
    },
  },
  build: {
    outDir: "dist",
  },
  test: {
    environment: "node",
    include: ["src/**/*.test.ts", "src/**/*.test.tsx"],
  },
});
