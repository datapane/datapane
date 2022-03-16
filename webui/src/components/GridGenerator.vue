<script setup lang="ts">
/**
 * Recursively renders a grid of report blocks
 */

import {
  BlockTree,
  Group,
  isBlock,
  isGroup,
  isSelect,
} from "../data-model/blocks";
import BlockWrapper from "./blocks/BlockWrapper.vue";
import GroupLayout from "./blocks/Group.vue";
import { inject, defineAsyncComponent } from "vue";
const Select = defineAsyncComponent(() => import("./layout/Select.vue"));

const createGridKey = (child: BlockTree, idx: number) =>
  isBlock(child) ? `${child.refId}-${idx}` : `${child.name}-${idx}`;

const singleBlockEmbed = inject("singleBlockEmbed");
const p = defineProps<{ tree: BlockTree }>();
</script>

<template>
  <template v-if="isGroup(p.tree)">
    <GroupLayout :columns="p.tree.columns" :singleBlockEmbed="singleBlockEmbed">
      <GridGenerator
        v-for="(child, idx) in p.tree.children"
        :key="createGridKey(child, idx)"
        :tree="child"
      ></GridGenerator>
    </GroupLayout>
  </template>
  <template v-else-if="isSelect(p.tree)">
    <Select :select="p.tree" />
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
