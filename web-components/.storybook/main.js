const vue = require("@vitejs/plugin-vue");
const replace = require("@rollup/plugin-replace");
const tailwindcss = require("tailwindcss");

module.exports = {
    stories: [
        "../report/src/**/*.stories.mdx",
        "../report/src/**/*.stories.@(js|jsx|ts|tsx)",
    ],
    addons: ["@storybook/addon-links", "@storybook/addon-essentials"],
    framework: "@storybook/vue3",
    core: {
        builder: "@storybook/builder-vite",
    },
    async viteFinal(config, { configType }) {
        config.css = {
            postcss: {
                plugins: [
                    tailwindcss({
                        config: "./report.tailwind.config.js",
                    }),
                ],
            },
        };

        config.plugins = config.plugins.filter((p) => p.name !== "vite:vue");
        config.plugins.push(
            vue({
                template: {
                    compilerOptions: {
                        isCustomElement: (tag) =>
                            tag.startsWith("revo-") || tag.startsWith("x-"),
                    },
                },
            }),
            replace({
                include: ["../node_modules/@bokeh/**/*.js"],
                values: {
                    // shim jquery to window object for bokehjs
                    jQuery: "window.jQuery",
                },
                preventAssignment: false,
            }),
        );

        if (configType === "PRODUCTION") {
            // Serve bundled storybook instance when running from datapane.com
            config.base = "/static/storybook/";
        }

        return config;
    },
};
