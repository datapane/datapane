<script setup lang="ts">
import { ReportStore } from "../data-model/report-store";
import { ref, provide } from "vue";
import GridGenerator from "./GridGenerator.vue";
import { createGridKey } from "./utils";

const p = defineProps<{ reportProps: any }>();
const store = new ReportStore(p.reportProps);
const pageNumber = ref(0);

const multiBlockEmbed =
  p.reportProps.mode === "EMBED" && !store.state.singleBlockEmbed;

// TODO - computed?
const rootGroup = store.state.report
  ? store.state.report.children[pageNumber.value].children[0]
  : undefined;

provide("singleBlockEmbed", store.state.singleBlockEmbed);
</script>

<script lang="ts">
export default {
  components: {
    GridGenerator,
  },
};
</script>

<template>
  <div class="max-w-full h-full bg-dp-background" data-cy="report-component">
    <!-- TODO - custom header; custom width; pages -->
    <div
      :class="{
        'flex flex-col justify-end bg-dp-background': true,
        'pb-10': p.reportProps.isOrg && multiBlockEmbed,
        'pb-6': !p.reportProps.isOrg && multiBlockEmbed,
      }"
    >
      <div class="flex-1 flex flex-col">
        <div
          :class="{ 'flex-grow': true, 'px-4': !store.state.singleBlockEmbed }"
        >
          <GridGenerator
            :key="createGridKey(rootGroup, 0)"
            :tree="rootGroup"
          ></GridGenerator>
        </div>
      </div>
    </div>
  </div>
</template>
