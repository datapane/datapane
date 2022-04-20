/* eslint-disable */
import { URLS } from "../../support/constants";

const XLSX = require("xlsx");
const EXPECTED_NUM_DS_ROWS = 1000;

const validateCsv = (csvDoc) => {
    // Validates the CSV header and num lines
    const lines = csvDoc.split("\n").filter((l) => l.length);
    cy.wrap(lines[0]).should("eq", "A,B,C,D,E,F");
    cy.wrap(lines.length).should("eq", EXPECTED_NUM_DS_ROWS + 1);
};

const validateExcel = (excelDoc) => {
    // Validates the Excel header and num lines
    const workbook = XLSX.read(new Uint8Array(excelDoc), { type: "array" });
    const rows = XLSX.utils.sheet_to_json(workbook.Sheets["Sheet1"]);
    cy.wrap(rows.length).should("eq", EXPECTED_NUM_DS_ROWS);
    cy.wrap(Object.keys(rows[0]).join(",")).should("eq", "A,B,C,D,E,F");
};

const interceptExport = (format, doc) => {
    const urlPattern = new RegExp(
        `.*\\/extensions\\/export\/.*\\/\\?export_format=${format}$`,
        "g"
    );
    return cy.intercept("GET", urlPattern, (req) => {
        req.reply((res) => {
            doc.content = res.body;
        });
    });
};

describe("Report datatable block extensions", () => {
    before(() => {
        cy.dpLogin();
    });

    beforeEach(() => {
        Cypress.Cookies.preserveOnce("sessionid", "djdt");
        cy.visit(URLS.STYLE_REPORT);
        cy.get("#djHideToolBarButton").click();
    });

    it("Should export a DataTable CSV with the correct headers and no. rows", () => {
        const doc = { content: "" };

        interceptExport("CSV", doc).as("csvDownload");

        cy.scrollToFirst("[data-cy=page-2]").click();

        cy.scrollToFirst("[data-cy=block-datatable]")
            .find("[data-cy=dropdown-export]")
            .as("dropdown-export")
            .click();
        cy.get("@dropdown-export").within(() => {
            cy.get("[data-cy=dropdown-option-download-original-csv]").click();
            cy.wait("@csvDownload").then(() => validateCsv(doc.content));
        });
    });

    it("Should export a DataTable Excel file with the correct headers and no. rows", () => {
        const doc = { content: "" };

        interceptExport("EXCEL", doc).as("excelDownload");

        cy.scrollToFirst("[data-cy=page-2]").click();

        cy.scrollToFirst("[data-cy=block-datatable]")
            .find("[data-cy=dropdown-export]")
            .as("dropdown-export")
            .click();
        cy.get("@dropdown-export").within(() => {
            cy.get("[data-cy=dropdown-option-download-original-excel]").click();
            cy.wait("@excelDownload").then(() => validateExcel(doc.content));
        });
    });

    it("Should run a SQL query successfully", () => {
        cy.scrollToFirst("[data-cy=page-2]").click();

        cy.scrollToFirst("[data-cy=block-datatable]")
            .find(".rgRow")
            .should("have.length.gt", 2);

        cy.get("[data-cy=btn-open-query").click();

        cy.get(".CodeMirror").then((editor) => {
            editor[0].CodeMirror.setValue("SELECT SUM(A) FROM $table");
            cy.get("[data-cy=btn-run-query").click();
            cy.get(".rgRow").should("have.length", 2);
            cy.get("[data-cy=btn-reset-data]").click();
            cy.get(".rgRow").should("have.length.gt", 2);
        });
    });

    it("Should run a SQL query with errors", () => {
        cy.scrollToFirst("[data-cy=page-2]").click();

        cy.get("[data-cy=btn-open-query").click();

        cy.get(".CodeMirror").then((editor) => {
            editor[0].CodeMirror.setValue("should err");
            cy.get("[data-cy=btn-run-query").click();
            cy.get("[data-cy=alasql-error-msg]").should("exist");
            cy.get("[data-cy=btn-reset-data").click();
            cy.get("[data-cy=alasql-error-msg]").should("not.exist");
        });
    });
});
