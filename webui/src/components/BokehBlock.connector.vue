<script setup lang="ts">
import { ref, reactive, defineAsyncComponent } from "vue";

const p = defineProps<{ fetchAssetData: any }>();
const childProps = reactive({ plotJson: null });

p.fetchAssetData().then((plotJson: any) => {
  childProps.plotJson = plotJson;
});
</script>

<script lang="ts">
export default {
  components: {
    BokehBlock: defineAsyncComponent(() => import("./BokehBlock.vue")),
  },
};
</script>

<template>
  <BokehBlock v-bind="childProps"></BokehBlock>
</template>
