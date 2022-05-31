<script setup lang="ts">
/* eslint-disable no-useless-escape */
import { computed, ComputedRef, onMounted } from "vue";
import contentWindowJs from "iframe-resizer/js/iframeResizer.contentWindow.js?raw";
import { v4 as uuid4 } from "uuid";
import iframeResize from "iframe-resizer/js/iframeResizer";

const p = defineProps<{ iframeContent: string; singleBlockEmbed: boolean }>();
const iframeId = `iframe_${uuid4()}`;

// Unescape script tags when embedding
const iframeDoc: ComputedRef<string> = computed(() => {
    return p.iframeContent
        .replace("<body>", `<body><script>${contentWindowJs}<\/script>`)
});

onMounted(() => {
    iframeResize({ checkOrigin: false, warningTimeout: 10000 }, `#${iframeId}`);
});
</script>

<template>
    <iframe
        :id="iframeId"
        :style="{ border: 'none !important' }"
        :class="['w-full', { 'h-iframe': singleBlockEmbed }]"
        :srcdoc="iframeDoc"
        sandbox="allow-scripts"
    />
</template>
