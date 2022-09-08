import vue from "@vitejs/plugin-vue";
import replace from "@rollup/plugin-replace";
import path from "path";
import { LibraryFormats } from "vite";

export const PLUGIN_REPLACE_BOKEH = replace({
    include: ["node_modules/@bokeh/**/*.js"],
    values: {
        // shim jquery to window object for bokehjs
        jQuery: "window.jQuery",
    },
    preventAssignment: false,
});

export const PLUGIN_VUE = (customEls: string[]) =>
    vue({
        template: {
            compilerOptions: {
                isCustomElement: (tag) =>
                    customEls.some((ce) => tag.startsWith(`${ce}-`)),
            },
        },
    });

// Bokeh 2.4 expects a global PACKAGE_VERSION to be defined
export const PACKAGE_VERSION_BOKEH = JSON.stringify(
    process.env.npm_package_version
);

export const ES_LIB = (entry: string) => ({
    entry: path.resolve(__dirname, entry),
    formats: ["es"] as LibraryFormats[],
});
