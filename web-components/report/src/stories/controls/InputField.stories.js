import InputField from "../../components/controls/InputField.vue";
import { makeTemplate } from "../utils";

export default {
    title: "Controls/InputField",
    component: InputField,
};

export const Primary = makeTemplate(InputField);

Primary.args = {
    name: "Input field",
    label: "Input some text",
};
