const vue = require("@vitejs/plugin-vue");

module.exports = {
    stories: [
        "../src/**/*.stories.mdx",
        "../src/**/*.stories.@(js|jsx|ts|tsx)",
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
                            tag.startsWith("dp-") ||
                            tag.startsWith("x-") ||
                            tag.startsWith("revo-"),
                    },
                },
            })
        );
        return config;
    },
};
