const jsonType = (json: any): string => {
  if (typeof json === "string") {
    return json;
  }
  return json.attributes && json.attributes.type ? json.attributes.type : "";
};

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

export const jsonIsEmpty = (json: any): boolean => json.name === "Empty";

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

export const jsonIsBase64HTML = (json: any): boolean => {
  return jsonType(json) === "application/vnd.folium+base64";
};

export const jsonIsBokeh = (json: any): boolean => {
  return jsonType(json) === "application/vnd.bokeh.show+json";
};

export const jsonIsImage = (json: any): boolean => {
  return (
    jsonType(json).includes("image") && !jsonType(json).includes("image/svg")
  );
};

export const jsonIsPlotly = (json: any): boolean => {
  return jsonType(json) === "application/vnd.plotly.v1+json";
};

export const jsonIsSvg = (json: any): boolean => {
  return jsonType(json).includes("image/svg");
};
