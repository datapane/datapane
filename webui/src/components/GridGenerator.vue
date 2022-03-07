<script setup lang="ts">
/**
 * Recursively renders a grid of report blocks
 */

import { BlockTree, Group, isGroup } from "../data-model/blocks";

const objOrEmpty = (obj: any, n: number) => (n > 0 ? obj : {});
const p = defineProps<{ tree: BlockTree; singleBlockEmbed: boolean }>();
const columns = (p.tree as Group).columns;

const gridLayoutStyle = {
  ...objOrEmpty(
    {
      gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))`,
    },
    +columns
  ),
};
</script>

<template>
  <template v-if="isGroup(p.tree)">
    <div
      :class="[
        'sm:grid sm:gap-4 py-4',
        { 'grid-flow-col grid-cols-fit': !columns },
      ]"
      :style="gridLayoutStyle"
    >
      <GridGenerator
        v-for="child in p.tree.children"
        :key="child.refId"
        :tree="child"
        :singleBlockEmbed="p.singleBlockEmbed"
      ></GridGenerator>
    </div>
  </template>
  <template v-else>
    <BlockWrapper
      :singleBlockEmbed="p.singleBlockEmbed"
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

<script lang="ts">
import BlockWrapper from "./blocks/BlockWrapper.vue";
export default {
  components: {
    BlockWrapper,
  },
};
</script>
