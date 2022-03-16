<script setup lang="ts">
import { ref, defineAsyncComponent } from "vue";
const PlotlyBlock = defineAsyncComponent(() => import("./Plotly.vue"));

const p = defineProps<{ fetchAssetData: any; responsive: boolean }>();
const plotJson = ref<any>(null);

(async () => {
  plotJson.value = await p.fetchAssetData();
})();
</script>

<template>
  <PlotlyBlock
    v-if="plotJson"
    :plotJson="plotJson"
    :responsive="p.responsive"
  ></PlotlyBlock>
</template>
