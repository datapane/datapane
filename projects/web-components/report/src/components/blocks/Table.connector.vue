<script setup lang="ts">
import { ref, inject } from "vue";

const p = defineProps<{ fetchAssetData: any }>();
const singleBlockEmbed = inject("singleBlockEmbed");
const html = ref<string | null>(null);

(async () => {
    html.value = await p.fetchAssetData();
})();
</script>

<template>
    <x-table-block
        v-if="html"
        :html="html"
        :single-block-embed="singleBlockEmbed"
        class="w-full"
    />
</template>
