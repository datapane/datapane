<script setup lang="ts">
/* eslint-disable no-useless-escape */
import { computed, ComputedRef, onMounted } from "vue";
import contentWindowJs from "iframe-resizer/js/iframeResizer.contentWindow.js?raw";
import { v4 as uuid4 } from "uuid";
import iframeResize from "iframe-resizer/js/iframeResizer";

const p = defineProps<{ html: string; isIframe: boolean }>();
const iframeId = `iframe_${uuid4()}`;

const iframeDoc: ComputedRef<string> = computed(() => {
    /**
     * Inject the JS needed to make the iframe resizer work
     */
    return `
        <!DOCTYPE html>
        <html>
        <body>
            <script>${contentWindowJs}<\/script>
            ${p.html}
        </body>
        </html>
    `;
});

onMounted(() => {
    iframeResize({ checkOrigin: false }, `#${iframeId}`);
});
</script>

<template>
    <div
        v-if="isIframe"
        v-html="p.html"
        class="flex justify-center items-center"
    />
    <iframe
        v-else
        :id="iframeId"
        :srcdoc="iframeDoc"
        class="flex justify-center items-center"
    />
</template>
