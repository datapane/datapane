import { createApp, use } from "vue";
import Report from "../components/Report.vue";
import he from "he";
import "../styles/report.scss";
import "../styles/tailwind.css";
import "./code-block";

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
  console.log(reportProps);
  const app = createApp(Report, { reportProps });
  app.mount("#report");
});