/* eslint-disable */

const defaultTheme = require("tailwindcss/defaultTheme");
const config = require("./base.tailwind.config");
const { colors: fontFamily } = defaultTheme;

config.theme.fontFamily = {
    ...fontFamily,
    "dp-prose": "var(--dp-font-family)",
};

config.theme.extend.colors = {
    "dp-accent-light": "var(--dp-accent-secondary-color)",
    "dp-accent": "var(--dp-accent-color)",
    "dp-accent-text": "var(--dp-accent-text)",
    "dp-background": "var(--dp-bg-color)",
    "dp-light-gray": "var(--dp-light-gray)",
    "dp-dark-gray": "var(--dp-dark-gray)",
};

config.content = [
    "./report/src/**/*.{vue,js,ts}",
    "./node_modules/@variantjs/**/*.ts",
    "../python-client/src/datapane/resources/local_report/*.html",
];

module.exports = config;
