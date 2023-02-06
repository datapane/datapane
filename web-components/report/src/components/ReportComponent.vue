<script setup lang="ts">
import HPages from "./layout/HPages.vue";
import VPages from "./layout/VPages.vue";
import PrevNext from "./layout/PrevNext.vue";
import MobilePages from "./layout/MobilePages.vue";
import { computed, ComputedRef } from "vue";
import { ReportProps } from "../data-model/types";
import { storeToRefs } from "pinia";
import { Block, View } from "../data-model/blocks";

// Vue can't use a ts interface as props
// see https://github.com/vuejs/core/issues/4294
const p = defineProps<{
    isOrg: ReportProps["isOrg"];
    mode: ReportProps["mode"];
    htmlHeader?: ReportProps["htmlHeader"];
    report: View;
}>();

// Set up deserialised report object

const { children, tabNumber, hasPages, layout } = storeToRefs(p.report.store);

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
        <div
            v-if="pages.length > 1 && layout === 'top'"
            class="hidden sm:block w-full mb-6"
        >
            <h-pages
                :labels="pageLabels"
                :page-number="tabNumber"
                @page-change="handlePageChange"
            />
        </div>
        <div class="w-full bg-dp-background" data-cy="report-component">
            <div
                :class="[
                    'flex flex-col justify-end bg-dp-background',
                    {
                        'pb-6': p.mode === 'EMBED',
                    },
                ]"
            >
                <div class="sm:hidden p-2" v-if="pages.length > 1">
                    <mobile-pages
                        :labels="pageLabels"
                        :page-number="tabNumber"
                        @page-change="handlePageChange"
                    />
                </div>
                <div class="sm:flex block">
                    <div
                        v-if="pages.length > 1 && layout === 'side'"
                        class="hidden sm:block flex-none w-1/6 bg-gray-100 px-4"
                    >
                        <v-pages
                            :labels="pageLabels"
                            :page-number="tabNumber"
                            @page-change="handlePageChange"
                        />
                    </div>
                    <div class="flex-1 flex flex-col min-w-0">
                        <div class="grow px-4">
                            <component
                                :is="child.component"
                                v-for="child in currentPage"
                                :key="child.refId"
                                v-bind="child.componentProps"
                            />
                        </div>
                        <prev-next
                            v-if="pages.length > 1"
                            :page-number="tabNumber"
                            :num-pages="pageLabels.length"
                            @page-change="handlePageChange"
                        />
                    </div>
                </div>
            </div>
        </div>
    </template>
</template>
