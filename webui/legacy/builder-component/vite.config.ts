import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
    plugins: [
        react({
            babel: {
                parserOpts: {
                    plugins: ["decorators-legacy"],
                },
            },
        }),
    ],
    resolve: {
        alias: {
            "~@blueprintjs": "@blueprintjs",
        },
    },
    build: {
        outDir: "./dist/builder/",
        lib: {
            entry: path.resolve(__dirname, "index.ts"),
            fileName: "index",
            formats: ["es"],
        },
    },
});
