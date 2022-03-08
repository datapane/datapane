// TODO - import tailwind as own entry?
import "../styles/tailwind.css";
import { createApp } from "vue";
import Report from "../components/Report.vue";

declare global {
  interface Window {
    dpLocal: boolean;
  }
}

const mountReport = (reportProps: any) => {
  const app = createApp(Report, { reportProps });
  app.mount("#report");
};

export { mountReport };
