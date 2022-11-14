<script setup lang="ts">
import { computed } from "vue";
import * as marked from "marked";
import hljs from "highlight.js";
import BlockWrapper from "../layout/BlockWrapper.vue";
import { BlockFigureProps } from "../../data-model/blocks";

(marked as any).setOptions({
    highlight: function (code: string, language: string) {
        return hljs.highlight(code, { language: language || "plaintext" })
            .value;
    },
});

const p = defineProps<{
    content: string;
    isLightProse: boolean;
    figure: BlockFigureProps;
    singleBlockEmbed?: boolean;
}>();
const md = computed(() => (marked as any).parse(p.content));
</script>

<template>
    <block-wrapper :figure="p.figure" :single-block-embed="singleBlockEmbed">
        <div
            :class="['w-full overflow-y-hidden', { dark: p.isLightProse }]"
            data-cy="block-markdown"
        >
            <div
                class="w-full prose font-dp-prose dark:prose-invert text-container"
                v-html="md"
            />
        </div>
    </block-wrapper>
</template>

<style scoped>
.text-container :deep(pre) {
    background: #f6f6f6 !important;
    padding: 1rem !important;
}

.dark :deep(code) {
    /* hack - TW prose disabling doesn't seem to work in invert mode, so this ensures
     non-highlighted code isn't affected by the prose-invert class */
    color: black;
}
</style>
