import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import replace from "@rollup/plugin-replace";
import path from "path";

module.exports = defineConfig({
  resolve: {
    alias: {
      // TODO - Keep vue bundled in dev mode and add external module to rollup config
      vue: "https://unpkg.com/vue@3.2.29/dist/vue.esm-browser.js",
    },
  },
  plugins: [
    vue({
      template: {
        compilerOptions: {
          isCustomElement: (tag) => tag.includes("-"),
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
    lib: {
      // build is empty if I don't add this build.lib config
      // TODO - Make issue on vite repo
      formats: ["es"],
      entry: "",
    },
    rollupOptions: {
      input: {
        dplib: path.resolve(__dirname, "src/entries/main.ts"),
        code: path.resolve(__dirname, "src/entries/code-block.ts"),
      },
      output: {
        format: "es",
        entryFileNames: "[name].[format].js",
        assetFileNames: "[name].[ext]",
        dir: path.resolve(__dirname, "dist"),
      },
    },
  },
});
