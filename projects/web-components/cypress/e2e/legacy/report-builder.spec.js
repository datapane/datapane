/* eslint-disable */
const uuid = require("uuid");
import { URLS } from "../../support/constants";

const REPORT_TEXT = uuid.v4();

const REPORT_SIDE_LAYOUT = `<Pages layout="side">
    <Page>
        <Text>Page: 1</Text>
    </Page>
    <Page>
        <Text>Page: 2</Text>
    </Page>
</Pages>`;

const addOuterPage = (cm) =>
    cm.setValue(`<Page>${cm.getValue().replace(/<\/?Page>/g, "")}</Page>`);

describe("Report builder", () => {
    before(() => {
        cy.dpLogin();
    });

    beforeEach(() => {
        Cypress.Cookies.preserveOnce("sessionid", "djdt");
        cy.visit(`${URLS.BUILDER_REPORT}edit/`);
        cy.get("#djHideToolBarButton").click();
    });

    it("(e2e): Should add assets to a report, preview the report, and save", () => {
        cy.dpSetInitialReport();

        // A report with markdown should exist on load
        cy.get("[data-cy=block-markdown]").should("exist");

        // Preview
        cy.get(".CodeMirror").then((editor) => {
            const cm = editor[0].CodeMirror;
            cm.setValue(`<Text>${REPORT_TEXT}</Text>`);
            cy.get("[data-cy=button-insert-assets]").click();
            cy.get("[data-cy=button-asset-Table]")
                .first()
                .click()
                .then(() => {
                    addOuterPage(cm);
                    cy.wait(2000); // 2s debounce on preview
                    cy.get("[data-cy=block-shadow]").should("exist");
                    cy.get("[data-cy=report-component]").should(
                        "contain",
                        REPORT_TEXT
                    );
                });
        });

        // Save
        cy.get("[data-cy=button-save-changes]").click();
        cy.wait("@addTemplate");
        cy.wait(1000); // TODO - this is an anti-pattern but the BE seems to take a sec to catch up, and there's no network response that can provide a cue

        // Verify updated report
        cy.visit(URLS.BUILDER_REPORT);
        cy.get("[data-cy=report-component]").should("contain", REPORT_TEXT);
    });

    it("Should error on adding invalid XML", () => {
        cy.dpSetInitialReport();

        cy.get("[data-cy=builder-error]").should("not.exist");

        cy.get(".CodeMirror").then((editor) => {
            const cm = editor[0].CodeMirror;
            cm.setValue("<Unclosed>should err");
            cy.wait(2000); // 2s debounce on preview
            cy.get("[data-cy=builder-error]").should("be.visible");
        });
    });

    it("Should error on invalid report schema", () => {
        cy.dpSetInitialReport();

        cy.get("[data-cy=builder-error]").should("not.exist");

        cy.get(".CodeMirror").then((editor) => {
            const cm = editor[0].CodeMirror;
            cm.setValue("<Page>valid XML but unwrapped text should err</Page>");
            cy.wait(2000); // 2s debounce on preview
            cy.get("[data-cy=builder-error]").should("be.visible");
        });
    });

    it("Should create and navigate between a report with vertical pages", () => {
        cy.get(".CodeMirror").then((editor) => {
            const cm = editor[0].CodeMirror;
            cm.setValue(REPORT_SIDE_LAYOUT);
            cy.wait(2000); // 2s debounce on preview
            cy.get("[data-cy=block-markdown]").should("contain", "Page: 1");
            cy.get("[data-cy=page-1]").click();
            cy.get("[data-cy=block-markdown]").should("contain", "Page: 2");
        });
    });
});
