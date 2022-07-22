import Formula from "../components/blocks/Formula.vue";
import { makeTemplate } from "./utils";

export default {
    title: "Formula",
    component: Formula,
};

export const Primary = makeTemplate(Formula);

Primary.args = {
    content: "\\int\\varphi = \\sum_{i=1}^{N}(a_i\\;\\mu(E_i))",
};
