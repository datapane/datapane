<script lang="ts">
type Col = {
    prop: string;
    name: string;
    sortable: boolean;
    size: number;
    type?: string;
    columnTemplate?: any;
};

type QueryResult =
    | {
          data: any[];
          schema: { name: string; type: string }[];
      }
    | undefined
    | null;

type KnownTypes =
    | "string"
    | "double"
    | "boolean"
    | "integer"
    | "timestamp"
    | "category"
    | "index"
    | "unknown";

const TableColors: { [t in KnownTypes]: string } = {
    string: "green",
    double: "blue",
    boolean: "indigo",
    timestamp: "red",
    category: "orange",
    integer: "teal",
    index: "black",
    unknown: "black",
};

const TableIcons: { [t in KnownTypes]: string } = {
    string: "font",
    timestamp: "calendar",
    category: "cubes",
    double: "bar-chart",
    boolean: "toggle-on",
    integer: "bar-chart",
    index: "list-ol",
    unknown: "circle",
};

const DEFAULT_QUERY = "SELECT * FROM $table";
const SCHEMA_SEARCH_LIMIT = 10;
const DISTINCT_CATEGORIES_LIMIT = 8; // TODO - what is the real categories limit?
</script>

<script setup lang="ts">
import { computed, ref, ComputedRef } from "vue";
import { defineCustomElements } from "@revolist/revogrid/custom-element";
import { formatNumber } from "./shared";
import { ExportType } from "../../../data-model/blocks";
import TableHeader from "./Header.vue";
import DPButton from "../../../shared/DPButton.vue";
import QueryArea from "./QueryArea.vue";
import alasql from "alasql";

const p = defineProps<{
    singleBlockEmbed: boolean;
    data: any[];
    cells: number;
    schema: any;
    previewMode: boolean;
    refId: string;
    getCsvText: () => Promise<string>;
    downloadLocal: (type: ExportType) => Promise<void>;
    downloadRemote: (type: ExportType) => Promise<void>;
}>();

const emit = defineEmits(["load-full"]);
const query = ref<string>(DEFAULT_QUERY);
const queryResult = ref<QueryResult>();
const queryOpen = ref(false);
const queryErrors = ref<any>();

const schema = computed(() => queryResult.value?.schema ?? p.schema);
const data = computed(() => queryResult.value?.data ?? p.data);

defineCustomElements();

const numericCellCompare = (prop: string | number, a: any, b: any) => {
    /**
     * Revogrid 3.0.97 requires an explicit numeric sort function
     **/
    const av = a[prop];
    const bv = b[prop];
    return av === bv ? 0 : av > bv ? 1 : -1;
};

const createHeader = (h: any, column: Col) => {
    /**
     * generate a custom hyperscript header based on column data type
     */
    const columnType: any = column.type || "unknown";
    const iconName = (TableIcons as any)[columnType];
    const colorName = (TableColors as any)[columnType];

    return h(
        "div",
        {
            class: "flex items-center w-full whitespace-nowrap overflow-hidden",
        },
        h("i", {
            class: `fa fa-${iconName} pr-2 text-${colorName}-400`,
        }),
        h("div", {}, column.name)
    );
};

const getColumnType = (columnType?: string) => {
    /**
     * convert arrow column type to revogrid column type
     */
    switch (columnType) {
        case "double":
        case "integer":
            return "number";
        case "timestamp":
            return "date";
        case "category":
            return "select";
        default:
            return "string";
    }
};

const cols: ComputedRef<Col[]> = computed(() => {
    /**
     * generate revogrid Col array based on the dataset's schema
     */
    const firstRow = p.data[0];

    if (p.previewMode || !firstRow) {
        return [];
    }

    // Use the schema to get column names, otherwise use first row as a fallback
    const colNames =
        schema.value && schema.value.length
            ? schema.value.map((s: any) => s.name)
            : Object.keys(firstRow);

    return colNames.map((n: string) => {
        const schemaField =
            schema.value && schema.value.find((f: any) => f.name === n);

        // schemaType: More granular data type used by the DS header and arrow
        // columnType: One of number/string/date/select used by revogrid
        const schemaType =
            schemaField && schemaField.type ? schemaField.type : "string";
        const columnType = getColumnType(schemaType);

        return {
            prop: n,
            name: n,
            size: 200,
            sortable: true,
            columnType,
            type: schemaType,
            filter: columnType,
            autoSize: true,
            cellCompare:
                columnType === "number" ? numericCellCompare : undefined,
            columnTemplate: createHeader,
        };
    });
});

