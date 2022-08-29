import { defineConfig } from "vite";
import {
    esLib,
    PACKAGE_VERSION_BOKEH,
    PLUGIN_REPLACE_BOKEH,
    pluginVue,
} from "./dp-base-config";
import tailwindcss from "tailwindcss";
import minBundle from "../shared/rollup-plugin-min-bundle";

const ENTRY_NAME = "local-report-base.fat.js";

module.exports = defineConfig({
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
        PACKAGE_VERSION: PACKAGE_VERSION_BOKEH,
    },
    build: {
        minify: "esbuild",
        outDir: "./dist/local-report/",
        lib: esLib("local-report.index.ts"),
        assetsInlineLimit: 100000000,
        chunkSizeWarningLimit: 100000000,
        cssCodeSplit: false,
        rollupOptions: {
            output: {
                inlineDynamicImports: true,
                entryFileNames: ENTRY_NAME,
                assetFileNames: (assetInfo) => {
                    if (assetInfo.name == "style.css") {
                        return "local-report-base.css";
                    }
                    return `${assetInfo.name}`;
                },
                plugins: [
                    // TODO - explain
                    minBundle({
                        entryFileName: ENTRY_NAME,
                        emittedFileName: "local-report-base.js",
                    }),
                ],
            },
        },
    },
});
