<script setup lang="ts">
const p = defineProps<{ code: string; language: string }>();
const childProps = { code: p.code, language: p.language };
</script>

<template>
    <dpx-code-block v-bind="childProps" class="w-full"></dpx-code-block>
</template>
