import * as React from "react";
import { updateEditorAtCursor } from "../utils";
import { DPDropdown } from "../../../legacy-report/DPDropdown";

const LayoutBlocks = ["Page", "Group", "Select"];
const DisplayBlocks = ["Big Number", "Code", "Formula", "Text"];
const EmbedBlocks = ["Embed", "HTML"];
const DynamicBlocks = ["Empty"];

type BlockButton = {
    val: any;
    tooltip: string;
};

const blockButtons: BlockButton[] = [
    {
        val: `<Page label="My page">
  <Text>[[
;Hello world!
  ]]</Text>
</Page>
`,
        tooltip: "Page",
    },
    {
        val: `<Group columns="1">
  <Text>[[
;Hello world!
  ]]</Text>
  <Formula>
    [[x^2 + y^2 = z^2]]
  </Formula>
</Group>`,
        tooltip: "Group",
    },
    {
        val: `<Select>
  <Text>[[
;Hello world!
  ]]</Text>
  <Formula>[[x^2 + y^2 = z^2]]</Formula>
</Select>`,
        tooltip: "Select",
    },
    {
        /* eslint-disable-next-line quotes */
        val: '<BigNumber heading="Users" value="34" prev_value="30"/>',
        tooltip: "Big Number",
    },
    {
        val: `<Code language="Python">[[
;def sqrt(num):
;  return num ** 0.5
]]</Code>`,
        tooltip: "Code",
    },
    {
        /* eslint-disable-next-line quotes */
        val: '<Embed url="https://www.youtube.com/watch?v=JDe14ulcfLA"/>',
        tooltip: "Embed",
    },
    {
        val: "<Formula>[[x^2 + y^2 = z^2]]</Formula>",
        tooltip: "Formula",
    },
    {
        val: `<HTML>[[
;<i>Hello</i>
]]</HTML>`,
        tooltip: "HTML",
    },
    {
        val: `<Text>[[
;Hello world!
]]</Text>`,
        tooltip: "Text",
    },
    {
        /* eslint-disable-next-line quotes */
        val: '<Empty name="empty-block"/>',
        tooltip: "Empty",
    },
];

export const NewBlocksIcons = () => {
    /**
     * Datapane blocks that are added to the editor on click
     */

    const generateBlockView = (filter: string[]) =>
        blockButtons
            .filter((b) => filter.includes(b.tooltip))
            .map((b) => ({
                name: b.tooltip,
                id: b.tooltip,
                onClick: () => updateEditorAtCursor(b.val),
            }));

    return (
        <DPDropdown
            name={"Insert Blocks"}
            orientation={"left"}
            sections={[
                {
                    title: "Layout",
                    options: generateBlockView(LayoutBlocks),
                },
                {
                    title: "Display",
                    options: generateBlockView(DisplayBlocks),
                },
                {
                    title: "Embed",
                    options: generateBlockView(EmbedBlocks),
                },
                {
                    title: "Dynamic",
                    options: generateBlockView(DynamicBlocks),
                },
            ]}
        />
    );
};
