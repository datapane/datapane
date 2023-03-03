import { createApp, defineCustomElement } from "vue";
import { plugin as formkitPlugin, defaultConfig } from "@formkit/vue";
import { formkitConfig } from "./src/components/controls/formkit";
import Report from "./src/components/ReportContainer.vue";
import TableBlock from "./src/components/blocks/Table.ce.vue";
import iframeResize from "iframe-resizer/js/iframeResizer";
import { createPinia } from "pinia";
import "./src/styles/report.scss";
import "highlight.js/styles/stackoverflow-light.css";
import "codemirror/lib/codemirror.css";
import "codemirror/theme/eclipse.css";

// Async load `tailwind.css` so that it can be split into own file by rollup
import("./tailwind");

customElements.define("x-table-block", defineCustomElement(TableBlock));

const parseElementProps = (elId: string): any => {
    const propsEl = document.getElementById(elId);
    if (!propsEl || !propsEl.textContent) {
        throw new Error("Couldn't find props JSON element");
    }
    return JSON.parse(propsEl.textContent);
};

const mountReport = (props: any) => {
    const app = createApp(Report, props);
    const pinia = createPinia();
    app.use(pinia);
    app.use(formkitPlugin, defaultConfig(formkitConfig));
    app.mount("#report");
    return app;
};

export {
    mountReport,
    parseElementProps,
    // Export iframeResize for use in ipython embedding
    iframeResize,
};
