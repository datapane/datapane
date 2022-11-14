import DateTimeField from "../../components/controls/DateTimeField.vue";
import { makeTemplate } from "../utils";

export default {
    title: "Controls/DateTimeField",
    component: DateTimeField,
};

export const Primary = makeTemplate(DateTimeField);

Primary.args = {
    name: "Date time field",
    type: "datetime-local",
    initial: "2023-01-05T15:27:00",
    label: "Select a date and time",
};
