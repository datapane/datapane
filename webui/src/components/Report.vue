<script setup lang="ts">
import { ReportStore } from "../data-model/report-store";
// import GridGenerator from "./GridGenerator.vue";

const p = defineProps<{ reportProps: any }>();
const store = new ReportStore(p.reportProps);
const multiBlockEmbed =
  p.reportProps.mode === "EMBED" && !store.state.singleBlockEmbed;
</script>

<script lang="ts">
// export default {
//   components: {
//     GridGenerator,
//   }
// }
</script>

<template>
  <div class="max-w-full h-full bg-dp-background" data-cy="report-component">
    <!-- TODO - custom header -->
    <div
      :class="{
        'flex flex-col justify-end bg-dp-background': true,
        'pb-10': p.reportProps.isOrg && multiBlockEmbed,
        'pb-6': !p.reportProps.isOrg && multiBlockEmbed,
      }"
    >
      {{ JSON.stringify(store.state.report) }}
    </div>
  </div>
</template>
