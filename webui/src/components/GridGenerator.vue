<script setup lang="ts">
/**
 * Recursively renders a grid of report blocks
 */

import { BlockTree, isGroup, isSelect, isToggle } from "../data-model/blocks";
import { createGridKey } from "./utils";
import { defineAsyncComponent, inject } from "vue";
import GroupLayout from "./layout/Group.vue";
import BlockWrapper from "./layout/BlockWrapper.vue";
import ToggleLayout from "./layout/Toggle.vue";
const SelectLayout = defineAsyncComponent(() => import("./layout/Select.vue"));

const p = defineProps<{ tree: BlockTree }>();
const singleBlockEmbed = inject<boolean>("singleBlockEmbed");
</script>

<template>
    <template v-if="isGroup(p.tree)">
        <group-layout
            :columns="p.tree.columns"
            :single-block-embed="!!singleBlockEmbed"
        >
            <grid-generator
                v-for="(child, idx) in p.tree.children"
                :key="createGridKey(child, idx)"
                :tree="child"
            ></grid-generator>
        </group-layout>
    </template>
    <template v-else-if="isSelect(p.tree)">
        <select-layout :select="p.tree" v-slot="slotProps">
            <grid-generator :tree="p.tree.children[slotProps.tabNumber]" />
        </select-layout>
    </template>
    <template v-else-if="isToggle(p.tree)">
        <toggle-layout :label="p.tree.label">
            <grid-generator
                v-for="(child, idx) in p.tree.children"
                :key="createGridKey(child, idx)"
                :tree="child"
            ></grid-generator>
        </toggle-layout>
    </template>
    <template v-else>
        <block-wrapper
            :caption-type="p.tree.captionType"
            :caption="p.tree.caption"
            :count="p.tree.count"
        >
            <component
                :is="p.tree.component"
                v-bind="p.tree.componentProps"
            ></component>
        </block-wrapper>
    </template>
</template>
