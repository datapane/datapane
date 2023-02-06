<script setup lang="ts">
import ReportComponent from "./ReportComponent.vue";
import LoadingSpinner from "./LoadingSpinner.vue";
import { AppData, ReportProps } from "../data-model/types";
import { computed, onMounted, ref } from "vue";
import { trackLocalReportView } from "../../../shared/dp-track";
import { useRootStore } from "../data-model/root-store";
import { storeToRefs } from "pinia";
import { isView } from "../data-model/blocks";
import sanitizeHtml from "sanitize-html";
import { setTheme } from "../theme";

const p = defineProps<{
    isOrg: ReportProps["isOrg"];
    isLightProse: ReportProps["isLightProse"];
    mode: ReportProps["mode"];
    htmlHeader: ReportProps["htmlHeader"];
    appData: AppData;
}>();

const rootStore = useRootStore();
const error = ref<string | undefined>();

const setReport = async () => {
    try {
        await rootStore.setReport(p.appData, {
            isLightProse: p.isLightProse,
            mode: p.mode,
            isOrg: p.isOrg,
            // TODO - webUrl
            webUrl: "",
        });
    } catch (e) {
        error.value = "Something went wrong while fetching the app";
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
    <Teleport to="#header-target" v-if="dpAppRunner && isView(report)">
        <button @click="setReport" class="dp-btn dp-btn-sm dp-btn-primary">
            <div class="flex align-items justify-between">
                <div>Reset</div>
                <div class="ml-1.5">
                    <i class="fa fa-refresh" aria-hidden="true"></i>
                </div>
            </div>
        </button>
    </Teleport>
    <div v-if="!singleBlockEmbed" id="html-header" v-html="htmlHeader" />
    <report-component
        v-if="isView(report) && !error"
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
    <div v-if="error" class="bg-red-100 p-4 mt-4">{{ error }}</div>
</template>
