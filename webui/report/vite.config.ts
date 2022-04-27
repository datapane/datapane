import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import replace from "@rollup/plugin-replace";
import path from "path";

module.exports = defineConfig(({ mode }) => ({
    css: {
        postcss: {},
    },
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
        replace({
            include: ["node_modules/@bokeh/**/*.js"],
            values: {
                // shim jquery to window object for bokehjs
                jQuery: "window.jQuery",
            },
            preventAssignment: false,
        }),
    ],
    build: {
        outDir: "./dist/report/",
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
