/**
 * Resources related to extracting metadata from blocks
 */
import * as maps from "../../legacy-report/test-maps";
import convert from "xml-js";
import { IReportFile, formatNumber } from "../../legacy-report/utils";

export type NamedBlock = {
    name: string;
    tagName: string;
    metadata: string[];
    props: any;
};

type JSONAssetMap = {
    test: (mimetype: string) => boolean;
    type: string;
};

const jsonAssetMaps: JSONAssetMap[] = [
    {
        test: maps.jsonIsVega,
        type: "Vega",
    },
    {
        test: maps.jsonIsPlotly,
        type: "Plotly",
    },
    {
        test: maps.jsonIsIFrameHTML,
        type: "Folium",
    },
    {
        test: maps.jsonIsBase64HTML,
        type: "Folium",
    },
    {
        test: maps.jsonIsPlotapi,
        type: "Plotapi",
    },
    {
        test: maps.jsonIsImage,
        type: "Image",
    },
    { test: maps.jsonIsSvg, type: "SVG" },
    {
        test: maps.jsonIsBokeh,
        type: "Bokeh",
    },
];

const getBlockType = (tagName: string, mimetype: string = ""): string => {
    /**
     * Gets `type` metadata based on the XML tag name and mimetype.
     * If an asset is a `Plot`, its specific plot type is taken as the type.
     * Otherwise the XML `tagName` is used.
     */
    if (tagName !== "Plot") {
        return tagName;
    }
    const map = jsonAssetMaps.find((testObj: any) => testObj.test(mimetype));
    return map ? map.type : "Plot";
};

const getBlockMetadata = (
    tagName: string,
    attributes: any,
    mimetype?: string // TODO - mimetype not currently used, remove?
): string[] => {
    /**
     * Gets misc metadata from the JSON like type, dimensions, etc.
     */

    const metadata: string[] = [getBlockType(tagName, mimetype)];
    if (tagName === "DataTable") {
        const columns = formatNumber(+attributes.columns);
        const rows = formatNumber(+attributes.rows);
        metadata.push(`${columns} × ${rows}`);
    }
    return metadata;
};

export const extractAssets = (reportFiles: IReportFile[]): NamedBlock[] => {
    return reportFiles.map((rf) => {
        const tagJson = convert.xml2js(rf.tag).elements[0];
        return {
            tagName: tagJson.name,
            name: rf.name || rf.id,
            metadata: getBlockMetadata(tagJson.name, tagJson.attributes),
            props: {
                ...tagJson.attributes,
                src: `ref://${rf.id}`,
            },
        };
    });
};
