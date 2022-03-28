/* eslint-disable */

const defaultTheme = require("tailwindcss/defaultTheme");
const { colors: fontFamily } = defaultTheme;

module.exports = {
    darkMode: "class",
    theme: {
        fontFamily: {
            // TODO - move to extends?
            ...fontFamily,
            "dp-prose": "var(--dp-font-family)",
        },
        extend: {
            colors: {
                "dp-accent-light": "var(--dp-accent-secondary-color)",
                "dp-accent": "var(--dp-accent-color)",
                "dp-accent-text": "var(--dp-accent-text)",
                "dp-background": "var(--dp-bg-color)",
                "dp-light-gray": "var(--dp-light-gray)",
                "dp-dark-gray": "var(--dp-dark-gray)",
            },
            typography: {
                DEFAULT: {
                    // Disable prose being applied to code elements
                    css: {
                        pre: false,
                        code: false,
                        "pre code": false,
                        "code::before": false,
                        "code::after": false,
                    },
                },
            },
            fontFamily: {
                sans: ["Inter var", ...defaultTheme.fontFamily.sans],
            },
            width: {
                80: "20rem",
                96: "24rem",
                "640px": "640px",
            },
            minWidth: {
                "100px": "100px",
            },
            maxWidth: {
                "150px": "150px",
            },
            height: {
                "480px": "480px",
            },
            flex: {
                fixed: "0 0 auto",
                "fixed-64": "0 0 16rem",
                full: "0 0 100%",
                "initial-grow": "1 0 0",
                "initial-80": "0 1 20rem",
            },
            gridTemplateColumns: {
                fit: "repeat(auto-fit, minmax(0, 1fr))",
            },
            gridTemplateRows: {
                fit: "repeat(auto-fit, minmax(auto, auto))",
            },
        },
        fontSize: {
            xs: "0.75rem",
            sm: "0.875rem",
            base: "1rem",
            lg: "1.125rem",
            xl: "1.25rem",
            "2xl": "1.5rem",
            "3xl": "1.875rem",
            "4xl": "2.25rem",
            "5xl": "3rem",
            "6xl": "4rem",
        },
    },
    variants: {
        extend: {
            backgroundColor: ["active", "odd"],
            textColor: ["active"],
            display: ["group-hover"],
            opacity: ["disabled"],
            cursor: ["disabled"],
        },
        opacity: ["responsive", "hover", "focus", "disabled"],
    },
    plugins: [
        require("@tailwindcss/forms"),
        require("@tailwindcss/typography"),
        require("@tailwindcss/aspect-ratio"),
    ],
    content: [
        // FE files
        "./src/**/*.{vue,js,ts}",
        // BE files
        // TODO - update paths when deploying
        "../datapane-hosted/dp-server/src/dp/apps/dp_core/templates/**/*.html",
        "../datapane-hosted/dp-server/src/dp/apps/dp_marketing/templates/**/*.html",
        "../datapane-hosted/dp-server/src/dp/apps/dp_comments/templates/**/*.html",
        "../datapane-hosted/dp-server/src/dp/apps/dp_org/templates/**/*.html",
        "../datapane-hosted/dp-server/src/dp/apps/dp_public/templates/**/*.html",
        "../datapane-hosted/dp-server/templates/**/*.html",
        "./node_modules/@variantjs/**/*.ts",
    ],
    safelist: [
        // TODO - remove redundant items
        { pattern: /bp3-.*/ },
        { pattern: /DayPicker.*/ },
        { pattern: /grid-cols-.*/ },
        { pattern: /grid-rows-.*/ },
        { pattern: /grid-flow-.*/ },
        { pattern: /dp-btn-.*/ },
        "text-teal-400",
        "text-orange-400",
        "text-blue-400",
        "text-green-400",
        "text-indigo-400",
        "text-red-400",
        "mb-3",
        "bg-green-100",
        "bg-green-800",
        "bg-red-100",
        "bg-red-800",
        "max-w-screen-xl",
        "max-w-3xl",
        "max-w-full",
        "w-full",
        "h-full",
        "max-w-none",
        "absolute",
        "top-0",
        "left-0",
    ],
};
