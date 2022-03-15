import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import replace from "@rollup/plugin-replace";
import path from "path";

module.exports = defineConfig({
  plugins: [
    vue({
      template: {
        compilerOptions: {
          isCustomElement: (tag) =>
            tag.startsWith("dp-") || tag.startsWith("revo-"),
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
    outDir: "./dist/local-report/",
    lib: {
      entry: path.resolve(__dirname, "src/entries/local-report.ts"),
      name: "DPLIB",
      fileName: (format) => "local-report-base.js",
      formats: ["es"],
    },
    assetsInlineLimit: 100000000,
    chunkSizeWarningLimit: 100000000,
    cssCodeSplit: false,
    rollupOptions: {
      output: {
        inlineDynamicImports: true,
        format: "esm",
        assetFileNames: (assetInfo) => {
          if (assetInfo.name == "style.css") {
            return "local-report-base.css";
          }
          return assetInfo.name;
        },
      },
    },
  },
});
