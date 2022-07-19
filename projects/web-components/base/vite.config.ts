import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import vueESM from "../shared/rollup-plugin-vue-esm";
import path from "path";

module.exports = defineConfig(({ mode }) => ({
    plugins: [
        vue({
            template: {
                compilerOptions: {
                    isCustomElement: (tag) =>
                        tag.startsWith("dpx-") ||
                        tag.startsWith("x-") ||
                        tag.startsWith("revo-"),
                },
            },
        }),
    ],
    css: {
        postcss: path.resolve(__dirname, "postcss.config.js"),
    },
    build: {
        outDir: "./dist/base/",
        lib: {
            formats: ["es"],
            entry: "",
        },
        rollupOptions: {
            input: {
                index: path.resolve(__dirname, "index.ts"),
                "code-block": path.resolve(__dirname, "code-block.index.ts"),
            },
            output: {
                format: "es",
                entryFileNames: "[name].[format].js",
                assetFileNames: "[name].[ext]",
                paths: {
                    vue:
                        mode === "development"
                            ? "/static/vue.esm-browser.js"
                            : "/static/vue.esm-browser.prod.js",
                },
            },
            external: ["vue"],
            plugins: [vueESM()],
        },
    },
}));
