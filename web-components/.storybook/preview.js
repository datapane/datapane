import { app } from "@storybook/vue3";
import { plugin as formkitPlugin, defaultConfig } from "@formkit/vue";
import { createPinia } from "pinia";
import { formkitConfig } from "../report/src/components/controls/formkit";
import "../base/src/styles/tailwind.css";
import "../report/src/styles/report.scss";
import "../report/src/styles/user-iframe.css";
import "highlight.js/styles/stackoverflow-light.css";
import "codemirror/lib/codemirror.css";
import "codemirror/theme/eclipse.css";

const pinia = createPinia();

app.use(formkitPlugin, defaultConfig(formkitConfig));
app.use(pinia);

export const parameters = {
    actions: { argTypesRegex: "^on[A-Z].*" },
    controls: {
        matchers: {
            color: /(background|color)$/i,
            date: /Date$/,
        },
    },
};
