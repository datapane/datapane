const vue = require("@vitejs/plugin-vue");

module.exports = {
    stories: [
        "../report/src/**/*.stories.mdx",
        "../report/src/**/*.stories.@(js|jsx|ts|tsx)",
    ],
    addons: ["@storybook/addon-links", "@storybook/addon-essentials"],
    framework: "@storybook/vue3",
    core: {
        builder: "storybook-builder-vite",
    },
    async viteFinal(config, { configType }) {
        // config.plugins = config.plugins ?? [];
        config.plugins = config.plugins.filter((p) => p.name !== "vite:vue");
        config.plugins.push(
            vue({
                template: {
                    compilerOptions: {
                        isCustomElement: (tag) =>
                            tag.startsWith("dpx-") ||
                            tag.startsWith("x-") ||
                            tag.startsWith("revo-"),
                    },
                },
            })
        );
        return config;
    },
};
