<script setup lang="ts">
import ReportComponent from "./ReportComponent.vue";
import LoadingSpinner from "./LoadingSpinner.vue";
import ErrorCallout from "./ErrorCallout.vue";
import { AppData, AppMetaData, ReportProps } from "../data-model/types";
import { computed, onMounted, ref } from "vue";
import { trackLocalReportView } from "../../../shared/dp-track";
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
    htmlHeader: ReportProps["htmlHeader"];
    webUrl?: AppMetaData["webUrl"];
    appData?: AppData;
}>();

const rootStore = useRootStore();
const error = ref<string | undefined>();

const setReport = async () => {
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

setReport();

const storeProps = storeToRefs(rootStore);
const { singleBlockEmbed, report } = storeProps;

onMounted(() => {
    /* View tracking */
    if (window.dpLocal) {
        trackLocalReportView("CLI_REPORT_VIEW");
    } else {
        // TODO - get app metadata for tracking
        // const { web_url, id, published, username, num_blocks } = p.report;
        // trackReportView({
        //     id: id,
        //     web_url: web_url,
        //     published,
        //     author_username: username,
        //     num_blocks,
        //     is_embed: window.location.href.includes("/embed/"),
        // });
    }
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
    <div v-if="!singleBlockEmbed" id="html-header" v-html="htmlHeader" />
    <report-component
        v-if="isView(report) && !error"
        :reset-app="setReport"
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
