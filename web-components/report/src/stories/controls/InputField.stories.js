import TextBox from "../../components/controls/TextBox.vue";
import { makeTemplate } from "../utils";

export default {
    title: "Controls/TextBox",
    component: TextBox,
};

export const Primary = makeTemplate(TextBox);

Primary.args = {
    name: "Input field",
    label: "Input some text",
};
