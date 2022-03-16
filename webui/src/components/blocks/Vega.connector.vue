<script setup lang="ts">
import { ref, defineAsyncComponent } from "vue";
const VegaBlock = defineAsyncComponent(() => import("./Vega.vue"));

const p = defineProps<{ fetchAssetData: any; responsive: boolean }>();
const plotJson = ref<any>(null);

(async () => {
  plotJson.value = await p.fetchAssetData();
})();
</script>

<template>
  <VegaBlock
    v-if="plotJson"
    :plotJson="plotJson"
    :responsive="p.responsive"
  ></VegaBlock>
</template>
