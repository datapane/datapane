import SVG from "../components/blocks/SVG.vue";
import { makeTemplate } from "./utils";
import svgData from "./assets/svg.b64?raw";

export default {
    title: "SVG",
    component: SVG,
};

export const Primary = makeTemplate(SVG);

Primary.args = {
    src: `data:image/svg+xml;base64,${svgData}`,
    responsive: true,
};
