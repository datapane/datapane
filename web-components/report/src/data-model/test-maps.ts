const jsonType = (json: any): string => {
    if (typeof json === "string") {
        return json;
    }
    return json.attributes && json.attributes.type ? json.attributes.type : "";
};

/* Inline blocks */

export const jsonIsMarkdown = (json: any): boolean => {
    return json.name === "Text";
};

export const jsonIsFormula = (json: any): boolean => {
    return json.name === "Formula";
};

export const jsonIsBigNumber = (json: any): boolean => {
    return json.name === "BigNumber";
};

export const jsonIsMedia = (json: any): boolean => {
    return json.name === "Media";
};

export const jsonIsHTML = (json: any): boolean => {
    return json.name === "HTML";
};

export const jsonIsCode = (json: any): boolean => {
    return json.name === "Code";
};

export const jsonIsEmbed = (json: any): boolean => {
    return json.name === "Embed";
};

/* Asset blocks */

export const jsonIsVega = (json: any): boolean => {
    return jsonType(json).includes("application/vnd.vegalite");
};

export const jsonIsArrowTable = (json: any): boolean => {
    return jsonType(json).includes("application/vnd.apache.arrow+binary");
};

export const jsonIsHTMLTable = (json: any): boolean => {
    return jsonType(json) === "application/vnd.datapane.table+html";
};

export const jsonIsIFrameHTML = (json: any): boolean => {
    return jsonType(json) === "application/vnd.folium+html";
};

export const jsonIsPlotapi = (json: any): boolean => {
    return jsonType(json) === "application/vnd.plotapi+html";
};

export const jsonIsBokeh = (json: any): boolean => {
    return jsonType(json) === "application/vnd.bokeh.show+json";
};

export const jsonIsPlotly = (json: any): boolean => {
    return jsonType(json) === "application/vnd.plotly.v1+json";
};

export const jsonIsSvg = (json: any): boolean => {
    return jsonType(json).includes("image/svg");
};
