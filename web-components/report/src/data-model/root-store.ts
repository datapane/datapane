import axios from "axios";
import { defineStore } from "pinia";
import convert from "xml-js";
import { reactive, ref } from "vue";
import * as b from "./blocks/index";
import * as maps from "./test-maps";
import { AppData, AppDataResult, AppMetaData, SwapType } from "./types";
import he from "he";
import { isParentElem } from "./blocks/index";

export type EmptyObject = Record<string, never>;

const mkBlockMap = (
    isLightProse: boolean,
    webUrl: string,
    isOrg: boolean,
): BlockTest[] => {
    /**
     * class_: The deserialized class that maps to a JSON `elem`
     * test: Function that returns true if the JSON should deserialize into the associated `class_`
     * opts: Additional metadata to be passed into the class
     */
    return [
        {
            class_: b.TextBlock,
            test: maps.jsonIsMarkdown,
            opts: { isLightProse },
        },
        { class_: b.BokehBlock, test: maps.jsonIsBokeh },
        {
            class_: b.DataTableBlock,
            test: maps.jsonIsArrowTable,
            opts: { webUrl },
        },
        { class_: b.CodeBlock, test: maps.jsonIsCode },
        { class_: b.VegaBlock, test: maps.jsonIsVega },
        { class_: b.PlotlyBlock, test: maps.jsonIsPlotly },
        { class_: b.TableBlock, test: maps.jsonIsHTMLTable },
        {
            class_: b.HTMLBlock,
            test: maps.jsonIsHTML,
            opts: { isOrg },
        },
        // NOTE - `MediaBlock` check should go before `SVGBlock` check,
        // as SVGs in a `Media` tag have precedence over plot SVGs
        { class_: b.MediaBlock, test: maps.jsonIsMedia },
        { class_: b.SVGBlock, test: maps.jsonIsSvg },
        { class_: b.FormulaBlock, test: maps.jsonIsFormula },
        { class_: b.EmbedBlock, test: maps.jsonIsEmbed },
        { class_: b.FoliumBlock, test: maps.jsonIsIFrameHTML },
        { class_: b.PlotapiBlock, test: maps.jsonIsPlotapi },
        { class_: b.BigNumberBlock, test: maps.jsonIsBigNumber },
        { class_: b.FunctionBlock, test: maps.jsonIsFunction },
        { class_: b.InputField, test: maps.jsonIsInputField },
        { class_: b.RangeField, test: maps.jsonIsRangeField },
        { class_: b.TagsField, test: maps.jsonIsTagsField },
        { class_: b.SwitchField, test: maps.jsonIsSwitchField },
        { class_: b.MultiChoiceField, test: maps.jsonIsMultiChoiceField },
        { class_: b.FileField, test: maps.jsonIsFileField },
        { class_: b.SelectField, test: maps.jsonIsSelectField },
        {
            class_: b.TemporalField,
            test: maps.jsonIsDateTimeField,
            opts: { timeFormat: "YYYY-MM-DDTHH:mm:ss", type: "datetime-local" },
        },
        {
            class_: b.TemporalField,
            test: maps.jsonIsDateField,
            opts: { timeFormat: "YYYY-MM-DD", type: "date" },
        },
        {
            class_: b.TemporalField,
            test: maps.jsonIsTimeField,
            opts: { timeFormat: "HH:mm:ss", type: "time" },
        },
        { class_: b.Group, test: maps.jsonIsGroup },
        { class_: b.View, test: maps.jsonIsView },
        { class_: b.Select, test: maps.jsonIsSelect },
        { class_: b.Toggle, test: maps.jsonIsToggle },
        { class_: b.EmptyBlock, test: maps.jsonIsEmpty },
        { class_: b.FileBlock, test: () => true },
    ];
};

type BlockTest = {
    class_: typeof b.Block;
    test: (elem: b.Elem) => boolean;
    opts?: any;
};

const getAttributes = (elem: b.Elem): any =>
    /**
     * Ensures the `attributes` object is never undefined
     * -- xml-js removes the attributes property when a tag has none
     **/
    elem.attributes || {};

const getElementByName = (elem: b.Elem, name: string): any => {
    if (!elem.elements) return null;
    return elem.elements.find((elem: any) => elem.name === name);
};

const isSingleBlockEmbed = (
    report: b.View,
    method: "EMBED" | "VIEW",
): boolean => {
    /**
     * Returns `true` if the report consists of a single block, and is in embed (iframe) method.
     * Single blocks embedded in an iframe require style changes to ensure they fit the iframe dimensions
     */
    const checkAllGroupsSingle = (node: b.Block): boolean => {
        /* Check there's a single route down to one leaf node */
        if (b.isLayoutBlock(node) && node.children.length === 1) {
            // Node is a layout block with a single child
            return checkAllGroupsSingle(node.children[0]);
        } else if (b.isLayoutBlock(node)) {
            // Node is a layout block with multiple children
            return false;
        } else {
            // Node is a Select or leaf
            return true;
        }
    };

    return method === "EMBED" && checkAllGroupsSingle(report);
};

