/**
 * Plugin that copies vue ES modules from node_modules/ to dist/
 * for access by template HTML files
 */

import path from "path";
import fs from "fs";

const VUE_DEV_FNAME = "vue.esm-browser.js";
const VUE_PROD_FNAME = "vue.esm-browser.prod.js";

export default () => ({
    name: "rollup-plugin-vue-esm",
    buildEnd: async () => {
        const vuePath = path.resolve(__dirname, "../node_modules/vue/dist");
        const distPath = path.resolve(__dirname, "../dist");

        if (!fs.existsSync(distPath)) {
            await fs.promises.mkdir(distPath);
        }

        await Promise.all([
            fs.promises.copyFile(
                path.resolve(vuePath, VUE_DEV_FNAME),
                path.resolve(distPath, VUE_DEV_FNAME)
            ),
            fs.promises.copyFile(
                path.resolve(vuePath, VUE_PROD_FNAME),
                path.resolve(distPath, VUE_PROD_FNAME)
            ),
        ]);
    },
});
