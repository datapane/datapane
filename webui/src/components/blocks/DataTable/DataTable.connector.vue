<script setup lang="ts">
import { defineAsyncComponent, inject, onMounted, ref, watch } from "vue";
import { DatasetResponse } from "../../../data-model/datatable/datatable-block";

const p = defineProps<{
  streamContents: () => Promise<DatasetResponse>;
  autoLoad: boolean;
}>();

const singleBlockEmbed = inject("singleBlockEmbed");

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

getResultData();
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
    :schema="dsSchema"
    :previewMode="false"
  />
</template>
