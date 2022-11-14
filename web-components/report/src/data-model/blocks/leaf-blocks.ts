import VTextBlock from "../../components/blocks/Text.vue";
import VHTMLBlock from "../../components/blocks/HTML.vue";
import VFileBlock from "../../components/blocks/File.vue";
import VEmbedBlock from "../../components/blocks/Embed.vue";
import VFoliumBlock from "../../components/blocks/Folium.connector.vue";
import VPlotapiBlock from "../../components/blocks/Plotapi.connector.vue";
import VFormulaBlock from "../../components/blocks/Formula.connector.vue";
import VCodeBlock from "../../components/blocks/Code.connector.vue";
import VBokehBlock from "../../components/blocks/Bokeh.connector.vue";
import VVegaBlock from "../../components/blocks/Vega.connector.vue";
import VPlotlyBlock from "../../components/blocks/Plotly.connector.vue";
import VTableBlock from "../../components/blocks/Table.connector.vue";
import VSVGBlock from "../../components/blocks/SVG.connector.vue";
import VMediaBlock from "../../components/blocks/Media.vue";
import VBigNumberBlock from "../../components/blocks/BigNumber.vue";
import VBigNumberBlockSimple from "../../components/blocks/BigNumberSimple.vue";
import { markRaw } from "vue";
import axios from "axios";
import { saveAs } from "file-saver";
import { v4 as uuid4 } from "uuid";
import { useRootStore } from "../root-store";

// Represents a serialised JSON element prior to becoming a Page/Group/Select/Block
export type Elem = {
    name: string;
    attributes?: any;
    elements?: Elem[];
    text?: string;
    cdata?: string;
    type: "element";
};

type AssetResource = Promise<string | object>;

export type BlockFigureProps = {
    caption?: string;
    captionType: string;
    count?: number;
};

export type BlockFigure = Pick<BlockFigureProps, "count" | "caption">;

export type CaptionType = "Table" | "Figure" | "Plot";

/* Helper functions */

const getInnerText = (elem: Elem): string => {
    /**
     * get the CDATA of a JSON-serialised element
     */
    if (!elem.elements || !elem.elements.length)
        throw new Error("Can't get inner text of a node without elements");
    const innerElem = elem.elements[0];
    return innerElem.text || innerElem.cdata || "";
};

const readGcsTextOrJsonFile = <T = string | object | null>(
    url: string,
): Promise<T> => {
    /**
     * wrapper around `axios.get` to fetch data object of response only
     */
    return axios.get(url).then((res) => res.data);
};

/* Inline blocks */

export class Block {
    public refId = uuid4();
    public id?: string;
    public captionType = "Figure";
    public caption?: string;
    public label?: string;
    public count?: number;
    public componentProps: any;
    public component: any;

    public constructor(
        elem: Elem,
        figure: BlockFigure,
        /* eslint-disable-next-line @typescript-eslint/no-unused-vars */
        opts?: any,
    ) {
        const { attributes } = elem;
        this.count = figure.count;
        this.caption = figure.caption;
        const rootStore = useRootStore();
        this.componentProps = {
            figure: { ...figure, captionType: this.captionType },
            singleBlockEmbed: rootStore.singleBlockEmbed,
        };

        if (attributes) {
            // TODO - use `id` not `name`
            // this.id = attributes.id;
            this.id = attributes.name;
            this.label = attributes.label;
        }
    }
}

export class TextBlock extends Block {
    public component = markRaw(VTextBlock);

    public constructor(elem: Elem, figure: BlockFigure, opts?: any) {
        super(elem, figure);
        const content = getInnerText(elem);
        this.componentProps = {
            ...this.componentProps,
            content,
            isLightProse: opts.isLightProse,
        };
    }
}

export class CodeBlock extends Block {
    public component = markRaw(VCodeBlock);

    public constructor(elem: Elem, figure: BlockFigure) {
        super(elem, figure);
        const { language } = elem.attributes;
        const code = getInnerText(elem);
        this.componentProps = { ...this.componentProps, code, language };
    }
}

export class HTMLBlock extends Block {
    public component = markRaw(VHTMLBlock);

    public constructor(elem: Elem, figure: BlockFigure, opts?: any) {
        super(elem, figure);
        const html = getInnerText(elem);
        this.componentProps = {
            ...this.componentProps,
            html,
            sandbox: opts.isOrg ? undefined : "allow-scripts",
        };
    }
}

export class FormulaBlock extends Block {
    public component = markRaw(VFormulaBlock);

    public constructor(elem: Elem, figure: BlockFigure) {
        super(elem, figure);
        const content = getInnerText(elem);
        this.componentProps = {
            ...this.componentProps,
            content,
        };
    }
}

export class EmptyBlock extends Block {}

