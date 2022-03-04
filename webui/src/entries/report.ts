// TODO - import tailwind as own entry?
import "../styles/tailwind.css";
import { createApp } from "vue";
import Report from "../components/Report.vue";

const mountReport = (report: any) => {
  const app = createApp(Report, { report });
  app.mount("#report");
};

export { mountReport };
