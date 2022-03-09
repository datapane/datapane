<script setup lang="ts">
import { defineAsyncComponent, inject, ref } from "vue";
import { DatasetResponse } from "../../../data-model/datatable/datatable-block";

const p = defineProps<{
  streamContents: () => Promise<DatasetResponse>;
  deferLoad: boolean;
  cells: number;
}>();

const singleBlockEmbed = inject("singleBlockEmbed");
const previewMode = ref(p.deferLoad);
const dsData = ref([]);
const dsSchema = ref({});

const getResultData = async () => {
  try {
    const successfulDownload: any = await p.streamContents();
    if (successfulDownload) {
      const { schema, data, containsBigInt } = successfulDownload;
      dsData.value = dsData.value.concat(data);
      dsSchema.value = schema;
    }
  } catch (e) {
    console.error("An error occurred downloading your dataset data: " + e);
  }
};

if (!p.deferLoad) {
  getResultData();
}

const handleLoadFull = async () => {
  await getResultData();
  if (dsData.value.length) {
    previewMode.value = false;
  }
};
</script>

<script lang="ts">
export default {
  components: {
    DataTableBlock: defineAsyncComponent(() => import("./DataTable.vue")),
  },
};
</script>

<template>
  <DataTableBlock
    :singleBlockEmbed="singleBlockEmbed"
    :data="dsData"
    :cells="p.cells"
    :schema="dsSchema"
    :previewMode="previewMode"
    @load-full="handleLoadFull"
  />
</template>
