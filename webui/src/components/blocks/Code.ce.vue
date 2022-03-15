<script setup lang="ts">
import { onUnmounted, onMounted, ref } from "vue";
import { DPClipboard } from "../../../DPClipboard";
// TODO - trim code

const p = defineProps<{ language: string; code: string }>();
let clip: DPClipboard;
const copyBtn = ref<HTMLButtonElement | null>(null);
const { dpLocal } = window;

onMounted(() => {
  if (copyBtn.value) {
    clip = new DPClipboard(copyBtn.value, {
      text: p.code,
    });
  }
});

onUnmounted(() => {
  clip && clip.destroy();
});
</script>

<template>
  <div class="relative">
    <link v-if="!dpLocal" rel="stylesheet" href="/static/style.css" />
    <button
      class="absolute top-2 right-2 text-gray-700 h-5 w-5 opacity-75"
      ref="copyBtn"
    >
      <!-- TODO - use icon lib -->
      <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
        <title>Copy</title>
        <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z"></path>
        <path
          d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z"
        ></path>
      </svg>
    </button>
    <highlightjs :language="p.language" :code="p.code" data-cy="block-code" />
  </div>
</template>

<script lang="ts">
import "highlight.js/lib/common";
import "highlight.js/styles/stackoverflow-light.css";
import hljsVuePlugin from "@highlightjs/vue-plugin";

export default {
  components: {
    highlightjs: hljsVuePlugin.component,
  },
};
</script>

<style>
/* TODO - serve this css statically in a link tag to avoid bloating the web component */
@import "highlight.js/styles/stackoverflow-light.css";

pre {
  @apply w-full;
}
</style>
