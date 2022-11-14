import FileField from "../../components/controls/FileField.vue";
import { makeTemplate } from "../utils";

export default {
    title: "Controls/FileField",
    component: FileField,
};

export const Primary = makeTemplate(FileField);

Primary.args = {
    name: "File field",
    type: "file",
    label: "Select a file",
};
