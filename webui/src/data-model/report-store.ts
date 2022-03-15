import {
  Block,
  BlockTree,
  CodeBlock,
  Elem,
  Group,
  isGroup,
  LayoutBlock,
  Page,
  Report,
  Select,
  TextBlock,
  Toggle,
  UnknownBlock,
  BokehBlock,
  VegaBlock,
  PlotlyBlock,
  TableBlock,
} from "./blocks";
import convert from "xml-js";
import * as maps from "./test-maps";
import { DataTableBlock } from "./datatable/datatable-block";

export type State = {
  report: Report;
  singleBlockEmbed: boolean;
};

export type AppViewMode = "VIEW" | "EDIT" | "EMBED";

const wrapInGroup = (elems: Elem[]): Elem[] => [
  {
    /**
     * Used by Page elements to wrap ungrouped Page children in a serialized group element,
     * so that the report renders a report as a single grid
     */
    name: "Group",
    type: "element",
    attributes: { columns: "1" },
    elements: elems,
  },
];

const getAttributes = (elem: Elem): any =>
  /* Ensure the attributes object is never undefined
   * -- xml-js removes the attributes property when a tag has none. */
  elem.attributes || {};

const getElementByName = (elem: Elem, name: string): any => {
  if (!elem.elements) return null;
  return elem.elements.find((elem: any) => elem.name === name);
};

export class ReportStore {
  public state: State;

  private webUrl: string;
  private isLightProse: boolean;

  private counts = {
    plots: 0,
    tables: 0,
    formulas: 0,
    codeBlocks: 0,
  };

  public constructor(reportProps: any) {
    this.webUrl = reportProps.report.web_url;
    this.isLightProse = reportProps.report.is_light_prose;

    const deserializedReport = this.xmlToReport(reportProps.report.document);
    const singleBlockEmbed = this.isSingleBlockEmbed(
      deserializedReport.children,
      reportProps.mode
    );

    this.state = {
      report: deserializedReport,
      singleBlockEmbed,
    };

    if (singleBlockEmbed) {
      // Prevent scrolling on single block plot embeds
      document.body.style.overflow = "hidden";
    }
  }

  private xmlToReport(xml: string): Report {
    const json: any = convert.xml2js(xml, { compact: false });
    const root = getElementByName(json, "Report");
    return this.deserialize(getElementByName(root, "Pages"));
  }

  private updateFigureCount(elemName: string): number {
    /**
     * Updates and returns the relevant count
     */
    let count = 0;
    if (elemName === "Plot") {
      count = ++this.counts.plots;
    } else if (["Table", "DataTable"].includes(elemName)) {
      count = ++this.counts.tables;
    } else if (elemName === "Formula") {
      count = ++this.counts.formulas;
    } else if (elemName === "Code") {
      count = ++this.counts.codeBlocks;
    }
    return count;
  }

  private deserialize(elem: Elem): Report {
    const attributes = getAttributes(elem);
    const pages: Page[] = [];
    elem.elements &&
      elem.elements.forEach((e) => {
        pages.push(
          new Page({
            label: getAttributes(e).label,
            children: this.deserializePage(e),
          })
        );
      });

    return new Report({
      width: attributes.width,
      layout: attributes.layout,
      children: pages,
    });
  }

  private isSingleBlockEmbed(pages: Page[], mode: AppViewMode): boolean {
    const checkAllGroupsSingle = (node: BlockTree): boolean => {
      /**
       * Check there's a single route down to one leaf node
       */
      if (isGroup(node) && node.children.length === 1) {
        // Node is a Group with a single child
        return checkAllGroupsSingle(node.children[0]);
      } else if (isGroup(node)) {
        // Node is a Group with multiple children
        return false;
      } else {
        // Node is a Select or leaf
        return true;
      }
    };

    return (
      mode === "EMBED" &&
      pages.length === 1 && // Only one page
      pages[0].children.length === 1 && // Only one Group in that page
      checkAllGroupsSingle(pages[0].children[0])
    ); // No groups with multiple children in that group
  }

  private deserializePage = (elem: Elem): LayoutBlock[] => {
    /**
     * Deserializes a page elem into an array of LayoutBlock
     */
    if (
      elem.elements &&
      (elem.elements.length > 1 || elem.elements[0].name !== "Group")
    ) {
      elem.elements = wrapInGroup(elem.elements);
    }
    return this.deserializeChildren(elem) as LayoutBlock[];
  };

  private deserializeGroup = (elem: Elem): Group => {
    /**
     * Deserializes a group elem into an array of BlockTrees (Block | Select | Group)
     */
    const attributes = getAttributes(elem);
    const children: BlockTree[] = this.deserializeChildren(elem);
    return new Group({
      children,
      columns: +attributes.columns,
      label: attributes.label,
    });
  };

  private deserializeToggle = (elem: Elem): Toggle => {
    /**
     * Deserializes a toggle elem into an array of BlockTrees
     */
    const attributes = getAttributes(elem);
    const children: BlockTree[] = this.deserializeChildren(elem);
    return new Toggle({
      children,
      label: attributes.label,
    });
  };

  private deserializeSelect = (elem: Elem): Select => {
    /**
     * Deserializes a select elem into (Group | Block)[]
     */
    const attributes = getAttributes(elem);
    const children: BlockTree[] = this.deserializeChildren(elem);
    return new Select({
      children,
      type: attributes.type,
      label: attributes.label,
    });
  };

  private deserializeChildren(elem: Elem): BlockTree[] {
    /**
     * Recursively deserialize layout blocks
     */
    const children: BlockTree[] = [];
    elem.elements &&
      elem.elements.forEach((e) => {
        if (e.name === "Group") children.push(this.deserializeGroup(e));
        else if (e.name === "Select") children.push(this.deserializeSelect(e));
        else if (e.name === "Toggle") children.push(this.deserializeToggle(e));
        else children.push(this.deserializeBlock(e));
      });
    return children;
  }

  private deserializeBlock(elem: Elem): Block {
    const count = this.updateFigureCount(elem.name);
    const caption = getAttributes(elem).caption;

    let BlockClass: typeof Block;
    let opts: any;
    if (maps.jsonIsMarkdown(elem)) {
      BlockClass = TextBlock;
      opts = { isLightProse: this.isLightProse };
    } else if (maps.jsonIsBokeh(elem)) {
      BlockClass = BokehBlock;
    } else if (maps.jsonIsArrowTable(elem)) {
      BlockClass = DataTableBlock;
      opts = { webUrl: this.webUrl };
    } else if (maps.jsonIsCode(elem)) {
      BlockClass = CodeBlock;
    } else if (maps.jsonIsVega(elem)) {
      BlockClass = VegaBlock;
    } else if (maps.jsonIsPlotly(elem)) {
      BlockClass = PlotlyBlock;
    } else if (maps.jsonIsHTMLTable(elem)) {
      BlockClass = TableBlock;
    } else {
      BlockClass = UnknownBlock;
    }
    return new BlockClass(elem, caption, count, opts);
  }
}
