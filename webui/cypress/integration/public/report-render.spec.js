/* eslint-disable */
import { URLS } from "../../support/constants";

describe("Report rendering", () => {
    before(() => {
        cy.dpLogin();
        cy.visit(URLS.STYLE_REPORT);
        cy.get("#djHideToolBarButton").click();
    });

    beforeEach(() => {
        Cypress.Cookies.preserveOnce("sessionid", "djdt");
    });

    it("Should switch between section tabs successfully", () => {
        cy.scrollToFirst("[data-cy=page-1]").click();

        cy.get("[data-cy=section-tabs]")
            .eq(2)
            .scrollIntoView()
            .within(() => {
                // Tab 0 state
                cy.get("[data-cy=block-shadow]").should("not.exist");
                cy.get("[data-cy=block-vega]").should("be.visible");
                cy.get("[data-cy=tab-1]").click();
                // Tab 1 state
                cy.get("[data-cy=block-shadow]").should("be.visible");
                cy.get("[data-cy=block-vega]").should("not.exist");
                cy.get("[data-cy=tab-0]").click();
                // Tab 0 state
                cy.get("[data-cy=block-shadow]").should("not.exist");
                cy.get("[data-cy=block-vega]").should("be.visible");
            });
    });

    it("Should find a rendered markdown block", () => {
        cy.scrollToFirst("[data-cy=page-0]").click();
        cy.scrollToFirst("[data-cy=block-markdown]").should("be.visible");
        cy.scrollToFirst("[data-cy=block-markdown]")
            .find("h2")
            .should("be.visible");
        cy.scrollToFirst("code[class=language-python]").should("be.visible");
    });

    it("Should find a rendered HTML table block", () => {
        cy.scrollToFirst("[data-cy=page-0]").click();
        cy.scrollToFirst("[data-cy=block-shadow]")
            .find("table")
            .should("be.visible");
    });

    it("Should find a rendered Vega block", () => {
        cy.scrollToFirst("[data-cy=page-0]").click();
        cy.scrollToFirst("[data-cy=block-vega]")
            .find("canvas")
            .should("be.visible");
    });

    it("Should find a rendered image block", () => {
        cy.scrollToFirst("[data-cy=page-0]").click();
        cy.scrollToFirst("[data-cy=block-media]").should("exist");
    });

    it("Should find a rendered big number block", () => {
        cy.scrollToFirst("[data-cy=page-0]").click();
        cy.scrollToFirst("[data-cy=block-bignumber]").should("be.visible");
    });

    it("Should find a rendered Bokeh block", () => {
        cy.scrollToFirst("[data-cy=page-2]").click();
        cy.scrollToFirst("[data-cy=block-bokeh]").should("be.visible");
    });

    it("Should find a rendered MPL block", () => {
        cy.scrollToFirst("[data-cy=page-2]").click();
        cy.scrollToFirst("[data-cy=block-svg]").should("be.visible");
    });

    it("Should find a rendered Plotly block", () => {
        cy.scrollToFirst("[data-cy=page-2]").click();
        cy.scrollToFirst("[data-cy=block-plotly]")
            .find("svg")
            .should("be.visible");
    });

    it("Should find a rendered Folium block", () => {
        cy.scrollToFirst("[data-cy=page-2]").click();
        cy.scrollToFirst("[data-cy=block-iframe]").should("be.visible");
    });

    it("Should find a rendered code block", () => {
        cy.scrollToFirst("[data-cy=page-2]").click();
        cy.scrollToFirst("[data-cy=block-code]")
            .find("code")
            .should("be.visible");
    });

    it("Should find a rendered iframe block", () => {
        cy.scrollToFirst("[data-cy=page-2]").click();
        cy.scrollToFirst("[data-cy=block-user-iframe]").should("be.visible");
    });

    it("Should find a rendered embed block", () => {
        cy.scrollToFirst("[data-cy=page-2]").click();
        cy.scrollToFirst("[data-cy=block-embed]").should("be.visible");
    });

    it("Should find a rendered text block", () => {
        cy.scrollToFirst("[data-cy=page-2]").click();
        cy.scrollToFirst("[data-cy=block-markdown]").should("be.visible");
    });

    it("Should find a rendered file block", () => {
        cy.scrollToFirst("[data-cy=page-2]").click();
        cy.scrollToFirst("[data-cy=block-file]").should("be.visible");
    });

    it("Should find a rendered DataTable block", () => {
        cy.scrollToFirst("[data-cy=block-datatable]")
            .find("revo-grid")
            .should("be.visible");
    });
});
