import Code from "../components/blocks/Code.ce.vue";
import { makeTemplate } from "./utils";

export default {
    title: "Code",
    component: Code,
};

export const Primary = makeTemplate(Code);

Primary.args = {
    language: "Python",
    code: `def hello_world():
    print("Hello, world!")`,
};
