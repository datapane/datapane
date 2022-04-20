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
    <bokeh-block
        v-if="plotJson"
        :plot-json="plotJson"
        :responsive="p.responsive"
    ></bokeh-block>
</template>
