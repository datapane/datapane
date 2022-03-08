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
    BokehBlock: defineAsyncComponent(() => import("../blocks/Bokeh.vue")),
  },
};
</script>

<template>
  <BokehBlock
    v-if="plotJson"
    :plotJson="plotJson"
    :responsive="p.responsive"
  ></BokehBlock>
</template>
