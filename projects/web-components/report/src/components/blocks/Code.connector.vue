<script setup lang="ts">
import CodeBlock from "./Code.vue";
const p = defineProps<{ code: string; language: string }>();
const childProps = { code: p.code, language: p.language };
</script>

<template>
    <code-block v-bind="childProps" class="w-full"></code-block>
</template>
