import RangeField from "../../components/controls/RangeField.vue";
import { makeTemplate } from "../utils";

export default {
    title: "Controls/RangeField",
    component: RangeField,
};

export const Primary = makeTemplate(RangeField);

Primary.args = {
    name: "Range field",
    min: 0,
    max: 10,
    step: 1,
    initial: 3,
};
