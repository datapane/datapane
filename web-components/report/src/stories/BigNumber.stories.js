import BigNumber from "../components/blocks/BigNumber.vue";
import { makeTemplate } from "./utils";

export default {
    title: "BigNumber",
    component: BigNumber,
};

export const Primary = makeTemplate(BigNumber);

Primary.args = {
    heading: "Foo",
    value: "100%",
    isPositiveIntent: true,
    isUpwardChange: true,
    prevValue: "98%",
    change: "2%",
};
