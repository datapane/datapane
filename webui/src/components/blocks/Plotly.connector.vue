<script setup lang="ts">
import { ref, defineAsyncComponent } from "vue";

const p = defineProps<{ fetchAssetData: any; responsive: boolean }>();
const plotJson = ref<any>(null);

(async () => {
  plotJson.value = await p.fetchAssetData();
})();
</script>

<script lang="ts">
export default {
  components: {
    PlotlyBlock: defineAsyncComponent(() => import("./Plotly.vue")),
  },
};
</script>

<template>
  <PlotlyBlock
    v-if="plotJson"
    :plotJson="plotJson"
    :responsive="p.responsive"
  ></PlotlyBlock>
</template>
