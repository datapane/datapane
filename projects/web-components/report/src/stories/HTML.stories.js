import HTML from "../components/blocks/HTML.vue";
import { makeTemplate } from "./utils";

export default {
    title: "HTML",
    component: HTML,
};

export const Primary = makeTemplate(HTML);

Primary.args = {
    html: "<h3>Hello world!</h3>",
};
