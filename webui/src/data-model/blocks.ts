import VTextBlock from "../components/blocks/Text.vue";
import VCodeBlock from "../components/blocks/Code.connector.vue";
import VBokehBlock from "../components/blocks/Bokeh.connector.vue";
import VVegaBlock from "../components/blocks/Vega.connector.vue";
import VPlotlyBlock from "../components/blocks/Plotly.connector.vue";
import { markRaw } from "vue";
import { v4 as uuidv4 } from "uuid";
import axios from "axios";

export class Report {
  public children: Page[];
  public width: ReportWidth;

  private _layout?: PageLayout;

  public get layout(): PageLayout {
    return this._layout || (this.children.length > 5 ? "side" : "top");
  }

  public constructor(o: {
    children: Page[];
    width: ReportWidth;
    layout?: PageLayout;
  }) {
    this.children = o.children;
    this.width = o.width;
    this._layout = o.layout;
  }
}

/* Layout blocks */

export class Page {
  public children: LayoutBlock[];
  public label?: string;

  public constructor(o: { children: LayoutBlock[]; label?: string }) {
    this.children = o.children;
    this.label = o.label;
  }
}

export class Group {
  public children: BlockTree[];
  public columns: number;
  public label?: string;
  public name = "Group";

  public constructor(o: {
    children: BlockTree[];
    columns: number;
    label?: string;
  }) {
    this.children = o.children;
    this.columns = o.columns;
    this.label = o.label;
  }
}

export class Toggle {
  public children: BlockTree[];
  public label?: string;
  public name = "Toggle";

  public constructor(o: { children: BlockTree[]; label?: string }) {
    this.children = o.children;
    this.label = o.label;
  }
}

export class Select {
  public children: BlockTree[];
  public label?: string;
  public type: string;
  public name = "Select";

  public constructor(o: {
    children: BlockTree[];
    type: string;
    label?: string;
  }) {
    this.children = o.children;
    this.label = o.label;
    this.type = o.type;
  }
}

/* Atomic blocks */

export class Block {
  public refId: string;
  public captionType = "Figure";
  public caption?: string;
  public label?: string;
  public count?: number;
  public componentProps: any;

  public constructor(elem: Elem, caption?: string, count?: number, opts?: any) {
    const { attributes } = elem;
    this.refId = uuidv4();
    this.count = count;
    this.caption = caption;
    this.componentProps = { caption: this.caption, count: this.count };

    if (attributes) {
      this.label = attributes.label;
    }
  }
}

// TODO - generic type T needed?
export abstract class AssetBlock<T = any> extends Block {
  public src: string;
  public type: string;

  public constructor(elem: Elem, caption?: string, count?: number) {
    super(elem, caption, count);
    const { attributes } = elem;
    this.src = attributes.src;
    this.type = attributes.type;
  }

  protected fetchLocalAssetData(): any {
    return decodeBase64Asset(this.src);
  }

  public fetchAssetData = async (): Promise<T> => {
    return window.dpLocal
      ? this.fetchLocalAssetData()
      : this.fetchRemoteAssetData();
  };

  protected fetchRemoteAssetData = async (): Promise<
    string | object | null
  > => {
    return await readGcsTextOrJsonFile(this.src);
  };
}

export abstract class PlotAssetBlock extends AssetBlock {
  public captionType = "Plot";
  public responsive: boolean;

  public constructor(elem: Elem, caption?: string, count?: number) {
    super(elem, caption, count);
    const { attributes } = elem;
    this.responsive = JSON.parse(attributes.responsive);
    this.componentProps = {
      ...this.componentProps,
      fetchAssetData: this.fetchAssetData,
      responsive: this.responsive,
    };
  }
}

export class BokehBlock extends PlotAssetBlock {
  public component = markRaw(VBokehBlock);

  protected fetchLocalAssetData(): any {
    const localAssetData = super.fetchLocalAssetData();
    return JSON.parse(localAssetData);
  }
}

export class VegaBlock extends PlotAssetBlock {
  public component = markRaw(VVegaBlock);

  protected fetchLocalAssetData(): any {
    const localAssetData = super.fetchLocalAssetData();
    return JSON.parse(localAssetData);
  }
}

export class PlotlyBlock extends PlotAssetBlock {
  public component = markRaw(VPlotlyBlock);

  protected fetchLocalAssetData(): any {
    return JSON.parse(JSON.parse(decodeBase64Asset(this.src)));
  }

  protected fetchRemoteAssetData = async (): Promise<any> => {
    /* TODO - type promise? */
    const res = await readGcsTextOrJsonFile<string>(this.src);
    return JSON.parse(res);
  };
}

export class TextBlock extends Block {
  public component = markRaw(VTextBlock);
  public content: string;
  public componentProps: any;

  public constructor(elem: Elem, caption?: string, count?: number, opts?: any) {
    super(elem, caption, count);
    this.content = getInnerText(elem);
    this.componentProps = {
      ...this.componentProps,
      content: this.content,
      isLightProse: opts.isLightProse,
    };
  }
}

export class CodeBlock extends AssetBlock {
  public component = markRaw(VCodeBlock);
  public componentProps: any;

  public constructor(elem: Elem, caption?: string, count?: number) {
    super(elem, caption, count);
    const { language } = elem.attributes;
    const code = getInnerText(elem);
    this.componentProps = { ...this.componentProps, code, language };
  }
}

export class UnknownBlock extends Block {
  public content: string;

  public constructor(elem: Elem) {
    super(elem);
    this.content = `Unknown block ${elem.name}`;
  }
}

/* Helper types */

type BlockProps = { captionType?: string; label?: string; count?: number };

export type LayoutBlock = Group | Select | Toggle;

export type ReportWidth = "full" | "medium" | "narrow";

export type PageLayout = "top" | "side";

export type ExportType = "EXCEL" | "CSV";

export const isBlock = (obj: any): obj is Block => !!obj.refId;

export const isGroup = (obj: any): obj is Group => obj.name === "Group";

export const isSelect = (obj: any): obj is Select => obj.name === "Select";

export const isToggle = (obj: any): obj is Toggle => obj.name === "Toggle";

export const isAssetBlock = (obj: any): obj is AssetBlock => !!obj.src;

// Represents a serialised JSON element prior to becoming a Page/Group/Select/Block
export type Elem = {
  name: string;
  attributes?: any;
  elements?: Elem[];
  text?: string;
  cdata?: string;
  type: "element";
};

export type BlockTree = LayoutBlock | Block;

/* Helper functions */

const getInnerText = (elem: Elem): string => {
  if (!elem.elements || !elem.elements.length)
    throw new Error("Can't get inner text of a node without elements");
  const innerElem = elem.elements[0];
  return innerElem.text || innerElem.cdata || "";
};

const readGcsTextOrJsonFile = <T = string | object | null>(
  url: string
): Promise<T> => {
  return axios.get(url).then((res) => res.data);
};

export const decodeBase64Asset = (src: string): any => {
  return window.atob(src.split("base64,")[1]);
};
