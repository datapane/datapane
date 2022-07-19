/* eslint-disable */
import { URLS } from "../../support/constants";

const CSS_HEADER = `:root {
  --dp-accent-color: green;
  --dp-bg-color: black;
  --dp-text-align: right;
  --dp-font-family: monospace;
}`;

describe("Changing a report's style", () => {
    before(() => {
        cy.dpLogin();
        cy.visit(`${URLS.STYLE_REPORT}settings-visual`);
        cy.get("#djHideToolBarButton").click();
    });

    it("(e2e): Should change the report to a dark theme then reset to default", () => {
        // Change to accent-green bg-black theme
        cy.get("#id_style_header").clear().type(CSS_HEADER);
        cy.get("#id_is_light_prose").check();
        cy.get("button[type=submit]").click();

        cy.visit(URLS.STYLE_REPORT);

        // Verify theme applied
        cy.get("[data-cy=page-0]").should(
            "have.css",
            "color",
            "rgb(0, 128, 0)"
        );
        cy.scrollToFirst("[data-cy=block-markdown]")
            .find("p")
            .should("have.css", "color", "rgb(209, 213, 219)")
            .and("have.css", "text-align", "right")
            .and("have.css", "font-family", "monospace");
        cy.get("[data-cy=report-component").should(
            "have.css",
            "background-color",
            "rgb(0, 0, 0)"
        );

        cy.visit(`${URLS.STYLE_REPORT}settings-visual`);

        // Revert to default theme
        cy.get("[data-cy=button-load-global-theme]").click();
        cy.get("#id_is_light_prose").uncheck();
        cy.get("button[type=submit]").click();

        // Verify theme reverted
        cy.get("[data-cy=page-0]").should(
            "have.css",
            "color",
            "rgb(78, 70, 229)"
        );
        cy.scrollToFirst("[data-cy=block-markdown]")
            .find("p")
            .should("have.css", "color", "rgb(55, 65, 81)")
            .and("have.css", "text-align", "justify")
            .and(
                "have.css",
                "font-family",
                '"Inter var", ui-sans-serif, system-ui'
            );
        cy.get("[data-cy=report-component").should(
            "have.css",
            "background-color",
            "rgb(255, 255, 255)"
        );
    });
});
