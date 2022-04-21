import { createApp, defineCustomElement } from "vue";
import Report from "./src/components/Report.vue";
import CodeBlock from "./src/components/blocks/Code.ce.vue";
import TableBlock from "./src/components/blocks/Table.ce.vue";
import "./src/styles/report.scss";
import "../base/src/styles/tailwind.css";
import "highlight.js/styles/stackoverflow-light.css";

customElements.define("x-table-block", defineCustomElement(TableBlock));

window.addEventListener("DOMContentLoaded", () => {
    const windowProps = window.reportProps;
    const reportProps = {
        ...windowProps,
        htmlHeader: windowProps.htmlHeader,
        report: {
            ...windowProps.report,
            document: windowProps.report.document,
        },
    };

    const app = createApp(Report, reportProps);

    // Register WCs as standard Vue components in local mode
    app.component("dpx-code-block", CodeBlock);

    app.mount("#report");
});
