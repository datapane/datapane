<script setup lang="ts">
import { ReportStore } from "../data-model/report-store";
import { ref, provide, computed } from "vue";
import { createGridKey } from "./utils";

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
import HPages from "./layout/HPages.vue";
import VPages from "./layout/VPages.vue";
import PrevNext from "./layout/PrevNext.vue";
import MobilePages from "./layout/MobilePages.vue";

export default {
  components: {
    GridGenerator,
    HPages,
    VPages,
    PrevNext,
    MobilePages,
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
      <div className="sm:hidden p-2">
        <MobilePages
          :labels="pageLabels"
          :pageNumber="pageNumber"
          @page-change="handlePageChange"
        />
      </div>
      <div class="sm:flex block">
        <div
          v-if="pageLabels.length > 1 && report.layout === 'side'"
          class="hidden sm:block w-1/6 bg-gray-100 px-4"
        >
          <VPages
            :labels="pageLabels"
            :pageNumber="pageNumber"
            @page-change="handlePageChange"
          />
        </div>
        <div class="flex-1 flex flex-col">
          <div :class="['flex-grow', { 'px-4': !singleBlockEmbed }]">
            <GridGenerator
              :key="createGridKey(rootGroup, 0)"
              :tree="rootGroup"
            ></GridGenerator>
          </div>
          <PrevNext
            v-if="pageLabels.length > 1"
            :pageNumber="pageNumber"
            :numPages="pageLabels.length"
            @page-change="handlePageChange"
          />
        </div>
      </div>
    </div>
  </div>
</template>
