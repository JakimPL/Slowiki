import { readFileSync } from "node:fs";

import react from "@vitejs/plugin-react";
import { parse } from "yaml";
import { defineConfig } from "vitest/config";

interface ServiceConfiguration {
    service: { host: string; port: number };
}

const configuration = parse(
    readFileSync(new URL("../config/config.yaml", import.meta.url), "utf-8"),
) as ServiceConfiguration;
const backend = `http://${configuration.service.host}:${String(configuration.service.port)}`;

export default defineConfig({
    plugins: [react()],
    build: {
        outDir: "../build/frontend",
        emptyOutDir: true,
    },
    server: {
        proxy: {
            "/offerings": backend,
            "/style": backend,
            "/tables": backend,
            "/artwork": backend,
            "/favicon.ico": backend,
        },
    },
    test: {
        environment: "node",
        include: ["tests/**/*.test.ts", "tests/**/*.test.tsx"],
    },
});
