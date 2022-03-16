<script setup lang="ts">
import { ref, defineAsyncComponent } from "vue";
const BokehBlock = defineAsyncComponent(() => import("./Bokeh.vue"));

const p = defineProps<{ fetchAssetData: any; responsive: boolean }>();
const plotJson = ref<any>(null);

(async () => {
  plotJson.value = await p.fetchAssetData();
})();
</script>

<template>
  <BokehBlock
    v-if="plotJson"
    :plotJson="plotJson"
    :responsive="p.responsive"
  ></BokehBlock>
</template>
