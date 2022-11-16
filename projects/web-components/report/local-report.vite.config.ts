import { defineConfig } from "vite";
import {
    esLib,
    PACKAGE_VERSION_BOKEH,
    PLUGIN_REPLACE_BOKEH,
    pluginVue,
    RESOLVE_ALIAS,
} from "./dp-base-config";
import tailwindcss from "tailwindcss";
import minBundle from "../shared/rollup-plugin-min-bundle";

const ENTRY_NAME = "local-report-base.fat.js";

module.exports = defineConfig({
    resolve: RESOLVE_ALIAS,
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
                    // Minify via terser at the final compilation stage,
                    // as minifation isn't supported by rollup on ES modules and converting
                    // to UMD modules makes the build time much slower.
                    // However, we can do it here as local-report-base is a single outputted file
                    minBundle({
                        entryFileName: ENTRY_NAME,
                        emittedFileName: "local-report-base.js",
                    }),
                ],
            },
        },
    },
});
