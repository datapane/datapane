import Media from "../components/blocks/Media.vue";
import { makeTemplate } from "./utils";
import dpLogo from "./assets/dplogo.b64?raw";

export default {
    title: "Media",
    component: Media,
};

export const Primary = makeTemplate(Media);

Primary.args = {
    src: `data:image/png;base64,${dpLogo}`,
    type: "image/png",
};
