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
    VegaBlock: defineAsyncComponent(() => import("./Vega.vue")),
  },
};
</script>

<template>
  <VegaBlock
    v-if="plotJson"
    :plotJson="plotJson"
    :responsive="p.responsive"
  ></VegaBlock>
</template>
