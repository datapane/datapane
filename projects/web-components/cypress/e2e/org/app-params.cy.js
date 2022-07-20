/* eslint-disable */
import { URLS } from "../../support/constants";

describe("Using an app's parameters", () => {
    const checkErrorExists = () => {
        cy.get("@field")
            .parents(".formkit-outer")
            .first()
            .find("[data-message-type=validation]")
            .should("exist");
    };

    const clearFieldInput = (name) => {
        cy.get("@field").siblings().find("input").clear();
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
        cy.get("[data-cy=datetime-local-field]").should("exist");
        cy.get("[data-cy=time-field]").should("exist");
        cy.get("[data-cy=float-field]").should("have.length", 2);
        cy.get("[data-cy=file-field]").should("exist");
    });

    it("Empties required list field and checks warning", () => {
        cy.get("[data-cy=list-field-__LIST__REQUIRED__]")
            .find("button")
            .click();
        cy.get("label:contains('__LIST__REQUIRED__')").as("field");
        checkErrorExists();
    });

    it("Empties required string field and checks warning", () => {
        cy.get("label:contains('__STRING__REQUIRED__')").as("field");
        clearFieldInput();
        checkErrorExists();
    });

    it("Empties required int field and checks warning", () => {
        cy.get("label:contains('__INT__REQUIRED__')").as("field");
        clearFieldInput();
        checkErrorExists();
    });

    it("Empties required float field and checks warning", () => {
        cy.get("label:contains('__FLOAT__REQUIRED__')").as("field");
        clearFieldInput();
        checkErrorExists();
    });

    it("Sets invalid upper bound on int field and checks warning", () => {
        cy.get("label:contains('__INT__UPPERBOUND__')")
            .siblings()
            .as("field")
            .find("input")
            .type("11");
        checkErrorExists();
    });
});
