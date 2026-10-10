// @leadconnector/vite-tanstack-config already includes the following — do NOT add them manually
// or the app will break with duplicate plugins:
//   - tanstackStart, viteReact, tailwindcss, tsConfigPaths, nitro (build-only using cloudflare as a default target),
//     componentTagger (dev-only, jsxSource fallback + tailwind config), @tanstack/devtools-vite source injection (data-tsd-source, dev-only),
//     HMR gate/flush, dev-server bridge controls, server diagnostics, lightningcss, and sandbox detection
//     (secure host allowlist, port/strictPort, watch ignores, and HMR overlay policy).
// You can pass additional config via defineConfig({ vite: { ... }, etc... }) if needed.
import { defineConfig } from "@leadconnector/vite-tanstack-config";

export default defineConfig({
  // Browser errors stay in the trusted parent-frame console-log flow;
  // do not expose the bridge collector on the public sandbox tunnel.
  devServerBridge: { errorCollector: false },
  vite: {
    // The TanStack Start plugin resolves the `#tanstack-router-entry` and
    // `#tanstack-start-entry` virtual imports (used by the legacy
    // createStartHandler path inside @tanstack/start-server-core) at request
    // time. Pre-bundling those server-core packages during dev dependency
    // optimization makes rolldown try to resolve the virtual specifiers as
    // bare package subpaths and crash. Exclude them so the plugin owns their
    // resolution.
    optimizeDeps: {
      exclude: [
        "@tanstack/start-server-core",
        "@tanstack/react-start-server",
        "@tanstack/start-plugin-core",
      ],
    },
  },
  // Do not set server.hmr.timeout — Vite 8 deprecated those websocket fields
  // (use server.ws.*). Overlay/host/port are package-owned; default WS timeout is 30s.
  tanstackStart: {
    // Redirect TanStack Start's bundled server entry to src/server.ts (our SSR error wrapper).
    // nitro/vite builds from this.
    server: {
      allowedHosts: true,
      entry: "server",
    },
  },
});