export class BigNumberBlock extends Block {
    public constructor(elem: Elem, figure: BlockFigure) {
        super(elem, figure);
        const { attributes } = elem;
        const useSimple = !attributes.prev_value && !attributes.change;
        this.component = markRaw(
            useSimple ? VBigNumberBlockSimple : VBigNumberBlock,
        );
        this.componentProps = {
            ...this.componentProps,
            heading: attributes.heading,
            value: attributes.value,
        };
        if (!useSimple) {
            this.componentProps = {
                ...this.componentProps,
                isPositiveIntent: JSON.parse(
                    attributes.is_positive_intent || "false",
                ),
                isUpwardChange: JSON.parse(
                    attributes.is_upward_change || "false",
                ),
                prevValue: attributes.prev_value,
                change: attributes.change,
            };
        }
    }
}

/* Asset blocks */

export abstract class AssetBlock extends Block {
    /**
     * Blocks whose data should be fetched on load rather than in-lined in the XML CDATA
     */
    public src: string;
    public type: string;

    public constructor(elem: Elem, figure: BlockFigure) {
        super(elem, figure);
        const { attributes } = elem;
        const rootStore = useRootStore();

        // Setting asset in constructor (during deserialization) as there's currently
        // no case where an existing block instance needs to have its asset dynamically updated
        const [, assetId] = attributes.src.split("://");

        if (!assetId) {
            throw new Error(
                `Couldn't get block asset ID from src ${attributes.src}`,
            );
        }

        const { src, mime } = rootStore.assetMap[assetId];
        this.src = src;
        this.type = mime;
        this.componentProps = {
            ...this.componentProps,
            fetchAssetData: this.fetchAssetData.bind(this),
        };
    }

    protected async fetchAssetData(): AssetResource {
        return await readGcsTextOrJsonFile(this.src);
    }
}

export class TableBlock extends AssetBlock {
    public component = markRaw(VTableBlock);
    public captionType = "Table";
}

export class FoliumBlock extends AssetBlock {
    public component = markRaw(VFoliumBlock);
    public captionType = "Plot";
}

export class PlotapiBlock extends AssetBlock {
    public component = markRaw(VPlotapiBlock);
    public captionType = "Plot";
}

export class EmbedBlock extends AssetBlock {
    public component = markRaw(VEmbedBlock);

    private _isIFrame?: boolean;
    private html: string;

    public constructor(elem: Elem, figure: BlockFigure) {
        super(elem, figure);
        this.html = getInnerText(elem);
        this.componentProps = {
            ...this.componentProps,
            html: this.html,
            isIframe: this.isIFrame,
        };
    }

    public get isIFrame(): boolean {
        /**
         * Returns `true` if the embed HTML is an iframe element
         */
        if (typeof this._isIFrame === "undefined") {
            const doc: Document = new DOMParser().parseFromString(
                this.html,
                "text/html",
            );
            const root: HTMLBodyElement | null =
                doc.documentElement.querySelector("body");
            this._isIFrame =
                !!root &&
                root.childElementCount === 1 &&
                root.children[0].tagName.toLowerCase() === "iframe";
        }
        return this._isIFrame;
    }
}

export class FileBlock extends AssetBlock {
    public component = markRaw(VFileBlock);

    private readonly filename: string;

    public constructor(elem: Elem, figure: BlockFigure) {
        super(elem, figure);
        const { attributes } = elem;
        this.filename = attributes.filename;
        this.componentProps = {
            ...this.componentProps,
            downloadFile: this.downloadFile.bind(this),
            filename: this.filename,
        };
    }

    protected async downloadFile(): Promise<void> {
        return saveAs(this.src, this.filename);
    }
}

export class MediaBlock extends AssetBlock {
    public component = markRaw(VMediaBlock);

    public constructor(elem: Elem, figure: BlockFigure) {
        super(elem, figure);
        this.componentProps = {
            ...this.componentProps,
            type: this.type,
            src: this.src,
        };
    }
}

export abstract class PlotAssetBlock extends AssetBlock {
    public captionType = "Plot";
    public responsive: boolean;

    public constructor(elem: Elem, figure: BlockFigure) {
        super(elem, figure);
        const { attributes } = elem;
        this.responsive = JSON.parse(attributes.responsive);
        this.componentProps = {
            ...this.componentProps,
            responsive: this.responsive,
        };
    }
}

export class BokehBlock extends PlotAssetBlock {
    public component = markRaw(VBokehBlock);
}

export class VegaBlock extends PlotAssetBlock {
    public component = markRaw(VVegaBlock);
}

export class PlotlyBlock extends PlotAssetBlock {
    public component = markRaw(VPlotlyBlock);

    protected async fetchAssetData(): AssetResource {
        const res = await readGcsTextOrJsonFile<string>(this.src);
        return JSON.parse(res);
    }
}

export class SVGBlock extends PlotAssetBlock {
    public component = markRaw(VSVGBlock);

    protected async fetchAssetData(): AssetResource {
        return this.src;
    }
}
