<script setup lang="ts">
import { ReportStore } from "../data-model/report-store";
import GridGenerator from "./GridGenerator.vue";
import HPages from "./layout/HPages.vue";
import VPages from "./layout/VPages.vue";
import PrevNext from "./layout/PrevNext.vue";
import MobilePages from "./layout/MobilePages.vue";
import { ref, provide, computed, ComputedRef, onMounted } from "vue";
import { createGridKey } from "./utils";
import { LayoutBlock } from "../data-model/blocks";
import { setTheme } from "../theme";
import {
    trackLocalReportView,
    trackReportView,
} from "../../../shared/dp-track";
import { ReportProps } from "../data-model/types";

// Vue can't use a ts interface as props
// see https://github.com/vuejs/core/issues/4294
const p = defineProps<{
    isOrg: ReportProps["isOrg"];
    mode: ReportProps["mode"];
    disableTrackViews?: ReportProps["disableTrackViews"];
    htmlHeader?: ReportProps["htmlHeader"];
    report: ReportProps["report"];
}>();

const pageNumber = ref(0);

onMounted(() => {
    /* View tracking */
    if (window.dpLocal && window.dpLocalViewEvent) {
        trackLocalReportView();
    } else {
        if (p.disableTrackViews) {
            return;
        }
        const { web_url, id, published, username, num_blocks } = p.report;
        trackReportView({
            id: id,
            web_url: web_url,
            published,
            author_username: username,
            num_blocks,
            is_embed: window.location.href.includes("/embed/"),
        });
    }
});

// Set up deserialised report object and embed properties
const store = new ReportStore(p);
const { report, singleBlockEmbed } = store.state;
const multiBlockEmbed = p.mode === "EMBED" && !singleBlockEmbed;

provide("singleBlockEmbed", singleBlockEmbed);

const rootGroup: ComputedRef<LayoutBlock> = computed(
    () => report.children[pageNumber.value].children[0]
);

// HTML header is taken from the report object, unless overwritten via props
const htmlHeader = p.htmlHeader || p.report.output_style_header;

const htmlHeaderRef = (node: any) => {
    /**
     * Set report theme on HTML header node load
     */
    if (node !== null) {
        setTheme(p.report.output_is_light_prose);
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
        :ref="htmlHeaderRef"
        id="html-header"
        v-html="htmlHeader"
    />
    <div
        v-if="pageLabels.length > 1 && report.layout === 'top'"
        class="hidden sm:block w-full mb-6"
    >
        <h-pages
            :labels="pageLabels"
            :page-number="pageNumber"
            @page-change="handlePageChange"
        />
    </div>
    <div class="w-full bg-dp-background" data-cy="report-component">
        <div
            :class="{
                'flex flex-col justify-end bg-dp-background': true,
                'pb-10': p.isOrg && multiBlockEmbed,
                'pb-6': !p.isOrg && multiBlockEmbed,
            }"
        >
            <div className="sm:hidden p-2">
                <mobile-pages
                    :labels="pageLabels"
                    :page-number="pageNumber"
                    @page-change="handlePageChange"
                />
            </div>
            <div class="sm:flex block">
                <div
                    v-if="pageLabels.length > 1 && report.layout === 'side'"
                    class="hiddeLan sm:block w-1/6 bg-gray-100 px-4"
                >
                    <v-pages
                        :labels="pageLabels"
                        :page-number="pageNumber"
                        @page-change="handlePageChange"
                    />
                </div>
                <div class="flex-1 flex flex-col">
                    <div :class="['flex-grow', { 'px-4': !singleBlockEmbed }]">
                        <grid-generator
                            :key="createGridKey(rootGroup, 0)"
                            :tree="rootGroup"
                        />
                    </div>
                    <prev-next
                        v-if="pageLabels.length > 1"
                        :page-number="pageNumber"
                        :num-pages="pageLabels.length"
                        @page-change="handlePageChange"
                    />
                </div>
            </div>
        </div>
    </div>
</template>
