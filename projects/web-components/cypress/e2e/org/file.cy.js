/* eslint-disable */
import { URLS } from "../../support/constants";

describe("File viewing", () => {
    before(() => {
        cy.dpLogin();
        cy.visit(URLS.FILE);
    });

    it("Should view a file and verify the information card exists", () => {
        cy.get("[data-cy=file-card]").should("exist");
    });
});
