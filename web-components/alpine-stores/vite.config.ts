import { defineConfig } from "vite";
import path from "path";

export default defineConfig({
    css: {
        postcss: {},
    },
    build: {
        outDir: "./dist/alpine-stores/",
        lib: {
            entry: path.resolve(__dirname, "./index.ts"),
            name: "DPLIB",
            fileName: (format) => `index.${format}.js`,
            formats: ["umd"],
        },
    },
});
