<script setup lang="ts">
import { ref, inject } from "vue";
import Plotapi from "./Plotapi.vue";

const p = defineProps<{ fetchAssetData: any }>();
const singleBlockEmbed: boolean | undefined = inject("singleBlockEmbed");
const iframeContent = ref<string | null>(null);

(async () => {
    iframeContent.value = await p.fetchAssetData();
})();
</script>

<template>
    <plotapi
        v-if="iframeContent"
        :iframe-content="iframeContent"
        :single-block-embed="!!singleBlockEmbed"
    />
</template>
