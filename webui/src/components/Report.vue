<script setup lang="ts">
import { ReportStore } from "../data-model/report-store";
import { ref, provide, computed } from "vue";
import GridGenerator from "./GridGenerator.vue";
import { createGridKey } from "./utils";
import { ReportWidth } from "../data-model/blocks";

const p = defineProps<{ reportProps: any }>();
const store = new ReportStore(p.reportProps);
const { report, singleBlockEmbed } = store.state;
const pageNumber = ref(0);

const multiBlockEmbed =
  p.reportProps.mode === "EMBED" && !store.state.singleBlockEmbed;

const isNarrowWidth = (w: ReportWidth) => !singleBlockEmbed && w === "narrow";
const isMediumWidth = (w: ReportWidth) => !singleBlockEmbed && w === "medium";
const isFullWidth = (w: ReportWidth) => !singleBlockEmbed && w === "full";

const rootGroup = computed(() =>
  report ? report.children[pageNumber.value].children[0] : undefined
);

provide("singleBlockEmbed", singleBlockEmbed);
</script>

<script lang="ts">
export default {
  components: {
    GridGenerator,
  },
};
</script>

<template>
  <div
    :class="[
      'w-full bg-dp-background',
      {
        'max-w-3xl': isNarrowWidth(report.width),
        'max-w-screen-xl': isMediumWidth(report.width),
        'max-w-full': isFullWidth(report.width),
      },
    ]"
    data-cy="report-component"
  >
    <!-- TODO - custom header; custom width; pages -->
    <div
      :class="{
        'flex flex-col justify-end bg-dp-background': true,
        'pb-10': p.reportProps.isOrg && multiBlockEmbed,
        'pb-6': !p.reportProps.isOrg && multiBlockEmbed,
      }"
    >
      <div class="flex-1 flex flex-col">
        <div :class="['flex-grow', { 'px-4': !singleBlockEmbed }]">
          <GridGenerator
            :key="createGridKey(rootGroup, 0)"
            :tree="rootGroup"
          ></GridGenerator>
        </div>
      </div>
    </div>
  </div>
</template>
