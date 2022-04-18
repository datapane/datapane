import { defineCustomElement } from "vue";
import CodeBlock from "../components/blocks/Code.ce.vue";

customElements.define("dpx-code-block", defineCustomElement(CodeBlock));

export { CodeBlock };
