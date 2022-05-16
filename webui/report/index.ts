import { createApp, defineCustomElement } from "vue";
import Report from "./src/components/Report.vue";
import TableBlock from "./src/components/blocks/Table.ce.vue";
import "./src/styles/report.scss";
import "highlight.js/styles/stackoverflow-light.css";

customElements.define("x-table-block", defineCustomElement(TableBlock));

const parseElementProps = (elId: string): any => {
    const propsEl = document.getElementById(elId);
    if (!propsEl || !propsEl.textContent) {
        throw "Couldn't find props JSON element";
    }
    return JSON.parse(propsEl.textContent);
};

const mountReport = (reportProps: any) => {
    const app = createApp(Report, reportProps);
    app.mount("#report");
    return app;
};

export { mountReport, parseElementProps };
