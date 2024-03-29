/* eslint-disable */
import { URLS } from "../../support/constants";

const CSS_HEADER = `<style>
:root {
  --dp-accent-color: green;
  --dp-bg-color: black;
  --dp-text-align: right;
  --dp-font-family: monospace;
}
</style>`;

const MALICIOUS_HEADER =
    "<style onload=\"window.location.href = 'https://google.com'\"></style><script id='cy-malicious-script'></script>";

describe("Changing a report's style", () => {
    before(() => {
        cy.dpLogin();
    });

    beforeEach(() => {
        Cypress.Cookies.preserveOnce("sessionid", "djdt");
        cy.visit(`${URLS.STYLE_REPORT}settings-visual`);
        cy.get("#djHideToolBarButton").click();
    });

    it("(e2e): Should change the report to a dark theme then reset to default", () => {
        // Change to accent-green bg-black theme
        cy.get("#id_style_header").clear().type(CSS_HEADER);
        cy.get("#id_prose_color").select("light_on_dark");
        cy.get("button[type=submit]").click();

        cy.visit(URLS.STYLE_REPORT);

        // Verify theme applied
        cy.get("[data-cy=page-1]").click();
        cy.scrollToFirst("[data-cy=tab-0]").should(
            "have.css",
            "color",
            "rgb(0, 128, 0)",
        );
        cy.scrollToFirst("[data-cy=block-markdown]")
            .find("p")
            .should("have.css", "color", "rgb(209, 213, 219)")
            .and("have.css", "text-align", "right")
            .and("have.css", "font-family", "monospace");
        cy.get("[data-cy=report-component").should(
            "have.css",
            "background-color",
            "rgb(0, 0, 0)",
        );

        cy.visit(`${URLS.STYLE_REPORT}settings-visual`);

        // Revert to default theme
        cy.get("[data-cy=button-load-global-theme]").click();
        cy.get("#id_prose_color").select("dark_on_light");
        cy.get("button[type=submit]").click();

        cy.visit(URLS.STYLE_REPORT);

        // Verify theme reverted
        cy.get("[data-cy=page-1]").click();
        cy.scrollToFirst("[data-cy=tab-0]").should(
            "have.css",
            "color",
            "rgb(78, 70, 229)",
        );
        cy.scrollToFirst("[data-cy=block-markdown]")
            .find("p")
            .should("have.css", "color", "rgb(55, 65, 81)")
            .and("have.css", "text-align", "left")
            .and("have.css", "font-family", "Inter, ui-sans-serif, system-ui");
        cy.get("[data-cy=report-component").should(
            "have.css",
            "background-color",
            "rgb(255, 255, 255)",
        );
    });

    it("Should sanitise attempted JS injection", () => {
        cy.get("#id_style_header").clear().type(MALICIOUS_HEADER);
        cy.get("button[type=submit]").click();

        cy.visit(URLS.STYLE_REPORT);

        cy.get("script[id=cy-malicious-script]").should("not.exist");
        cy.get("[data-cy=report-component]").should("exist");
    });
});
