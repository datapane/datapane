<script setup lang="ts">
import { computed, ComputedRef, onMounted } from "vue";
import iframeResize from "iframe-resizer/js/iframeResizer";
import userIframeCss from "../../styles/user-iframe.css?inline";
import contentWindowJs from "iframe-resizer/js/iframeResizer.contentWindow.js?raw";

const p = defineProps<{ html: string; sandbox?: string }>();

const iframeDoc: ComputedRef<string> = computed(() => {
  return `
        <!DOCTYPE html>
        <body>
            <style>${userIframeCss}</style>
            <script>${contentWindowJs}<\/script>
            <div class="doc-root">${p.html}</div>
        </body>
        </html>
    `;
});

onMounted(() => {
  iframeResize({ log: true, checkOrigin: false }, "#my-iframe");
});
</script>

<template>
  <iframe
    :srcdoc="iframeDoc"
    :sandbox="p.sandbox"
    id="my-iframe"
    width="100%"
    frameborder="0"
    data-cy="block-user-iframe"
  ></iframe>
</template>
