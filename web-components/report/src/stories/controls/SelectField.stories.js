import SelectField from "../../components/controls/SelectField.vue";
import { makeTemplate } from "../utils";

export default {
    title: "Controls/SelectField",
    component: SelectField,
};

export const Primary = makeTemplate(SelectField);

Primary.args = {
    name: "Select field",
    options: ["foo", "bar", "boo", "far"],
    initial: "foo",
};
