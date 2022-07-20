<script setup lang="ts">
import { defineAsyncComponent } from "vue";
const Formula = defineAsyncComponent(() => import("./Formula.vue"));
const p = defineProps<{ content: string }>();
</script>

<template>
    <formula :content="p.content"></formula>
</template>
