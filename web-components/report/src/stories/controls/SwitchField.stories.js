import SwitchField from "../../components/controls/SwitchField.vue";
import { makeTemplate } from "../utils";

export default {
    title: "Controls/SwitchField",
    component: SwitchField,
};

export const Primary = makeTemplate(SwitchField);

Primary.args = {
    name: "Switch field",
    initial: false,
};
