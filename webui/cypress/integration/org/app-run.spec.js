/* eslint-disable */
const uuid = require("uuid");
import { URLS } from "../../support/constants";

const STR_VAL = uuid.v4();
const INT_VAL = 1;
const FLOAT_VAL = 1.1;
const FILE_PARAM_NAME = "file_upload.txt";

const visit = (url) => {
    cy.visit(url);
    cy.get("#djHideToolBarButton").click();
};

const inputParamField = (label, content) => {
    return cy
        .get(`label:contains('${label}')`)
        .siblings()
        .find("input")
        .first()
        .clear()
        .type(content);
};

describe("Running an app", () => {
    before(() => {
        cy.dpLogin();
    });

    beforeEach(() => {
        Cypress.Cookies.preserveOnce("sessionid", "djdt");
    });

    it("(e2e): Should run an app and verify changed parameters in report, run history and run output", () => {
        visit(URLS.PARAMS_APP);
        // Run and verify report result
        cy.intercept("GET", "**/runs/**").as("getRuns");

        inputParamField("__STRING__REQUIRED__", STR_VAL);
        inputParamField("__INT__", INT_VAL);
        inputParamField("__FLOAT__", FLOAT_VAL);

        // params change debounce
        cy.wait(500);

        cy.get("[data-cy=file-field]").attachFile(FILE_PARAM_NAME);

        // file is attached programatically so we need to manually trigger the store update
        cy.window().then((win) => {
            win.$testResources.paramsStore.serialized[
                "__FILE__"
            ] = FILE_PARAM_NAME;
        });

        cy.get("[data-cy=button-run]").click();
        cy.wait("@getRuns", { requestTimeout: 10000 });
        cy.get("#inline-report").should("contain", STR_VAL);
        cy.get("#inline-report").should("contain", INT_VAL);
        cy.get("#inline-report").should("contain", FLOAT_VAL);
        cy.get("#inline-report").should("contain", "file upload fixture");

        // Run history page
        cy.visit(`${URLS.PARAMS_APP}runs/`);
        cy.get("[data-cy=run-view-output]").first().click();
        cy.get("[data-cy=modal-component]").should("be.visible");
    });

    it("Should run an app and cancel", () => {
        visit(URLS.PARAMS_APP);

        // Seems like a small delay is needed between page load and run to allow form fields to be populated
        // TODO - use a more deterministic method
        cy.wait(500);

        // Run
        cy.intercept("POST", "**/runs/new/").as("getRuns");
        cy.get("[data-cy=button-run]").click();
        cy.wait("@getRuns");
        cy.intercept("POST", "**/stop/").as("stopRun");

        // Stop
        cy.get("[data-cy=button-cancel-run]").trigger("mouseover").click();
        cy.wait("@stopRun");
        cy.scrollToFirst("[data-cy=no-report]").should("be.visible");
    });

    it("Should error based on invalid param", () => {
        visit(URLS.PARAMS_APP);
        cy.intercept("POST", "**/runs/new/").as("newRun");
        cy.get("label:contains('__STRING__REQUIRED__')")
            .siblings()
            .find("input")
            .clear();
        cy.get("[data-cy=button-run]").click();
        cy.wait("@newRun");
        cy.get("[data-cy=app-run-errors]").should("be.visible");
    });

    it("Should run an app with no parameters", () => {
        visit(URLS.NO_PARAMS_APP);
        cy.intercept("GET", "**/runs/**").as("getRuns");
        cy.get("[data-cy=button-run]").click();

        cy.wait("@getRuns", { requestTimeout: 10000 });
        cy.get("#inline-report").should("contain", "__REPORT_RENDERED__");
    });
});
