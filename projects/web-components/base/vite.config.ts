import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import vueESM from "../shared/rollup-plugin-vue-esm";
import path from "path";
import tailwindcss from "tailwindcss";

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
        postcss: {
            plugins: [
                tailwindcss({
                    config: "./tailwind.config.js",
                }) as any,
            ],
        },
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
                            ? "../vue.esm-browser.js"
                            : "../vue.esm-browser.prod.js",
                },
            },
            external: ["vue"],
            plugins: [vueESM()],
        },
    },
}));
