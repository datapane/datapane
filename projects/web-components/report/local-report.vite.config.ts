import { defineConfig } from "vite";
import {
    ES_LIB,
    PACKAGE_VERSION_BOKEH,
    PLUGIN_REPLACE_BOKEH,
    PLUGIN_VUE,
} from "./dp-base-config";
import tailwindcss from "tailwindcss";
import minBundle from "../shared/rollup-plugin-min-bundle";

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
    plugins: [PLUGIN_VUE(["revo", "x"]), PLUGIN_REPLACE_BOKEH],
    define: {
        PACKAGE_VERSION: PACKAGE_VERSION_BOKEH,
    },
    build: {
        minify: "esbuild",
        outDir: "./dist/local-report/",
        lib: ES_LIB("local-report.index.ts"),
        assetsInlineLimit: 100000000,
        chunkSizeWarningLimit: 100000000,
        cssCodeSplit: false,
        rollupOptions: {
            output: {
                inlineDynamicImports: true,
                entryFileNames: "local-report-base.fat.js",
                assetFileNames: (assetInfo) => {
                    if (assetInfo.name == "style.css") {
                        return "local-report-base.css";
                    }
                    return `${assetInfo.name}`;
                },
                plugins: [minBundle()],
            },
        },
    },
});
