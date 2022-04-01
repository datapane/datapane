<script setup lang="ts">
import { DPClipboard } from "../../../../DPClipboard";
import { Section } from "../../../shared/shared";
import { ExportType } from "../../../data-model/blocks";
import DataTag from "./DataTag.vue";
import DPDropdown from "../../../shared/DPDropdown.vue";
import DPButton from "../../../shared/DPButton.vue";

const p = defineProps<{
    previewMode: boolean;
    queryOpen: boolean;
    rows: number;
    columns: number;
    cells: number;
    getCsvText: () => Promise<string>;
    downloadLocal: (type: ExportType) => Promise<void>;
    downloadRemote: (type: ExportType) => Promise<void>;
}>();

const emit = defineEmits(["toggle-query-open"]);

const withErrHandling = function (f: Function): any {
    return function (this: any, ...args: any[]) {
        return f.apply(this, args).catch((e: any) => {
            console.error(e);
        });
    };
};

const actionSections: Section[] = [
    {
        title: "Current State",
        options: [
            {
                name: "Copy CSV to clipboard",
                onClick: async () => DPClipboard.copyOnce(await p.getCsvText()),
                id: "copy-clipboard",
            },
            {
                name: "Download CSV",
                onClick: withErrHandling(p.downloadLocal),
                id: "download-csv",
            },
        ],
    },
    {
        title: "Original Data",
        options: [
            {
                name: "Download CSV",
                onClick: withErrHandling(() => p.downloadRemote("CSV")),
                id: "download-original-csv",
            },
            {
                name: "Download Excel",
                onClick: withErrHandling(() => p.downloadRemote("EXCEL")),
                id: "download-original-excel",
            },
        ],
    },
];

const showActions = !window.dpLocal && !p.previewMode;
</script>

<template>
    <div class="bg-gray-100 py-2" data-cy="block-datatable">
        <div class="flex justify-between items-center flex-wrap">
            <div class="flex justify-end md:space-x-2 ml-2">
                <DataTag :value="p.rows" icon="fa-bars" unit="rows" />
                <DataTag :value="p.columns" icon="fa-columns" unit="columns" />
                <DataTag :value="p.cells" icon="fa-th-large" unit="cells" />
            </div>
            <div
                v-if="showActions"
                class="min-w-0 flex items-center pr-2 sm:divide-x flex-wrap"
            >
                <div class="pr-2 sm:flex hidden space-x-2">
                    <DPButton
                        @click="emit('toggle-query-open')"
                        :icon="`fa ${
                            p.queryOpen ? 'fa-caret-up' : 'fa-caret-down'
                        }`"
                        :disabled="p.previewMode"
                        data-cy="btn-open-query"
                        class="dp-btn-info"
                    >
                        Run SQL Query
                    </DPButton>
                </div>
                <DPDropdown name="Export" :sections="actionSections" />
            </div>
        </div>
    </div>
</template>
