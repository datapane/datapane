/* eslint-disable */

const config = require("./base.tailwind.config");

config.content = [
    "../../../dp-server/src/dp/apps/dp_core/templates/**/*.html",
    "../../../dp-server/src/dp/apps/dp_marketing/templates/**/*.html",
    "../../../dp-server/src/dp/apps/dp_comments/templates/**/*.html",
    "../../../dp-server/src/dp/apps/dp_org/templates/**/*.html",
    "../../../dp-server/src/dp/apps/dp_public/templates/**/*.html",
    "../../../dp-server/templates/**/*.html",
];

module.exports = config;
