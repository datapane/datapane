<script setup lang="ts">
import { ref } from "vue";

const p = defineProps<{ fetchAssetData: any; responsive: boolean }>();
const plotSrc = ref<string | null>(null);

(async () => {
  plotSrc.value = await p.fetchAssetData();
})();
</script>

<script lang="ts">
import SVGBlock from "./SVG.vue";

export default {
  components: {
    SVGBlock,
  },
};
</script>

<template>
  <SVGBlock v-if="plotSrc" :src="plotSrc" :responsive="p.responsive" />
</template>
