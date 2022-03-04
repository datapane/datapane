<script setup lang="ts">
import { computed } from "vue";
import * as marked from "marked";
const p = defineProps<{ content: string }>();

const md = computed(() => marked.parse(p.content));
</script>

<template>
  <div v-html="md"></div>
</template>
