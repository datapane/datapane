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
        :class="['w-full overflow-y-hidden', { dark: p.isLightProse }]"
        data-cy="block-markdown"
    >
        <div class="w-full prose font-dp-prose dark:prose-invert" v-html="md" />
    </div>
</template>

<style>
@import "highlight.js/styles/stackoverflow-light.css";

pre {
    background: #f6f6f6 !important;
}

.dark code {
    /* hack - TW prose disabling doesn't seem to work in invert mode, so this ensures
     non-highlighted code isn't affected by the prose-invert class */
    color: black;
}
</style>
