<script setup lang="ts">
const p = defineProps<{ iframeContent: string; singleBlockEmbed: boolean }>();
const IFRAME_HEIGHT = "35rem";
</script>

<template>
    <div
        :style="{ height: IFRAME_HEIGHT }"
        :class="[
            'flex justify-center w-full',
            { 'h-iframe': singleBlockEmbed },
        ]"
        data-cy="block-iframe"
    >
        <iframe
            :style="{ border: 'none !important' }"
            :class="['w-full', { 'h-iframe': singleBlockEmbed }]"
            :srcdoc="p.iframeContent"
            sandbox="allow-scripts"
        />
    </div>
</template>
