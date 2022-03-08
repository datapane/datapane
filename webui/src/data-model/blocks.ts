import VTextBlock from "../components/blocks/Text.vue";
import VCodeBlock from "../components/blocks/Code.connector.vue";
import VBokehBlock from "../components/blocks/Bokeh.connector.vue";
import { markRaw } from "vue";
import { v4 as uuidv4 } from "uuid";
import axios from "axios";

/* TODO - use class-transformer */

const readGcsTextOrJsonFile = <T = string | object | null>(
  url: string
): Promise<T> => {
  return axios.get(url).then((res) => res.data);
};

export class Report {
  public children: Page[];
  public width: ReportWidth;
  public layout?: PageLayout;

  public constructor(o: {
    children: Page[];
    width: ReportWidth;
    layout?: PageLayout;
  }) {
    this.children = o.children;
    this.width = o.width;
    this.layout = o.layout;
  }
}

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
  public columns: Number;
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

  public constructor(elem: Elem, caption?: string, count?: number) {
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

export abstract class AssetBlock extends Block {
  public src: string;
  public type: string;

  public constructor(elem: Elem, caption?: string, count?: number) {
    super(elem, caption, count);
    const { attributes } = elem;
    this.src = attributes.src;
    this.type = attributes.type;
  }

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
      fetchAssetData: this.fetchRemoteAssetData,
      responsive: this.responsive,
    };
  }
}

export class BokehBlock extends PlotAssetBlock {
  public component = markRaw(VBokehBlock);
}

export class TextBlock extends Block {
  public component = markRaw(VTextBlock);
  public content: string;
  public componentProps: any;

  public constructor(elem: Elem, caption?: string, count?: number) {
    super(elem, caption, count);
    this.content = getInnerText(elem);
    this.componentProps = {
      ...this.componentProps,
      content: this.content,
      isLightProse: false,
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
