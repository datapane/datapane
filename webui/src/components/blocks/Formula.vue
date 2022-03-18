<script setup lang="ts">
import katex from "katex";
const p = defineProps<{ content: string }>();

const renderFormula = (node: any) => {
    try {
        katex.render(p.content, node);
    } catch (e) {
        console.error(`Error rendering formula: ${e}`);
    }
};

const formulaRef = (node: any) => {
    renderFormula(node);
};
</script>

<template>
    <div
        data-cy="block-formula"
        className="w-full overflow-y-hidden bg-white flex justify-center"
        :ref="formulaRef"
    />
</template>

<style>
@import "katex/dist/katex.min.css";
</style>
