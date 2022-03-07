<script setup lang="ts">
const p = defineProps<{ code: string; language: string }>();
const childProps = { code: p.code, language: p.language };
</script>

<template>
  <dp-code-block v-bind="childProps" class="w-full h-full"></dp-code-block>
</template>
