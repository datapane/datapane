<script setup lang="ts">
import { ReportStore } from "../data-model/report-store";
import { ref, provide, computed } from "vue";
import { createGridKey } from "./utils";
import { ReportWidth } from "../data-model/blocks";

const p = defineProps<{ reportProps: any }>();
const store = new ReportStore(p.reportProps);
const { report, singleBlockEmbed } = store.state;
const pageNumber = ref(0);

const multiBlockEmbed =
  p.reportProps.mode === "EMBED" && !store.state.singleBlockEmbed;

const rootGroup = computed(() =>
  report ? report.children[pageNumber.value].children[0] : undefined
);

provide("singleBlockEmbed", singleBlockEmbed);

const getPageLabel = (
  label: string | undefined,
  pageNumber: number
): string => {
  return label || `Page ${pageNumber}`;
};

const pageLabels = report.children.map((page, idx) =>
  getPageLabel(page.label, idx + 1)
);

const handlePageChange = (newPageNumber: number) =>
  (pageNumber.value = newPageNumber);
</script>

<script lang="ts">
import GridGenerator from "./GridGenerator.vue";
import HPages from "./HPages.vue";

export default {
  components: {
    GridGenerator,
    HPages,
  },
};
</script>

<template>
  <div
    v-if="pageLabels.length > 1 && report.layout === 'top'"
    class="hidden sm:block w-full mb-6"
  >
    <HPages
      :labels="pageLabels"
      :pageNumber="pageNumber"
      @page-change="handlePageChange"
    />
  </div>
  <div class="w-full bg-dp-background" data-cy="report-component">
    <!-- TODO - custom header; pages -->
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
