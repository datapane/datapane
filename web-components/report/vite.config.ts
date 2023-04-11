import { defineConfig, LibraryFormats } from "vite";
import replace from "@rollup/plugin-replace";
import vueESM from "../shared/rollup-plugin-vue-esm";
import path from "path";
import tailwindcss from "tailwindcss";
import vue from "@vitejs/plugin-vue";
import copy from "rollup-plugin-copy";

module.exports = defineConfig(({ mode }) => ({
    test: {
        include: ["./report/tests/*.test.ts"],
        setupFiles: ["./report/tests/setup.ts"],
        environment: "jsdom",
    },
    resolve: {
        alias: {
            emitter: require.resolve("emitter-component"),
        },
    },
    css: {
        postcss: {
            plugins: [
                tailwindcss({
                    config: "./local-report.tailwind.config.js",
                }) as any,
            ],
        },
    },
    plugins: [
        vue({
            template: {
                compilerOptions: {
                    isCustomElement: (tag) =>
                        ["revo", "x"].some((ce) => tag.startsWith(`${ce}-`)),
                },
            },
        }),
        replace({
            include: ["node_modules/@bokeh/**/*.js"],
            values: {
                // shim jquery to window object for bokehjs
                jQuery: "window.jQuery",
            },
            preventAssignment: false,
        }) as any,
    ],
    define: {
        // Bokeh 2.4 expects a global PACKAGE_VERSION to be defined
        PACKAGE_VERSION: JSON.stringify(process.env.npm_package_version),
        // Pinia expects the node `process` global to be defined but support for this
        // was removed in Vite 3
        "process.env.NODE_ENV": `"${process.env.NODE_ENV}"`,
    },
    build: {
        sourcemap: process.env.NODE_ENV === "development",
        // Enabled in order to split out report `tailwind.css` file
        cssCodeSplit: true,
        outDir: "./dist/report/",
        lib: {
            entry: [path.resolve(__dirname, "index.ts")],
            formats: ["es"] as LibraryFormats[],
            fileName: "[name]",
        },
        rollupOptions: {
            output: {
                assetFileNames: "[name].[ext]",
                entryFileNames: "[name].[format].js",
                chunkFileNames: "[name].[hash].[format].js",
                paths: {
                    vue:
                        mode === "development"
                            ? "../vue.esm-browser.js"
                            : "../vue.esm-browser.prod.js",
                    katex: "https://cdn.jsdelivr.net/npm/katex@0.16.0/dist/katex.mjs",
                },
            },
            external: ["vue", "katex"],
            plugins: [
                vueESM(),
                // Cast as `any` as there seems to be a type conflict between the rollup plugin and Vite's typed config (which uses rollup under the hood)
                copy({
                    targets: [
                        {
                            src: "./node_modules/iframe-resizer/js/iframeResizer.contentWindow.min.js",
                            dest: "./dist/assets",
                        },
                        {
                            src: "./node_modules/iframe-resizer/js/iframeResizer.contentWindow.map",
                            dest: "./dist/assets",
                        },
                    ],
                    verbose: true,
                }) as any,
            ],
        },
    },
}));
