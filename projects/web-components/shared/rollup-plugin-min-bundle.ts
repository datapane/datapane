/**
 * TODO
 */

import { minify } from "terser";

export default () => ({
    name: "rollup-plugin-postprocess-terser",
    async generateBundle(options, bundle) {
        const { code } = bundle["local-report-base.fat.js"] as any;
        this.emitFile({
            type: "asset",
            fileName: "local-report-base.js",
            source: (await minify(code)).code,
        });
    },
});
