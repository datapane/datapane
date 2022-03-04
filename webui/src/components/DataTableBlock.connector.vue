<script setup lang="ts">
import { ref, reactive, defineAsyncComponent } from "vue";

// const p = defineProps<{ fetchAssetData: any }>();
const childProps = reactive({});

// p.fetchAssetData().then(plotJson => {
//     childProps.plotJson = plotJson;
// })
</script>

<script lang="ts">
export default {
  components: {
    DataTableBlock: defineAsyncComponent(() => import("./DataTableBlock.vue")),
  },
};
</script>

<template>
  <DataTableBlock v-bind="childProps"></DataTableBlock>
</template>

<style scoped></style>
