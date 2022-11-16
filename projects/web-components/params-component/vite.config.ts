import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import path from "path";
import { RESOLVE_ALIAS } from "../report/dp-base-config";

module.exports = defineConfig(({ mode }) => ({
    resolve: RESOLVE_ALIAS,
    css: {
        postcss: {},
    },
    plugins: [vue()],
    build: {
        outDir: "./dist/params/",
        lib: {
            entry: path.resolve(__dirname, "index.ts"),
            fileName: "index",
            formats: ["es"],
        },
        rollupOptions: {
            output: {
                entryFileNames: "[name].[format].js",
                chunkFileNames: "[name].[hash].[format].js",
                paths: {
                    vue:
                        mode === "development"
                            ? "/static/vue.esm-browser.js"
                            : "/static/vue.esm-browser.prod.js",
                },
            },
            external: ["vue"],
        },
    },
}));
