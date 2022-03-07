<script setup lang="ts">
import { computed } from "vue";
import * as marked from "marked";

const p = defineProps<{ content: string; isLightProse: boolean }>();
const md = computed(() => marked.parse(p.content));
</script>

<template>
  <!-- TODO - linkReference, gfm needed? -->
  <div
    :class="[
      'w-full h-full overflow-y-hidden prose font-dp-prose',
      { proseDark: p.isLightProse },
    ]"
    data-cy="block-markdown"
    v-html="md"
  ></div>
</template>
