/* eslint-disable */
// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add("login", (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add("drag", { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add("dismiss", { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This is will overwrite an existing command --
// Cypress.Commands.overwrite("visit", (originalFn, url, options) => { ... })

import "cypress-file-upload";

Cypress.Commands.add("dpLogin", (opts = { isStaff: false }) => {
    Cypress.log({
        name: "DP_LOGIN",
        message: "Logging in",
    });
    cy.request({
        method: "POST",
        url: "accounts/login/",
        form: true,
        body: {
            login: Cypress.env(opts.isStaff ? "staffEmail" : "testEmail"),
            password: Cypress.env(
                opts.isStaff ? "staffPassword" : "testPassword"
            ),
        },
    });
});

Cypress.Commands.add("dpSetInitialReport", () => {
    Cypress.log({
        name: "DP_SET_INITIAL_REPORT",
        message: "Setting placeholder report",
    });
    cy.get(".CodeMirror").then((editor) => {
        const cm = editor[0].CodeMirror;
        cm.setValue("<Page><Text>Initial report</Text></Page>");
        cy.wait(2000); // 2s debounce on preview
    });
    cy.intercept("POST", "**/report-editor/**").as("addTemplate");
});

Cypress.Commands.add("scrollToFirst", (selector) => {
    return cy.get(selector).first().scrollIntoView();
});
