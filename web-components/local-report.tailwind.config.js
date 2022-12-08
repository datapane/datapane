/* eslint-disable */

const defaultTheme = require("tailwindcss/defaultTheme");
const config = require("./base.tailwind.config");
const { colors: fontFamily } = defaultTheme;

config.content = [
    "./report/src/**/*.{vue,js,ts}",
    "./node_modules/@variantjs/**/*.ts",
    "../python-client/src/datapane/resources/local_report/*.html",
];

module.exports = config;
