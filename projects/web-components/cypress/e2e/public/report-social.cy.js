/* eslint-disable */
import { URLS } from "../../support/constants";
const uuid = require("uuid");

const makeTextComment = () => `Test comment ${uuid.v4()}`;
const testComment = makeTextComment();
const editedTestComment = makeTextComment();

describe("Report Social", () => {
    before(() => {
        cy.dpLogin();
    });

    beforeEach(() => {
        Cypress.Cookies.preserveOnce("sessionid", "djdt");
        cy.visit(URLS.STYLE_REPORT);
        cy.get("#djHideToolBarButton").click();
    });

    it("(e2e): Should post and edit a comment, then delete", () => {
        cy.get("[data-cy=button-comment]").click();

        // Post commment
        cy.intercept("GET", "**/comments/box/**/").as("posted");
        cy.get("[data-cy=input-comment]").type(testComment);
        cy.get("[data-cy=button-post-comment]").click();
        cy.wait("@posted");
        cy.get("[data-cy=comment-box]").should(($commentBox) => {
            expect($commentBox).to.contain(testComment);
        });

        // Edit comment
        cy.intercept("POST", "**/comments/edit/**/").as("edit");
        cy.get("[data-cy=comment-box]")
            .find("li")
            .last()
            .as("comment")
            .within(() => {
                cy.get("[data-cy=button-edit-comment]").click();
                cy.get("[data-cy=input-edit-comment]")
                    .clear()
                    .type(editedTestComment);
                cy.get("[data-cy=button-update-comment]").click();
            });

        cy.wait("@edit");
        cy.get("[data-cy=comment-box]").should("contain", editedTestComment);

        // Delete comment
        cy.intercept("POST", "**/comments/delete_comment/**/").as("delete");
        cy.visit(URLS.STYLE_REPORT);
        cy.get("[data-cy=button-comment]").click();
        cy.get("@comment").find("[data-cy=button-delete-comment]").click();

        cy.wait("@delete");
        cy.get("[data-cy=comment-box]").should("not.contain", testComment);
    });
});
