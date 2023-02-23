const jsonType = (json: any): string => {
    if (typeof json === "string") {
        return json;
    }
    return json.attributes && json.attributes.type ? json.attributes.type : "";
};

/* Inline blocks */

export const jsonIsMarkdown = (json: any): boolean => json.name === "Text";

export const jsonIsFormula = (json: any): boolean => json.name === "Formula";

export const jsonIsBigNumber = (json: any): boolean =>
    json.name === "BigNumber";

export const jsonIsMedia = (json: any): boolean => json.name === "Media";

export const jsonIsHTML = (json: any): boolean => json.name === "HTML";

export const jsonIsCode = (json: any): boolean => json.name === "Code";

export const jsonIsEmbed = (json: any): boolean => json.name === "Embed";

export const jsonIsEmpty = (json: any): boolean => json.name === "Empty";

/* Control fields */

export const jsonIsTextBox = (json: any): boolean => json.name === "TextBox";

export const jsonIsRangeField = (json: any): boolean => json.name === "Range";

export const jsonIsSwitchField = (json: any): boolean => json.name === "Switch";

export const jsonIsTagsField = (json: any): boolean => json.name === "Tags";

export const jsonIsSelectField = (json: any): boolean => json.name === "Choice";

export const jsonIsMultiChoiceField = (json: any): boolean =>
    json.name === "MultiChoice";

export const jsonIsFileField = (json: any): boolean => json.name === "File";

export const jsonIsDateTimeField = (json: any): boolean =>
    json.name === "DateTime";

export const jsonIsDateField = (json: any): boolean => json.name === "Date";

export const jsonIsTimeField = (json: any): boolean => json.name === "Time";

/* Layout blocks */

export const jsonIsGroup = (json: any): boolean => json.name === "Group";

export const jsonIsView = (json: any): boolean => json.name === "View";

export const jsonIsSelect = (json: any): boolean => json.name === "Select";

export const jsonIsToggle = (json: any): boolean => json.name === "Toggle";

export const jsonIsCompute = (json: any): boolean => json.name === "Compute";

/* Asset blocks */

export const jsonIsVega = (json: any): boolean =>
    jsonType(json).includes("application/vnd.vegalite");

export const jsonIsArrowTable = (json: any): boolean =>
    jsonType(json).includes("application/vnd.apache.arrow+binary");

export const jsonIsHTMLTable = (json: any): boolean =>
    jsonType(json) === "application/vnd.datapane.table+html";

export const jsonIsIFrameHTML = (json: any): boolean =>
    jsonType(json) === "application/vnd.folium+html";

export const jsonIsPlotapi = (json: any): boolean =>
    jsonType(json) === "application/vnd.plotapi+html";

export const jsonIsBokeh = (json: any): boolean =>
    jsonType(json) === "application/vnd.bokeh.show+json";

export const jsonIsPlotly = (json: any): boolean =>
    jsonType(json) === "application/vnd.plotly.v1+json";

export const jsonIsSvg = (json: any): boolean =>
    jsonType(json).includes("image/svg");
