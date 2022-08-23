import { createApp, defineCustomElement } from "vue";
import Report from "./src/components/ReportComponent.vue";
import TableBlock from "./src/components/blocks/Table.ce.vue";
import "./src/styles/report.scss";
import "../base/src/styles/tailwind.css";
import "highlight.js/styles/stackoverflow-light.css";
import "codemirror/lib/codemirror.css";
import "codemirror/theme/eclipse.css";
import CodeBlock from "./src/components/blocks/Code.ce.vue";

customElements.define("x-table-block", defineCustomElement(TableBlock));

const mountReport = (props: any) => {
    const app = createApp(Report, props);
    app.mount("#report");

    // Register WCs as standard Vue components in local mode
    app.component("dpx-code-block", CodeBlock);

    return app;
};

export { mountReport };
