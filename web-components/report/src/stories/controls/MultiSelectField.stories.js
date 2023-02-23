import MultiChoiceField from "../../components/controls/MultiChoiceField.vue";
import { makeTemplate } from "../utils";

export default {
    title: "Controls/MultiChoiceField",
    component: MultiChoiceField,
};

export const Primary = makeTemplate(MultiChoiceField);

Primary.args = {
    name: "Multi select field",
    label: "Multi select field",
    options: ["foo", "bar", "boo", "far"],
    initial: ["foo"],
};
