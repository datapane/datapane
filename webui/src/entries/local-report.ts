import { createApp, defineCustomElement } from "vue";
import Report from "../components/Report.vue";
import CodeBlock from "../components/blocks/Code.ce.vue";
import TableBlock from "../components/blocks/Table.ce.vue";
import "../styles/report.scss";
import "../styles/tailwind.css";
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

    const app = createApp(Report, { reportProps });

    // Register WCs as standard Vue components in local mode
    app.component("dp-code-block", CodeBlock);

    app.mount("#report");
});
