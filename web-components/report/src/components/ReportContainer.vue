<script setup lang="ts">
import ReportComponent from "./ReportComponent.vue";
import LoadingSpinner from "./LoadingSpinner.vue";
import ErrorCallout from "./ErrorCallout.vue";
import { AppData, AppMetaData, ReportProps } from "../data-model/types";
import { computed, onMounted, ref } from "vue";
import { useRootStore } from "../data-model/root-store";
import { storeToRefs } from "pinia";
import { isView } from "../data-model/blocks";
import sanitizeHtml from "sanitize-html";
import { setTheme } from "../theme";
import { parseError } from "../shared/shared";

const p = defineProps<{
    isOrg: ReportProps["isOrg"];
    isLightProse: ReportProps["isLightProse"];
    reportWidthClass: ReportProps["reportWidthClass"];
    mode: ReportProps["mode"];
    id: ReportProps["id"];
    htmlHeader: ReportProps["htmlHeader"];
    webUrl?: AppMetaData["webUrl"];
    appData?: AppData;
}>();

const rootStore = useRootStore();
const error = ref<string | undefined>();

const setApp = async () => {
    try {
        await rootStore.setReport(
            {
                isLightProse: p.isLightProse,
                mode: p.mode,
                isOrg: p.isOrg,
                webUrl: p.webUrl,
            },
            p.appData,
        );
    } catch (e) {
        error.value = parseError(e);
        console.error(e);
    }
};

const resetApp = async () => {
    try {
        await rootStore.resetAppSession();
    } catch (e) {
        error.value = parseError(e);
        console.error(e);
    }
    await setApp();
};

setApp();

const storeProps = storeToRefs(rootStore);
const { report } = storeProps;

onMounted(() => {
    return;
});

const htmlHeader = computed(() => {
    // HTML header is taken from the report object, unless overwritten via props
    // TODO - support setting via report object?
    const dirtyHeader = p.htmlHeader;
    return p.isOrg
        ? dirtyHeader
        : sanitizeHtml(dirtyHeader, {
              allowedTags: ["style"],
              allowedAttributes: {
                  style: [],
              },
              allowVulnerableTags: true, // Suppress warning for allowing `style`
          });
});

onMounted(() => {
    setTheme(p.isLightProse);
});

const { dpAppRunner } = window;
</script>

<template>
    <div id="html-header" v-html="htmlHeader" />
    <report-component
        v-if="isView(report) && !error"
        :reset-app="resetApp"
        :is-served-app="dpAppRunner"
        :report-width-class="p.reportWidthClass"
        :is-org="p.isOrg"
        :mode="p.mode"
        :report="report"
        :key="report.refId"
    />
    <div
        v-else-if="!isView(report) && !error"
        class="flex items-center justify-center h-screen w-full -mt-12"
    >
        <loading-spinner :large="true" />
    </div>
    <error-callout v-if="error" :error="error" />
</template>
