import "../src/styles/tailwind.css";
import "../src/styles/report.scss";
import "highlight.js/styles/stackoverflow-light.css";

export const parameters = {
    actions: { argTypesRegex: "^on[A-Z].*" },
    controls: {
        matchers: {
            color: /(background|color)$/i,
            date: /Date$/,
        },
    },
};
