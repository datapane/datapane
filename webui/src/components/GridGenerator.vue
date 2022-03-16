<script setup lang="ts">
/**
 * Recursively renders a grid of report blocks
 */

import {
  BlockTree,
  isGroup,
  isSelect,
  isToggle,
  isBlock,
} from "../data-model/blocks";
import { defineAsyncComponent, inject } from "vue";
import GroupLayout from "./blocks/Group.vue";
import BlockWrapper from "./blocks/BlockWrapper.vue";
const SelectLayout = defineAsyncComponent(() => import("./layout/Select.vue"));

const createGridKey = (child: BlockTree, idx: number) =>
  isBlock(child) ? `${child.refId}-${idx}` : `${child.name}-${idx}`;

const singleBlockEmbed = inject<boolean>("singleBlockEmbed");
const p = defineProps<{ tree: BlockTree }>();
</script>

<template>
  <template v-if="isGroup(p.tree)">
    <GroupLayout
      :columns="p.tree.columns"
      :singleBlockEmbed="!!singleBlockEmbed"
    >
      <GridGenerator
        v-for="(child, idx) in p.tree.children"
        :key="createGridKey(child, idx)"
        :tree="child"
      ></GridGenerator>
    </GroupLayout>
  </template>
  <template v-else-if="isSelect(p.tree)">
    <SelectLayout :select="p.tree" v-slot="slotProps">
      <GridGenerator :tree="p.tree.children[slotProps.tabNumber]" />
    </SelectLayout>
  </template>
  <template v-else-if="isToggle(p.tree)">
    <div><!-- TODO --></div>
  </template>
  <template v-else>
    <BlockWrapper
      :captionType="p.tree.captionType"
      :caption="p.tree.caption"
      :count="p.tree.count"
    >
      <component
        :is="p.tree.component"
        v-bind="p.tree.componentProps"
      ></component>
    </BlockWrapper>
  </template>
</template>
