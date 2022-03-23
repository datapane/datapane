<script setup lang="ts">
import { computed } from "vue";
import * as marked from "marked";
import hljs from "highlight.js";

(marked as any).setOptions({
    highlight: function (code: string, lang: string) {
        return hljs.highlight(lang, code).value;
    },
});

const p = defineProps<{ content: string; isLightProse: boolean }>();
const md = computed(() => (marked as any).parse(p.content));
</script>

<template>
    <div
        :class="[
            'w-full overflow-y-hidden prose font-dp-prose',
            { 'prose-dark': p.isLightProse },
        ]"
        data-cy="block-markdown"
        v-html="md"
    ></div>
</template>

<style>
@import "highlight.js/styles/stackoverflow-light.css";
</style>
