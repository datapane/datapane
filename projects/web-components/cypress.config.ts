import { defineConfig } from "cypress";

export default defineConfig({
    viewportWidth: 1680,
    viewportHeight: 1050,
    defaultCommandTimeout: 8000,
    includeShadowDom: true,
    video: true,
    env: {
        testEmail: "test@datapane.com",
        testPassword: "",
        staffEmail: "support@datapane.com",
        staffPassword: "",
        styleReportURL: "",
        paramsAppURL: "",
        noParamsAppURL: "",
        fileURL: "",
    },
    e2e: {
        baseUrl: "http://localhost:8090",
    },
});
