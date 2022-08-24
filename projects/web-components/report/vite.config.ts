import { defineConfig } from "vite";
import {
    ES_LIB,
    PACKAGE_VERSION_BOKEH,
    PLUGIN_REPLACE_BOKEH,
    PLUGIN_VUE,
} from "./dp-base-config";
import tailwindcss from "tailwindcss";

module.exports = defineConfig(({ mode }) => ({
    css: {
        postcss: {
            plugins: [
                tailwindcss({
                    config: "./report.tailwind.config.js",
                }) as any,
            ],
        },
    },
    plugins: [PLUGIN_VUE(["revo", "x", "dpx"]), PLUGIN_REPLACE_BOKEH],
    define: {
        // Bokeh 2.4 expects a global PACKAGE_VERSION to be defined
        PACKAGE_VERSION: PACKAGE_VERSION_BOKEH,
    },
    build: {
        outDir: "./dist/report/",
        lib: { ...ES_LIB("index.ts"), fileName: "index" },
        rollupOptions: {
            output: {
                paths: {
                    vue:
                        mode === "development"
                            ? "/static/vue.esm-browser.js"
                            : "/static/vue.esm-browser.prod.js",
                    katex:
                        "https://cdn.jsdelivr.net/npm/katex@0.16.0/dist/katex.mjs",
                },
            },
            external: ["vue", "katex"],
        },
    },
}));
