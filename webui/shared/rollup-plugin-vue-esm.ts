/**
 * Plugin that copies vue ES modules from node_modules/ to dist/
 * for access by template HTML files
 */

import path from "path";
import fs from "fs";

const VUE_DEV_FNAME = "vue.esm-browser.js";
const VUE_PROD_FNAME = "vue.esm-browser.prod.js";

const findPath = async (subpath: string) => {
    /**
     * Travel upwards through tree until subpath is found
     */
    let dir = path.resolve(__dirname);
    while (true) {
        const fullPath = path.resolve(dir, subpath);
        if (fs.existsSync(fullPath)) {
            return fullPath;
        } else {
            dir = path.resolve(dir, "../");
        }
    }
};

export default () => ({
    name: "rollup-plugin-vue-esm",
    buildEnd: async () => {
        const vuePath = await findPath("node_modules/vue/dist");
        const distPath = await findPath("dist");
        await fs.promises.copyFile(
            path.resolve(vuePath, VUE_DEV_FNAME),
            path.resolve(distPath, VUE_DEV_FNAME)
        );
        await fs.promises.copyFile(
            path.resolve(vuePath, VUE_PROD_FNAME),
            path.resolve(distPath, VUE_PROD_FNAME)
        );
    },
});
