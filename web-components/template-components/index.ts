import { defineAsyncComponent, defineCustomElement } from "vue";
import { toggleVisibility, onLoad } from "./src/template-utils";

const Modal = defineAsyncComponent(() => import("./src/Modal.ce.vue"));
const CopyField = defineAsyncComponent(() => import("./src/CopyField.ce.vue"));
const CodeCopyField = defineAsyncComponent(
    () => import("./src/CodeCopyField.ce.vue"),
);
const GettingStarted = defineAsyncComponent(
    () => import("./src/GettingStarted.ce.vue"),
);
const SearchQuery = defineAsyncComponent(
    () => import("./src/SearchQuery.ce.vue"),
);

customElements.define(
    "dp-getting-started",
    defineCustomElement(GettingStarted),
);
customElements.define("dp-modal", defineCustomElement(Modal));
customElements.define("dp-copy-field", defineCustomElement(CopyField));
customElements.define("dp-code-copy-field", defineCustomElement(CodeCopyField));
customElements.define("dp-search-query", defineCustomElement(SearchQuery));

const templateUtils = {
    toggleVisibility,
    onLoad,
};

export { templateUtils };
