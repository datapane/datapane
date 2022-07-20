/* eslint-disable */
import { URLS } from "../../support/constants";

const CRON_EXPRESSION = "* * * * *";
const UPDATED_CRON_EXPRESSION = "5 4 * * *";

describe("App scheduling", () => {
    before(() => {
        cy.dpLogin();
        cy.visit(URLS.SCHEDULE);
    });

    it("(e2e): Should create an app schedule, update, then delete it", () => {
        cy.intercept("POST", "**/schedules/").as("scheduleList");

        // Create
        cy.get("input[name=cron]").as("cronField").type(CRON_EXPRESSION);
        cy.scrollToFirst("[data-cy=button-save-schedule]")
            .as("saveScheduleButton")
            .click();

        cy.scrollToFirst("[data-cy=schedule]")
            .as("mostRecentSchedule")
            .get("[data-cy=schedule-cron]")
            .as("scheduleCron")
            .should("contain", CRON_EXPRESSION);

        // Update
        cy.get("@mostRecentSchedule")
            .find("[data-cy=button-update-schedule]")
            .click();
        cy.get("@cronField").clear().type(UPDATED_CRON_EXPRESSION);
        cy.get("@saveScheduleButton").click();
        cy.get("@scheduleCron").should("contain", UPDATED_CRON_EXPRESSION);

        // Delete
        cy.get("@mostRecentSchedule").within(() => {
            cy.get("[data-cy=button-delete-schedule]").click();
            cy.get("[data-cy=button-confirm-action]").click();
        });
    });
});
