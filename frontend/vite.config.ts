import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
    plugins: [react()],
    build: {
        outDir: "../build/frontend",
        emptyOutDir: true,
    },
    server: {
        proxy: {
            "/offerings": "http://127.0.0.1:8000",
            "/tables": "http://127.0.0.1:8000",
        },
    },
});
