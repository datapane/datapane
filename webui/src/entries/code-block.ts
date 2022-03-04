import { defineCustomElement } from "vue";
import CodeBlock from "../components/blocks/Code.ce.vue";

customElements.define("dp-code-block", defineCustomElement(CodeBlock));

export { CodeBlock };
