<script setup lang="ts">
import { ReportStore } from "../data-model/report-store";
import { ref, provide, computed, ComputedRef } from "vue";
import { createGridKey } from "./utils";
import { LayoutBlock } from "../data-model/blocks";
import { setTheme } from "../theme";

const p = defineProps<{ reportProps: any }>();
const store = new ReportStore(p.reportProps);
const { report, singleBlockEmbed } = store.state;
const pageNumber = ref(0);

const multiBlockEmbed =
  p.reportProps.mode === "EMBED" && !store.state.singleBlockEmbed;

const rootGroup: ComputedRef<LayoutBlock> = computed(
  () => report.children[pageNumber.value].children[0]
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

const htmlHeaderRef = ref<HTMLDivElement | null>(null);
const htmlHeader =
  p.reportProps.htmlHeader || p.reportProps.report.output_style_header;

const onHeaderChange = (node: HTMLDivElement) => {
  if (node !== null) {
    setTheme(p.reportProps.report.is_light_prose);
  }
};
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
    v-if="!singleBlockEmbed"
    v-html="htmlHeader"
    :ref="onHeaderChange"
    id="html-header"
  />
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
          class="hiddeLan sm:block w-1/6 bg-gray-100 px-4"
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
