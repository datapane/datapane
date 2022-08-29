/**
 * TODO
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
