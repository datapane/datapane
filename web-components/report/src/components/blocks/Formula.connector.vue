<script setup lang="ts">
import { defineAsyncComponent } from "vue";
import BlockWrapper from "../layout/BlockWrapper.vue";
import { BlockFigureProps } from "../../data-model/blocks";
const Formula = defineAsyncComponent(() => import("./Formula.vue"));
const p = defineProps<{
    content: string;
    figure: BlockFigureProps;
    singleBlockEmbed?: boolean;
}>();
</script>

<template>
    <block-wrapper :figure="p.figure" :single-block-embed="singleBlockEmbed">
        <formula :content="p.content"></formula>
    </block-wrapper>
</template>
