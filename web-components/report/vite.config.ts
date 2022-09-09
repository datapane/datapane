import { defineConfig } from "vite";
import {
    esLib,
    PACKAGE_VERSION_BOKEH,
    PLUGIN_REPLACE_BOKEH,
    pluginVue,
} from "./dp-base-config";
import tailwindcss from "tailwindcss";
import vueESM from "../shared/rollup-plugin-vue-esm";

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
    plugins: [pluginVue(["revo", "x"]), PLUGIN_REPLACE_BOKEH],
    define: {
        // Bokeh 2.4 expects a global PACKAGE_VERSION to be defined
        PACKAGE_VERSION: PACKAGE_VERSION_BOKEH,
    },
    build: {
        outDir: "./dist/report/",
        lib: { ...esLib("index.ts"), fileName: "index" },
        rollupOptions: {
            output: {
                paths: {
                    vue:
                        mode === "development"
                            ? "../vue.esm-browser.js"
                            : "../vue.esm-browser.prod.js",
                    katex:
                        "https://cdn.jsdelivr.net/npm/katex@0.16.0/dist/katex.mjs",
                },
            },
            external: ["vue", "katex"],
            plugins: [vueESM()],
        },
    },
}));
