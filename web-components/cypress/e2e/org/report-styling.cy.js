/* eslint-disable */
import { URLS, HTML_HEADER, HTML_HEADER_LIGHT } from "../../support/constants";

describe("Changing a report's style", () => {
    it("Should set a global theme and submit empty an local theme, then verify that the global theme has been applied", () => {
        cy.dpLogin({ isStaff: true });

        // Change to accent-green bg-black theme
        cy.visit("/teams-settings-visual");
        cy.get("#djHideToolBarButton").click();
        cy.get("[name=html_header]").clear().type(HTML_HEADER);
        cy.get("[name=light_text]").check();
        cy.get("[data-cy=button-save-visual]").click();

        cy.clearCookies();
        cy.dpLogin({ isStaff: true });

        // Submit empty local visual form
        cy.visit(`${URLS.STYLE_REPORT}settings-visual`);
        cy.get("#id_prose_color").select("light_on_dark");
        cy.get("[name=style_header]").clear();
        cy.get("[type=submit]").click();

        cy.visit(URLS.STYLE_REPORT);

        // Verify global theme still applied
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
    });

    it("Should set a local theme and verify that it overwrites the global one", () => {
        cy.dpLogin({ isStaff: true });

        // Change to global light prose
        cy.visit("/teams-settings-visual");
        cy.get("#djHideToolBarButton").click();
        cy.get("[name=light_text]").check();
        cy.get("[data-cy=button-save-visual]").click();

        cy.clearCookies();
        cy.dpLogin({ isStaff: true });

        // Set local theme
        cy.visit(`${URLS.STYLE_REPORT}settings-visual`);
        cy.get("[data-cy=button-load-global-theme]").click();
        cy.get("[name=style_header]").clear().type(HTML_HEADER_LIGHT);
        cy.get("#id_prose_color").select("dark_on_light");
        cy.get("[type=submit]").click();

        cy.visit(URLS.STYLE_REPORT);

        // Verify local theme applied
        cy.get("[data-cy=page-1]").click();
        cy.scrollToFirst("[data-cy=tab-0]").should(
            "have.css",
            "color",
            "rgb(255, 0, 0)",
        );
        cy.scrollToFirst("[data-cy=block-markdown]")
            .find("p")
            .should("have.css", "color", "rgb(55, 65, 81)");
    });

    it("Should empty both global and local themes, and verify fallback default theme", () => {
        cy.dpLogin({ isStaff: true });

        // Delete global header
        cy.visit("/teams-settings-visual");
        cy.get("#djHideToolBarButton").click();
        cy.get("[name=html_header]").clear();
        cy.get("[data-cy=button-save-visual]").click();

        cy.clearCookies();
        cy.dpLogin({ isStaff: true });

        // Delete local header
        cy.visit(`${URLS.STYLE_REPORT}settings-visual`);
        cy.get("[name=style_header]").clear();
        cy.get("[type=submit]").click();

        cy.visit(URLS.STYLE_REPORT);

        // Verify default (indigo) theme
        cy.get("[data-cy=page-1]").click();
        cy.scrollToFirst("[data-cy=tab-0]").should(
            "have.css",
            "color",
            "rgb(78, 70, 229)",
        );
        cy.scrollToFirst("[data-cy=block-markdown]")
            .find("p")
            .should("have.css", "text-align", "left")
            .and("have.css", "font-family", "Inter, ui-sans-serif, system-ui");
        cy.get("[data-cy=report-component").should(
            "have.css",
            "background-color",
            "rgb(255, 255, 255)",
        );
    });
});