const runQuery = () => {
    /**
     * Run alasql query on the dataset and set the query result
     */

    const guessQueryColumnType = (col: string, queryData: any[]) => {
        /**
         * Guess the column type based on the given value
         * TODO - timestamp validation is complex so we interpret them as strings for now
         */

        const guessValueType = (v: any): string => {
            if (Number(v) === v && `${v}`.includes(".")) {
                return "double";
            } else if (Number(v) === v) {
                return "integer";
            } else if (Boolean(v) === v) {
                return "boolean";
            } else {
                return "string";
            }
        };

        const rowLimit = Math.min(SCHEMA_SEARCH_LIMIT, p.data.length - 1);
        const firstNRows: any[] = queryData
            .slice(0, rowLimit)
            .map((r) => r[col]);
        const rowTypes: string[] = firstNRows.map(guessValueType);

        const isAllTypesEqual = rowTypes.every(
            (rowType) => rowType === rowTypes[0]
        );

        if (isAllTypesEqual && rowTypes[0] !== "string") {
            // If all row types are equal and non-string then return the row type
            return rowTypes[0];
        } else if (
            [...new Set(firstNRows)].length <= DISTINCT_CATEGORIES_LIMIT
        ) {
            // Otherwise, return `category` if there are few distinct values
            return "category";
        } else {
            return "string";
        }
    };

    const buildSchema = (queryData: any[]) => {
        /**
         * Generate new schema entries based on data types generated by the query
         */
        const columns = Object.keys(queryData[0]);
        return columns.map((col) => ({
            name: col,
            type: guessQueryColumnType(col, queryData),
        }));
    };

    queryErrors.value = null;

    try {
        const alasqlQuery = query.value?.replace(/\$table/g, "?");
        const queryData = alasql(alasqlQuery, [p.data]);
        const querySchema = queryData.length ? buildSchema(queryData) : [];
        queryResult.value = { data: queryData, schema: querySchema };
    } catch (e) {
        queryErrors.value = e;
    }
};

const onQueryChange = (newQuery: string) => {
    query.value = newQuery;
};

const clearQuery = () => {
    queryResult.value = null;
    queryErrors.value = null;
};
</script>

<template>
    <div
        data-cy="block-datatable"
        :class="[
            'rounded shadow w-full',
            { 'h-full flex flex-col': p.singleBlockEmbed },
        ]"
    >
        <table-header
            :single-block-embed="p.singleBlockEmbed"
            :preview-mode="p.previewMode"
            :query-open="queryOpen"
            :rows="p.data.length"
            :columns="cols.length"
            :cells="p.cells"
            :get-csv-text="p.getCsvText"
            :download-local="p.downloadLocal"
            :download-remote="p.downloadRemote"
            @toggle-query-open="queryOpen = !queryOpen"
        />
        <query-area
            v-if="queryOpen"
            :errors="queryErrors"
            :initialQuery="query"
            @query-change="onQueryChange"
            @run-query="runQuery"
            @clear-query="clearQuery"
        />
        <revo-grid
            v-if="cols.length && !p.previewMode"
            theme="compact"
            :source="data"
            :columns="cols"
            :class="{
                'flex-1': p.singleBlockEmbed,
                'h-96': !p.singleBlockEmbed,
            }"
            :resize="true"
            :autoSizeColumn="true"
            :rowHeaders="true"
            :filter="true"
            :readonly="true"
            :exporting="true"
            :id="`grid-${p.refId}`"
        />
        <div v-if="p.previewMode" class="w-full flex justify-center">
            <DPButton
                dataCy="button-load-dataset"
                @click="emit('load-full')"
                icon="fa fa-table"
            >
                Click to load dataset ({{ formatNumber(p.cells) }} cells)
            </DPButton>
        </div>
    </div>
</template>

<style>
revo-grid {
    background-color: white;
}
</style>
