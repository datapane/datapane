import Table from "../components/blocks/Table.ce.vue";
import { defineCustomElement } from "vue";
import tableHtml from "./assets/table.html?raw";

const TableCE = defineCustomElement(Table);
customElements.define("x-table-block", TableCE);

export default {
    title: "Table",
    component: Table,
};

export const Primary = (args) => ({
    components: { Table },
    setup() {
        return { args };
    },
    template:
        "<x-table-block :html='args.html' :single-block-embed='args.singleBlockEmbed' :class='args.class'/>",
});

Primary.args = {
    singleBlockEmbed: "false",
    class: "w-full",
    html: tableHtml,
};
