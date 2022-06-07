import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import path from "path";

module.exports = defineConfig(({ mode }) => ({
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