export const useRootStore = defineStore("root", () => {
    const counts = reactive({
        Figure: 0,
        Table: 0,
        Plot: 0,
    });

    const blockMap = reactive<BlockTest[]>([]);
    const report = ref<b.View | EmptyObject>({});
    const assetMap = reactive<any>({});
    const singleBlockEmbed = ref<boolean>();

    const deserializeBlock = (elem: b.Elem): b.Block => {
        /**
         * Deserialize leaf block node into relevant `Block` class
         */
        const blockTest: BlockTest | undefined = blockMap.find((b) =>
            b.test(elem),
        );

        if (blockTest) {
            const { class_, opts } = blockTest;
            const { caption } = getAttributes(elem);
            const count = caption
                ? updateFigureCount(class_.captionType)
                : undefined;
            const figure = { caption, count, captionType: class_.captionType };
            return new class_(elem, figure, opts);
        } else {
            throw new Error(`Couldn't deserialize from JSON ${elem}`);
        }
    };

    const fetchReport = async (
        { functionId, params } = { functionId: "app.main", params: undefined },
    ) =>
        await axios.post(
            "/dispatch/",
            {
                jsonrpc: "2.0",
                id: 2,
                method: functionId,
                params,
            },
            { headers: { "Content-Type": "application/json" } },
        );

    const setReport = async (meta: AppMetaData, localAppData?: AppData) => {
        /**
         * Set report object either from given app data or
         * by fetching from the app server
         */
        const appData = localAppData ?? (await fetchReport());

        const { view_xml, assets } = parseAppData(appData, !!localAppData);

        blockMap.push(
            ...mkBlockMap(meta.isLightProse, meta.webUrl, meta.isOrg),
        );

        Object.assign(assetMap, assets);

        // Using `reactive` / Object.assign on `report` only preserved JSON-serialisable properties (i.e. no methods)
        report.value = xmlToView(view_xml);

        // Can cast to `View` as we just assigned the response to `report.value`
        singleBlockEmbed.value = isSingleBlockEmbed(
            report.value as b.View,
            meta.mode,
        );
    };

    const parseAppData = (
        appData: AppData,
        isLocal?: boolean,
    ): AppDataResult => {
        /**
         * Return XML and assets from `appData`, decoding the XML if needed.
         */
        if (!appData.data.result) {
            // Throw JSON-RPC error if available
            const { error } = appData.data;
            throw new Error(
                error ? `${error.message} (${error.code})` : "Unknown error",
            );
        }

        if (isLocal) {
            // Decode HTML entities for locally saved reports
            appData.data.result.view_xml = he.decode(
                appData.data.result.view_xml,
            );
        }

        return appData.data.result;
    };

    const deserialize = (elem: b.Elem, isFragment = false): b.Block => {
        if (!elem.attributes) {
            elem.attributes = {};
        }

        if (b.isFunctionElem(elem)) {
            // Skip inner `Controls` block.
            // Can assert not-null as layout block JSON always contains `elements`
            const controlBlock = elem.elements![0];
            elem.elements = controlBlock.elements;
            elem.attributes.subtitle = controlBlock.attributes?.label;
        } else if (b.isViewElem(elem) && isFragment) {
            elem.name = "Group";
            elem.attributes.columns = "1";
        }

        if (isParentElem(elem)) {
            // Recursively deserialize children if present
            elem.attributes.children = elem.elements
                ? elem.elements.map((e) => deserialize(e))
                : [];
        }

        return deserializeBlock(elem);
    };

    const update = async (
        target: string,
        method: SwapType,
        params: any,
        functionId: string,
    ) => {
        /**
         * Generates new `View` fragment by hitting the app server with params and function ID,
         * and updates the app at the given `target`
         */
        if (!(report.value instanceof b.View)) {
            throw new Error("App not yet initialized");
        }

        const r = await fetchReport({ functionId, params });

        const { view_xml, assets } = parseAppData(r);

        // Update asset store
        Object.assign(assetMap, assets);

        const group: b.Group = xmlToFragment(view_xml);

        const stack: b.LayoutBlock[] = [report.value];
        let didUpdate = false;

        while (stack.length && !didUpdate) {
            // We can assert `LayoutBlock` (not `undefined`) as the stack is only popped while non-empty
            const block = stack.pop() as b.LayoutBlock;

            // If the target block is in `block.children` then update the `children` accordingly and return `true`
            didUpdate = block.update(target, group, method);

            stack.push(...block.children.filter(b.isLayoutBlock));
        }

        if (!didUpdate) {
            throw new Error(`Target block with ID '${target}' not found`);
        }
    };

    const xmlToJson = (xml: string): any => {
        /**
         * TODO
         */
        const json: any = convert.xml2js(xml, { compact: false });
        return getElementByName(json, "View");
    };

    const xmlToView = (xml: string): b.View => {
        /**
         * Convert an XML string document to a deserialized `View` of `Block` objects
         */
        const root = xmlToJson(xml);
        return deserialize(root) as b.View;
    };

    const xmlToFragment = (xml: string): b.Group => {
        /**
         * Convert an XML string document to a deserialized `Group` of `Block` objects
         */
        const root = xmlToJson(xml);
        return deserialize(root, true) as b.Group;
    };

    function updateFigureCount(captionType: b.CaptionType): number {
        return ++counts[captionType];
    }

    return {
        report,
        counts,
        update,
        assetMap,
        singleBlockEmbed,
        setReport,
    };
});
