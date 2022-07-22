import Plotapi from "../components/blocks/Plotapi.vue";
import { makeTemplate } from "./utils";
import iframeContent from "./assets/plotapi.html?raw";

export default {
    title: "Plotapi",
    component: Plotapi,
};

export const Primary = makeTemplate(Plotapi);

Primary.args = {
    iframeContent,
    singleBlockEmbed: false,
};
