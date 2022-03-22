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
    <vega-block
        v-if="plotJson"
        :plot-json="plotJson"
        :responsive="p.responsive"
    ></vega-block>
</template>
