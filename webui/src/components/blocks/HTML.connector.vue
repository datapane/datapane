<script setup lang="ts">
import { ref } from "vue";

const p = defineProps<{ fetchAssetData: any }>();
const html = ref<string | null>(null);

(async () => {
  html.value = await p.fetchAssetData();
})();
</script>

<template>
  <HTMLBlock v-if="html" :html="html" class="w-full" />
</template>

<script lang="ts">
import HTMLBlock from "./HTML.vue";

export default {
  components: {
    HTMLBlock,
  },
};
</script>
