/* eslint-disable */

// URLs

const APPS_BASE = `u/datapane-test/apps/`;
const REPORTS_BASE = `u/datapane-test/reports/`;
const FILE_BASE = `u/datapane-test/files/`;

export const URLS = {
    PARAMS_APP: `${APPS_BASE}${Cypress.env("paramsAppId")}/`,
    NO_PARAMS_APP: `${APPS_BASE}${Cypress.env("noParamsAppId")}/`,
    SCHEDULE: `${APPS_BASE}${Cypress.env("paramsAppId")}/schedules/create/`,
    FILE: `${FILE_BASE}${Cypress.env("fileId")}/`,
    STYLE_REPORT: `${REPORTS_BASE}${Cypress.env("styleReportId")}/`,
    BUILDER_REPORT: `${REPORTS_BASE}${Cypress.env("builderReportId")}/`,
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
