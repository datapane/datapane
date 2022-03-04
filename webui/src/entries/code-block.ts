import { defineCustomElement } from "vue";
import CodeBlock from "../components/CodeBlock.ce.vue";

customElements.define("dp-code-block", defineCustomElement(CodeBlock));

export { CodeBlock };
