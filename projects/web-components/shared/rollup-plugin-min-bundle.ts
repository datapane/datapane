/**
 * Minify generated bundle during last step of JS compilation
 * NOTE: This should only be used on single-file outputs (e.g. local-report.base),
 * as minifying at the end stage could cause some issues with codesplitting
 */

import { minify } from "terser";
import { OutputPlugin } from "rollup";

type Options = { entryFileName: string; emittedFileName: string };

export default ({ entryFileName, emittedFileName }: Options) =>
    ({
        name: "rollup-plugin-min-bundle",
        async generateBundle(options, bundle) {
            const { code } = bundle[entryFileName] as any;
            this.emitFile({
                type: "asset",
                fileName: emittedFileName,
                source: (await minify(code)).code,
            });
        },
    } as OutputPlugin);
