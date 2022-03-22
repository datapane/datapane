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
    <plotly-block
        v-if="plotJson"
        :plot-json="plotJson"
        :responsive="p.responsive"
    />
</template>
