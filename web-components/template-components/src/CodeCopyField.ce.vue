<script setup lang="ts">
import { onMounted, ref, computed, withDefaults } from "vue";
import { DPClipboard } from "../../shared/DPClipboard";
import hljs from "highlight.js/lib/common";

const hlHtml = ref<string>();

const p = withDefaults(
    defineProps<{ language: string; title?: string; content: string }>(),
    { language: "python" },
);

const content = computed(() => p.content.replace(/\\"/g, '"'));

const copy = () => {
    DPClipboard.copyOnce(content.value);
};

onMounted(() => {
    hlHtml.value = hljs.highlight(content.value, {
        language: p.language,
    }).value;
});
</script>

<template>
    <div>
        <link rel="stylesheet" href="/static/report/index.css" />
        <link rel="stylesheet" href="/static/report/tailwind.css" />
        <div class="text-gray-500 pt-4" v-if="p.title">{{ p.title }}</div>
        <div class="mt-2">
            <div class="relative">
                <span>
                    <button
                        class="absolute right-2 top-2 border-0 bg-transparent hover:text-gray-800 text-gray-700 font-bold py-2 px-4 rounded inline-flex items-center"
                        @click="copy"
                    >
                        Copy code
                    </button>
                </span>
                <div id="code" class="border border-gray-200 rounded-lg p-2">
                    <pre v-html="hlHtml" />
                </div>
            </div>
        </div>
    </div>
</template>

<style>
.hljs {
    background: white !important;
}

pre {
    @apply w-full;
}
</style>
