/* eslint-disable */

const config = require("./base.tailwind.config");

config.content = [
    "../dp-server/src/dp/apps/dp_core/templates/**/*.html",
    "../dp-server/src/dp/apps/dp_marketing/templates/**/*.html",
    "../dp-server/src/dp/apps/dp_org/templates/**/*.html",
    "../dp-server/src/dp/apps/dp_public/templates/**/*.html",
    "../dp-server/templates/**/*.html",
    // Report renderer
    "./report/src/**/*.{vue,js,ts}",
    "./node_modules/@variantjs/**/*.ts",
    // Web components
    "./template-components/src/**/*.{vue,js,ts}",
];

module.exports = config;
