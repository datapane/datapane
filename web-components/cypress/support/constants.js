/* eslint-disable */

// URLs

export const URLS = {
    PARAMS_APP: `${Cypress.env("paramsAppURL")}`,
    NO_PARAMS_APP: `${Cypress.env("noParamsAppURL")}`,
    SCHEDULE: `${Cypress.env("paramsAppURL")}schedules/create/`,
    FILE: `${Cypress.env("fileURL")}`,
    STYLE_REPORT: `${Cypress.env("styleReportURL")}`,
    BUILDER_REPORT: `${Cypress.env("builderReportURL")}`,
};

export const HTML_HEADER = `<style type="text/css">
:root {
  --dp-accent-color: green;
  --dp-bg-color: black;
  --dp-text-align: right;
  --dp-font-family: monospace;
}
</style>`;

export const HTML_HEADER_LIGHT = `<style type="text/css">
:root {
  --dp-accent-color: red;
  --dp-bg-color: white;
  --dp-text-align: right;
  --dp-font-family: monospace;
}
</style>`;
