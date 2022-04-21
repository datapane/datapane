import { createApp, defineCustomElement } from "vue";
import Report from "./src/components/Report.vue";
import TableBlock from "./src/components/blocks/Table.ce.vue";
import "./src/styles/report.scss";
import "highlight.js/styles/stackoverflow-light.css";

customElements.define("x-table-block", defineCustomElement(TableBlock));

declare global {
    interface Window {
        dpLocal: boolean;
        reportProps?: any;
        posthog: any;
        hasPosthog: any;
        dpAuthorId: string;
        dpReportId: string;
        dpLocalViewEvent: any;
    }
}

const mountReport = (reportProps: any) => {
    const app = createApp(Report, reportProps);
    app.mount("#report");
    return app;
};

export { mountReport };
