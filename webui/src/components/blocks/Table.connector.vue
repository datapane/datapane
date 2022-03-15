<script setup lang="ts">
import { ref, inject } from "vue";

const p = defineProps<{ fetchAssetData: any }>();
const html = ref<string | null>(null);

const singleBlockEmbed = inject("singleBlockEmbed");

(async () => {
  html.value = await p.fetchAssetData();
})();
</script>

<template>
  <x-table-block
    v-if="html"
    :html="html"
    :singleBlockEmbed="singleBlockEmbed"
    class="w-full"
  ></x-table-block>
</template>
