/* eslint-disable */
import { URLS } from "../../support/constants";

describe("Using an app's parameters", () => {
    const checkErrorExists = () => {
        cy.get("@siblings").find("[data-cy=param-error]").should("exist");
    };

    const clearFieldInput = (name) => {
        cy.get(`label:contains("${name}")`)
            .siblings()
            .as("siblings")
            .find("input")
            .clear();
    };

    before(() => {
        cy.dpLogin();
        cy.visit(URLS.PARAMS_APP);
        cy.get("#djHideToolBarButton").click();
    });

    it("Checks that all fields are rendered", () => {
        cy.get("[data-cy=list-field]").should("have.length", 2);
        cy.get("[data-cy=list-field-choices]").should("exist");
        cy.get("[data-cy=string-field]").should("have.length", 2);
        cy.get("[data-cy=boolean-field]").should("exist");
        cy.get("[data-cy=int-field-unbounded]").should("have.length", 3);
        cy.get("[data-cy=int-field-bounded]").should("exist");
        cy.get("[data-cy=enum-field]").should("exist");
        cy.get("[data-cy=datetime-field]").should("have.length", 2);
        cy.get("[data-cy=time-field]").should("exist");
        cy.get("[data-cy=float-field]").should("have.length", 2);
        cy.get("[data-cy=file-field]").should("exist");
    });

    it("Empties required list field and checks warning", () => {
        cy.get("label:contains('__LIST__REQUIRED__')")
            .siblings()
            .as("siblings")
            .find(".bp4-tag-remove")
            .click();
        checkErrorExists();
    });

    it("Empties required string field and checks warning", () => {
        clearFieldInput("__STRING__REQUIRED__");
        checkErrorExists();
    });

    it("Empties required int field and checks warning", () => {
        clearFieldInput("__INT__REQUIRED__");
        checkErrorExists();
    });

    it("Empties required float field and checks warning", () => {
        clearFieldInput("__FLOAT__REQUIRED__");
        checkErrorExists();
    });

    it("Sets invalid upper bound on int field and checks warning", () => {
        cy.get("label:contains('__INT__UPPERBOUND__')")
            .siblings()
            .as("siblings")
            .find("input")
            .type("11");
        checkErrorExists();
    });

    it("Checks datetime field calendar popup", () => {
        cy.get("label:contains('__DATETIME__')")
            .siblings()
            .find("input")
            .click();
        cy.get(".DayPicker").should("exist");
    });
});
