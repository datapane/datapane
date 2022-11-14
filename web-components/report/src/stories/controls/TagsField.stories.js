import TagsField from "../../components/controls/TagsField.vue";
import { makeTemplate } from "../utils";

export default {
    title: "Controls/TagsField",
    component: TagsField,
};

export const Primary = makeTemplate(TagsField);

Primary.args = {
    name: "Tags field",
    initial: ["foo", "bar"],
};
