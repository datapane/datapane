import "../base/src/styles/tailwind.css";
import "../report/src/styles/report.scss";
import "../report/src/styles/user-iframe.css";
import "highlight.js/styles/stackoverflow-light.css";
import "codemirror/lib/codemirror.css";
import "codemirror/theme/eclipse.css";

export const parameters = {
    actions: { argTypesRegex: "^on[A-Z].*" },
    controls: {
        matchers: {
            color: /(background|color)$/i,
            date: /Date$/,
        },
    },
};
