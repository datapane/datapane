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
    BokehBlock,
    VegaBlock,
    PlotlyBlock,
    TableBlock,
    HTMLBlock,
    SVGBlock,
    FileBlock,
    FormulaBlock,
    MediaBlock,
    EmbedBlock,
    FoliumBlock,
    BigNumberBlock,
} from "./blocks";
import convert from "xml-js";
import * as maps from "./test-maps";
import { DataTableBlock } from "./datatable/datatable-block";

type BlockTest = {
    class_: typeof Block;
    test: (elem: Elem) => boolean;
    opts?: any;
};

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

const isSingleBlockEmbed = (pages: Page[], mode: AppViewMode): boolean => {
    /**
     * Returns `true` if the report consists of a single block, and is in embed (iframe) mode.
     * Single blocks embedded in an iframe require style changes to ensure they fit the iframe dimensions
     */
    const checkAllGroupsSingle = (node: BlockTree): boolean => {
        /* Check there's a single route down to one leaf node */
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
};

const getAttributes = (elem: Elem): any =>
    /**
     * Ensure the attributes object is never undefined
     * -- xml-js removes the attributes property when a tag has none.
     **/
    elem.attributes || {};

const getElementByName = (elem: Elem, name: string): any => {
    if (!elem.elements) return null;
    return elem.elements.find((elem: any) => elem.name === name);
};

export class ReportStore {
    /**
     * deserializes and stores the Report object, and related metadata
     */
    public state: State;

    private readonly webUrl: string;
    private readonly isLightProse: boolean;
    private readonly isOrg: boolean;

    private counts = {
        plots: 0,
        tables: 0,
        formulas: 0,
        codeBlocks: 0,
    };

    public constructor(reportProps: any) {
        this.webUrl = reportProps.report.web_url;
        this.isOrg = reportProps.isOrg;
        this.isLightProse = reportProps.report.is_light_prose;

        const deserializedReport = this.xmlToReport(
            reportProps.report.document
        );

        const singleBlockEmbed = isSingleBlockEmbed(
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
        /**
         * Convert an XML string document to a deserialized tree of `Block` objects
         */
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
        /**
         * Convert a serialised JSON object to a deserialized tree of `Block` objects
         */
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
         * Deserialize a page elem into an array of LayoutBlock
         */
        if (
            elem.elements &&
            (elem.elements.length > 1 || elem.elements[0].name !== "Group")
        ) {
            // Ensure there's a single top-level `Group` as the child of the `Page`
            elem.elements = wrapInGroup(elem.elements);
        }
        return this.deserializeChildren(elem) as LayoutBlock[];
    };

    private deserializeGroup = (elem: Elem): Group => {
        /**
         * Deserialize a group elem into an array of BlockTrees (Block | Select | Group)
         */
        const attributes = getAttributes(elem);
        return new Group({
            children: this.deserializeChildren(elem),
            columns: +attributes.columns,
            label: attributes.label,
        });
    };

    private deserializeToggle = (elem: Elem): Toggle => {
        /**
         * Deserializes a toggle elem into an array of BlockTrees
         */
        const attributes = getAttributes(elem);
        return new Toggle({
            children: this.deserializeChildren(elem),
            label: attributes.label,
        });
    };

    private deserializeSelect = (elem: Elem): Select => {
        /**
         * Deserializes a select elem into (Group | Block)[]
         */
        const attributes = getAttributes(elem);
        return new Select({
            children: this.deserializeChildren(elem),
            type: attributes.type,
            label: attributes.label,
        });
    };

    private deserializeChildren(elem: Elem): BlockTree[] {
        /**
         * Recursively deserialize layout block children
         */
        const children: BlockTree[] = [];
        elem.elements &&
            elem.elements.forEach((e) => {
                if (e.name === "Group") children.push(this.deserializeGroup(e));
                else if (e.name === "Select")
                    children.push(this.deserializeSelect(e));
                else if (e.name === "Toggle")
                    children.push(this.deserializeToggle(e));
                else children.push(this.deserializeBlock(e));
            });
        return children;
    }

    private deserializeBlock(elem: Elem): Block {
        const count = this.updateFigureCount(elem.name);
        const caption = getAttributes(elem).caption;

        const blockTest: BlockTest | undefined = this.blockMap.find((b) =>
            b.test(elem)
        );

        if (blockTest) {
            const { class_, opts } = blockTest;
            return new class_(elem, caption, count, opts);
        } else {
            throw `Couldn't deserialize from JSON ${elem}`;
        }
    }

    private get blockMap(): BlockTest[] {
        /**
         * class_: The deserialized class that maps to a JSON `elem`
         * test: Function that returns true if the JSON should deserialize into the associated `class_`
         * opts: Additional metadata to be passed into the class
         */
        return [
            {
                class_: TextBlock,
                test: maps.jsonIsMarkdown,
                opts: { isLightProse: this.isLightProse },
            },
            { class_: BokehBlock, test: maps.jsonIsBokeh },
            {
                class_: DataTableBlock,
                test: maps.jsonIsArrowTable,
                opts: { webUrl: this.webUrl },
            },
            { class_: CodeBlock, test: maps.jsonIsCode },
            { class_: VegaBlock, test: maps.jsonIsVega },
            { class_: PlotlyBlock, test: maps.jsonIsPlotly },
            { class_: TableBlock, test: maps.jsonIsHTMLTable },
            {
                class_: HTMLBlock,
                test: maps.jsonIsHTML,
                opts: { isOrg: this.isOrg },
            },
            { class_: SVGBlock, test: maps.jsonIsSvg },
            { class_: FormulaBlock, test: maps.jsonIsFormula },
            { class_: MediaBlock, test: maps.jsonIsMedia },
            { class_: EmbedBlock, test: maps.jsonIsEmbed },
            { class_: FoliumBlock, test: maps.jsonIsIFrameHTML },
            { class_: BigNumberBlock, test: maps.jsonIsBigNumber },
            { class_: FileBlock, test: () => true },
        ];
    }
}
