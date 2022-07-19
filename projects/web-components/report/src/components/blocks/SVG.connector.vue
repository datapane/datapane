<script setup lang="ts">
import { ref } from "vue";
import SvgBlock from "./SVG.vue";

const p = defineProps<{ fetchAssetData: any; responsive: boolean }>();
const plotSrc = ref<string | null>(null);

(async () => {
    plotSrc.value = await p.fetchAssetData();
})();
</script>

<template>
    <svg-block v-if="plotSrc" :src="plotSrc" :responsive="p.responsive" />
</template>
