import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import replace from "@rollup/plugin-replace";
import path from "path";

module.exports = defineConfig({
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
        }),
    ],
    build: {
        outDir: "./dist/report/",
        lib: {
            // build is empty if I don't add this build.lib config
            // TODO - Make issue on vite repo
            entry: path.resolve(__dirname, "index.ts"),
            fileName: "index",
            formats: ["es"],
        },
        rollupOptions: {
            output: {
                paths: {
                    vue: "https://unpkg.com/vue@3.2.29/dist/vue.esm-browser.js",
                },
            },
            external: ["vue"],
        },
    },
});
