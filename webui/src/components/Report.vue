<script setup lang="ts">
import { ReportStore } from "../data-model/report-store";
import GridGenerator from "./GridGenerator.vue";
import HPages from "./layout/HPages.vue";
import VPages from "./layout/VPages.vue";
import PrevNext from "./layout/PrevNext.vue";
import MobilePages from "./layout/MobilePages.vue";
import { ref, provide, computed, ComputedRef } from "vue";
import { createGridKey } from "./utils";
import { LayoutBlock } from "../data-model/blocks";
import { setTheme } from "../theme";

const p = defineProps<{ reportProps: any }>();
const pageNumber = ref(0);

// Set up deserialised report object and embed properties
const store = new ReportStore(p.reportProps);
const { report, singleBlockEmbed } = store.state;
const multiBlockEmbed = p.reportProps.mode === "EMBED" && !singleBlockEmbed;

provide("singleBlockEmbed", singleBlockEmbed);

const rootGroup: ComputedRef<LayoutBlock> = computed(
    () => report.children[pageNumber.value].children[0]
);

// HTML header is taken from the report object, unless overwritten via props
const htmlHeader =
    p.reportProps.htmlHeader || p.reportProps.report.output_style_header;

const htmlHeaderRef = (node: any) => {
    /**
     * Set report theme on HTML header node load
     */
    if (node !== null) {
        setTheme(p.reportProps.report.is_light_prose);
    } else {
        console.error("Unable to find HTML header node");
    }
};

const pageLabels = report.children.map(
    (page, idx) => page.label || `Page ${idx + 1}`
);

const handlePageChange = (newPageNumber: number) =>
    (pageNumber.value = newPageNumber);
</script>

<template>
    <div
        v-if="!singleBlockEmbed"
        v-html="htmlHeader"
        :ref="htmlHeaderRef"
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
