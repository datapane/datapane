<script setup lang="ts">
const p = defineProps<{ language: string; code: string }>();
</script>

<template>
  <!-- TODO - copy button -->
  <div>
    <link rel="stylesheet" href="/static/style.css" />
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
  @apply w-full h-full;
}
</style>
