import { defineConfig, LibraryFormats } from "vite";
import path from "path";
import vue from "@vitejs/plugin-vue";

module.exports = defineConfig(({ mode }) => ({
    plugins: [
        vue({
            template: {
                compilerOptions: {
                    isCustomElement: (tag) =>
                        ["dp"].some((ce) => tag.startsWith(`${ce}-`)),
                },
            },
        }),
    ],
    define: {
        "process.env.NODE_ENV": `"${process.env.NODE_ENV}"`,
    },
    build: {
        sourcemap: process.env.NODE_ENV === "development",
        // Enabled in order to split out report `tailwind.css` file
        cssCodeSplit: true,
        outDir: "./dist/template-components/",
        lib: {
            entry: [path.resolve(__dirname, "index.ts")],
            formats: ["es"] as LibraryFormats[],
            fileName: "[name]",
        },
        rollupOptions: {
            output: {
                assetFileNames: "[name].[ext]",
                entryFileNames: "[name].[format].js",
                chunkFileNames: "[name].[format].js",
                paths: {
                    vue:
                        mode === "development"
                            ? "../vue.esm-browser.js"
                            : "../vue.esm-browser.prod.js",
                },
            },
            external: ["vue"],
        },
    },
}));
