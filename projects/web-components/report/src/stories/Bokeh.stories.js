import Bokeh from "../components/blocks/Bokeh.vue";
import { makeTemplate } from "./utils";

export default {
    title: "Bokeh",
    component: Bokeh,
};

export const Primary = makeTemplate(Bokeh);

Primary.args = {
    responsive: true,
    plotJson: {
        target_id: null,
        root_id: "1002",
        doc: {
            defs: [],
            roots: {
                references: [
                    {
                        attributes: {
                            line_alpha: 0.2,
                            line_color: "#1f77b4",
                            line_width: 2,
                            x: { field: "x" },
                            y: { field: "y" },
                        },
                        id: "1038",
                        type: "Line",
                    },
                    {
                        attributes: {
                            axis_label: "x",
                            coordinates: null,
                            formatter: { id: "1046" },
                            group: null,
                            major_label_policy: { id: "1047" },
                            ticker: { id: "1014" },
                        },
                        id: "1013",
                        type: "LinearAxis",
                    },
                    {
                        attributes: {
                            coordinates: null,
                            group: null,
                            items: [{ id: "1052" }],
                        },
                        id: "1051",
                        type: "Legend",
                    },
                    {
                        attributes: {
                            axis: { id: "1013" },
                            coordinates: null,
                            group: null,
                            ticker: null,
                        },
                        id: "1016",
                        type: "Grid",
                    },
                    {
                        attributes: {
                            line_color: "#1f77b4",
                            line_width: 2,
                            x: { field: "x" },
                            y: { field: "y" },
                        },
                        id: "1036",
                        type: "Line",
                    },
                    { attributes: {}, id: "1014", type: "BasicTicker" },
                    {
                        attributes: {
                            coordinates: null,
                            group: null,
                            text: "simple line example",
                        },
                        id: "1003",
                        type: "Title",
                    },
                    { attributes: {}, id: "1044", type: "AllLabels" },
                    { attributes: {}, id: "1047", type: "AllLabels" },
                    {
                        attributes: {
                            tools: [
                                { id: "1021" },
                                { id: "1022" },
                                { id: "1023" },
                                { id: "1024" },
                                { id: "1025" },
                                { id: "1026" },
                            ],
                        },
                        id: "1028",
                        type: "Toolbar",
                    },
                    { attributes: {}, id: "1021", type: "PanTool" },
                    { attributes: {}, id: "1007", type: "DataRange1d" },
                    {
                        attributes: {
                            axis_label: "y",
                            coordinates: null,
                            formatter: { id: "1043" },
                            group: null,
                            major_label_policy: { id: "1044" },
                            ticker: { id: "1018" },
                        },
                        id: "1017",
                        type: "LinearAxis",
                    },
                    {
                        attributes: {
                            data: { x: [1, 2, 3, 4, 5], y: [6, 7, 2, 4, 5] },
                            selected: { id: "1049" },
                            selection_policy: { id: "1048" },
                        },
                        id: "1035",
                        type: "ColumnDataSource",
                    },
                    { attributes: {}, id: "1046", type: "BasicTickFormatter" },
                    { attributes: {}, id: "1048", type: "UnionRenderers" },
                    {
                        attributes: {
                            coordinates: null,
                            data_source: { id: "1035" },
                            glyph: { id: "1036" },
                            group: null,
                            hover_glyph: null,
                            muted_glyph: { id: "1038" },
                            nonselection_glyph: { id: "1037" },
                            view: { id: "1040" },
                        },
                        id: "1039",
                        type: "GlyphRenderer",
                    },
                    { attributes: {}, id: "1009", type: "LinearScale" },
                    { attributes: {}, id: "1049", type: "Selection" },
                    { attributes: {}, id: "1024", type: "SaveTool" },
                    { attributes: {}, id: "1022", type: "WheelZoomTool" },
                    {
                        attributes: {
                            below: [{ id: "1013" }],
                            center: [
                                { id: "1016" },
                                { id: "1020" },
                                { id: "1051" },
                            ],
                            left: [{ id: "1017" }],
                            renderers: [{ id: "1039" }],
                            title: { id: "1003" },
                            toolbar: { id: "1028" },
                            x_range: { id: "1005" },
                            x_scale: { id: "1009" },
                            y_range: { id: "1007" },
                            y_scale: { id: "1011" },
                        },
                        id: "1002",
                        subtype: "Figure",
                        type: "Plot",
                    },
                    {
                        attributes: {
                            axis: { id: "1017" },
                            coordinates: null,
                            dimension: 1,
                            group: null,
                            ticker: null,
                        },
                        id: "1020",
                        type: "Grid",
                    },
                    {
                        attributes: {
                            line_alpha: 0.1,
                            line_color: "#1f77b4",
                            line_width: 2,
                            x: { field: "x" },
                            y: { field: "y" },
                        },
                        id: "1037",
                        type: "Line",
                    },
                    { attributes: {}, id: "1011", type: "LinearScale" },
                    {
                        attributes: { source: { id: "1035" } },
                        id: "1040",
                        type: "CDSView",
                    },
                    {
                        attributes: {
                            bottom_units: "screen",
                            coordinates: null,
                            fill_alpha: 0.5,
                            fill_color: "lightgrey",
                            group: null,
                            left_units: "screen",
                            level: "overlay",
                            line_alpha: 1,
                            line_color: "black",
                            line_dash: [4, 4],
                            line_width: 2,
                            right_units: "screen",
                            syncable: false,
                            top_units: "screen",
                        },
                        id: "1027",
                        type: "BoxAnnotation",
                    },
                    {
                        attributes: {
                            label: { value: "Temp." },
                            renderers: [{ id: "1039" }],
                        },
                        id: "1052",
                        type: "LegendItem",
                    },
                    { attributes: {}, id: "1018", type: "BasicTicker" },
                    {
                        attributes: { overlay: { id: "1027" } },
                        id: "1023",
                        type: "BoxZoomTool",
                    },
                    { attributes: {}, id: "1025", type: "ResetTool" },
                    { attributes: {}, id: "1043", type: "BasicTickFormatter" },
                    { attributes: {}, id: "1005", type: "DataRange1d" },
                    { attributes: {}, id: "1026", type: "HelpTool" },
                ],
                root_ids: ["1002"],
            },
            title: "",
            version: "2.4.2",
        },
        version: "2.4.2",
    },
};
