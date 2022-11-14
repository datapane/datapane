import Interactive from "../../components/controls/Interactive.vue";
import * as b from "../../data-model/blocks/index";
import { makeTemplate } from "../utils";
import he from "he";
import { MultiChoiceField } from "../../data-model/blocks/index";

export default {
    title: "Controls/Interactive",
    component: Interactive,
};

export const Primary = makeTemplate(Interactive);

Primary.args = {
    label: "Interactive block",
    subtitle: "Interactive subtitle",
    update: () => null,
    onChange: () => null,
    prompt: "Custom prompt",
    functionId: "abc",
    trigger: "submit",
    children: [
        new b.TemporalField(
            {
                attributes: {
                    initial: "2023-01-05T15:27:00",
                    name: "Date time field",
                },
                type: "element",
                name: "DateTime",
            },
            {},
            { timeFormat: "YYYY-MM-DDTHH:mm:ss", type: "datetime-local" },
        ),
        new b.FileField(
            {
                attributes: { name: "File field" },
                type: "element",
                name: "File",
            },
            {},
        ),
        new b.InputField(
            {
                attributes: { name: "Input field" },
                type: "element",
                name: "Input",
            },
            {},
        ),
        new b.MultiChoiceField(
            {
                attributes: {
                    name: "Multi select field",
                    choices: JSON.stringify(["foo", "bar", "boo", "far"]),
                    initial: JSON.stringify(["foo"]),
                },
                type: "element",
                name: "MultiSelect",
            },
            {},
        ),
        new b.RangeField(
            {
                attributes: {
                    name: "Range field",
                    min: 0,
                    max: 10,
                    initial: 3,
                    step: 1,
                },
                type: "element",
                name: "Range",
            },
            {},
        ),
        new b.SelectField(
            {
                attributes: {
                    name: "Select field",
                    choices: JSON.stringify(["foo", "bar", "boo", "far"]),
                    initial: "foo",
                },
                type: "element",
                name: "Select",
            },
            {},
        ),
        new b.SwitchField(
            {
                attributes: { name: "Switch field", initial: false },
                type: "element",
                name: "Switch",
            },
            {},
        ),
        new b.TagsField(
            {
                attributes: {
                    name: "Tags field",
                    choices: JSON.stringify(["foo", "bar", "boo", "far"]),
                    initial: JSON.stringify(["foo"]),
                },
                type: "element",
                name: "Tags",
            },
            {},
        ),
    ],
};
