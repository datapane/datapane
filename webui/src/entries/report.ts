import { createApp, use } from "vue";
import Report from "../components/Report.vue";
import "../styles/report.scss";

declare global {
  interface Window {
    dpLocal: boolean;
    reportProps?: any;
  }
}

const mountReport = (reportProps: any) => {
  const app = createApp(Report, { reportProps });
  app.mount("#report");
};

export { mountReport };
