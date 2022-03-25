import { createApp } from "vue";
import Report from "../components/Report.vue";
import CodeBlock from "../components/blocks/Code.ce.vue";
import he from "he";
import "../styles/report.scss";
import "../styles/tailwind.css";

window.addEventListener("DOMContentLoaded", () => {
    const windowProps = window.reportProps;
    const reportProps = {
        ...windowProps,
        htmlHeader: he.decode(windowProps.htmlHeader),
        report: {
            ...windowProps.report,
            document: he.decode(windowProps.report.document),
        },
    };

    const app = createApp(Report, { reportProps });

    // Register WCs as standard Vue components in local mode
    app.component("dp-code-block", CodeBlock);

    app.mount("#report");
});
