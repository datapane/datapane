import { createApp, defineCustomElement } from "vue";
import Report from "./src/components/ReportComponent.vue";
import TableBlock from "./src/components/blocks/Table.ce.vue";
import "./src/styles/report.scss";
import "../base/src/styles/tailwind.css";
import "highlight.js/styles/stackoverflow-light.css";
import "codemirror/lib/codemirror.css";
import "codemirror/theme/eclipse.css";

customElements.define("x-table-block", defineCustomElement(TableBlock));

window.addEventListener("DOMContentLoaded", () => {
    const { reportProps } = window;
    const app = createApp(Report, reportProps);
    app.mount("#report");
});
