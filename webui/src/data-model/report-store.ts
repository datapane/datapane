import {
  Block,
  BlockTree,
  CodeBlock,
  Elem,
  Group,
  LayoutBlock,
  Page,
  Report,
  Select,
  TextBlock,
  Toggle,
  UnknownBlock,
} from "./blocks";
import convert from "xml-js";
import * as maps from "./test-maps";
import he from "he";
import { BokehBlock } from "./bokeh-block";
import { DataTableBlock } from "./datatable-block";

export type State = {
  report?: Report;
};

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
  public state: State = {};

  public constructor(reportProps: any) {
    // const decoded = he.decode(reportProps.report.document);
    // console.log(decoded)
    this.state.report = this.xmlToReport(reportProps.report.document);
  }

  private xmlToReport(xml: string): Report {
    const json: any = convert.xml2js(xml, { compact: false });
    const root = getElementByName(json, "Report");
    return this.deserialize(getElementByName(root, "Pages"));
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
    if (maps.jsonIsMarkdown(elem)) {
      return new TextBlock(elem);
    } else if (maps.jsonIsBokeh(elem)) {
      return new BokehBlock(elem);
    } else if (maps.jsonIsArrowTable(elem)) {
      return new DataTableBlock(elem);
    } else if (maps.jsonIsCode(elem)) {
      return new CodeBlock(elem);
    } else {
      return new UnknownBlock(elem);
    }
  }
}
