import { reactRouter } from "@react-router/dev/vite";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [
    tailwindcss(),
    reactRouter(),
    {
      name: "automation-server-ownership",
      apply: "serve",
      configureServer(server) {
        const owner = process.env.PW_SERVER_NONCE;
        if (!owner) return;
        server.middlewares.use("/__automation/owner", (_request, response) => {
          response.setHeader("X-Automation-Owner", owner);
          response.setHeader("Cache-Control", "no-store");
          response.statusCode = 204;
          response.end();
        });
      },
    },
  ],
  resolve: {
    dedupe: ["react", "react-dom"],
    tsconfigPaths: true,
  },
});
