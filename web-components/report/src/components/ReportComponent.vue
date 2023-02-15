<script setup lang="ts">
import NavBar from "./layout/NavBar.vue";
import { computed, ComputedRef } from "vue";
import { ReportProps } from "../data-model/types";
import { storeToRefs } from "pinia";
import { Block, View } from "../data-model/blocks";

// Vue can't use a ts interface as props
// see https://github.com/vuejs/core/issues/4294
const p = defineProps<{
    isOrg: ReportProps["isOrg"];
    reportWidthClass: ReportProps["reportWidthClass"];
    mode: ReportProps["mode"];
    htmlHeader?: ReportProps["htmlHeader"];
    isServedApp: ReportProps["isServedApp"];
    resetApp: () => void;
    report: View;
}>();

// Set up deserialised report object

const { children, tabNumber, hasPages } = storeToRefs(p.report.store);

const pages: ComputedRef<Block[]> = computed(() =>
    hasPages.value ? children.value[0].children : [],
);

const pageLabels: ComputedRef<string[]> = computed(() =>
    pages.value.map((pa: Block, i: number) => pa.label || `Page ${i + 1}`),
);

const currentPage: ComputedRef<Block[]> = computed(() =>
    hasPages.value ? [pages.value[tabNumber.value]] : children.value,
);

const handlePageChange = (newPageNumber: number) =>
    p.report!.store.setTab(newPageNumber);
</script>

<template>
    <template v-if="p.report">
        <nav-bar
            :reset-app="p.resetApp"
            :is-served-app="p.isServedApp"
            :labels="pageLabels"
            :page-number="tabNumber"
            :report-width-class="p.reportWidthClass"
            @page-change="handlePageChange"
        />
        <main
            class="w-full bg-dp-background mx-auto"
            :class="p.reportWidthClass"
            data-cy="report-component"
        >
            <div
                :class="[
                    'flex flex-col justify-end bg-dp-background',
                    {
                        'pb-6': p.mode === 'EMBED',
                    },
                ]"
            >
                <div class="sm:flex block">
                    <div class="flex-1 flex flex-col min-w-0">
                        <div class="grow px-4">
                            <component
                                :is="child.component"
                                v-for="child in currentPage"
                                :key="child.refId"
                                v-bind="child.componentProps"
                            />
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </template>
</template>
