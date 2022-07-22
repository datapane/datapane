import Text from "../components/blocks/Text.vue";
import { makeTemplate } from "./utils";

export default {
    title: "Text",
    component: Text,
};

export const Primary = makeTemplate(Text);

Primary.args = {
    content: `### Hello world!
This is a *markdown* block`,
    isLightProse: false,
};
