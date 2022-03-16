<script setup lang="ts">
import { computed, ComputedRef, defineEmits } from "vue";
import { defineCustomElements } from "@revolist/revogrid/custom-element";
import { formatNumber } from "./shared";
import { ExportType } from "../../../data-model/blocks";
import Header from "./Header.vue";
import DPButton from "../../../shared/DPButton.vue";

type Col = {
  prop: string;
  name: string;
  sortable: boolean;
  size: number;
  type?: string;
  columnTemplate?: any;
};

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

const numericCellCompare = (prop: string | number, a: any, b: any) => {
  /* Revogrid 3.0.97 requires an explicit numeric sort function */
  const av = a[prop];
  const bv = b[prop];
  return av === bv ? 0 : av > bv ? 1 : -1;
};

const createHeader = (h: any, column: Col) => {
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

const emit = defineEmits(["load-full"]);

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

defineCustomElements();

const cols: ComputedRef<Col[]> = computed(() => {
  const firstRow = p.data[0];

  if (p.previewMode || !firstRow) {
    return [];
  }
  const colNames =
    p.schema && p.schema.length
      ? p.schema.map((s: any) => s.name)
      : Object.keys(firstRow);

  return colNames.map((n: string) => {
    const optSchemaField = p.schema && p.schema.find((f: any) => f.name === n);

    // schemaType: More granular data type used by the DS header and arrow
    // columnType: One of number/string/date/select used by revogrid
    const schemaType =
      optSchemaField && optSchemaField.type ? optSchemaField.type : "string";
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
      cellCompare: columnType === "number" ? numericCellCompare : undefined,
      columnTemplate: createHeader,
    };
  });
});
</script>

<template>
  <div
    data-cy="block-datatable"
    :class="[
      'rounded shadow w-full',
      { 'h-full flex flex-col': p.singleBlockEmbed },
    ]"
  >
    <Header
      :singleBlockEmbed="p.singleBlockEmbed"
      :previewMode="false"
      :rows="p.data.length"
      :columns="cols.length"
      :cells="p.cells"
      :getCsvText="p.getCsvText"
      :downloadLocal="p.downloadLocal"
      :downloadRemote="p.downloadRemote"
    />
    <revo-grid
      v-if="cols.length && !p.previewMode"
      theme="compact"
      :source="p.data"
      :columns="cols"
      :class="{ 'flex-1': p.singleBlockEmbed, 'h-96': !p.singleBlockEmbed }"
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

<style scoped>
revo-grid {
  background-color: white;
}
</style>
