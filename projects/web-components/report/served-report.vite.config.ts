import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import replace from "@rollup/plugin-replace";
import path from "path";

module.exports = defineConfig(() => ({
    plugins: [
        vue({
            template: {
                compilerOptions: {
                    isCustomElement: (tag) =>
                        tag.startsWith("revo-") || tag.startsWith("x-"),
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
    define: {
        // Bokeh 2.4 expects a global PACKAGE_VERSION to be defined
        PACKAGE_VERSION: JSON.stringify(process.env.npm_package_version),
    },
    build: {
        outDir: "./dist/served-report/",
        lib: {
            entry: path.resolve(__dirname, "served-report.index.ts"),
            fileName: "index",
            formats: ["es"],
        },
        rollupOptions: {
            output: {
                paths: {
                    vue: "/dist/vue.esm-browser.prod.js",
                },
            },
            external: ["vue"],
        },
    },
}));
