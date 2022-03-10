<script setup lang="ts">
/**
 * Recursively renders a grid of report blocks
 */

import { BlockTree, Group, isBlock, isGroup } from "../data-model/blocks";
import { inject } from "vue";

const createGridKey = (child: BlockTree, idx: number) =>
  isBlock(child) ? `${child.refId}-${idx}` : `${child.name}-${idx}`;

const singleBlockEmbed = inject("singleBlockEmbed");
const p = defineProps<{ tree: BlockTree }>();
</script>

<template>
  <template v-if="isGroup(p.tree)">
    <GroupLayout :columns="p.tree.columns">
      <GridGenerator
        v-for="(child, idx) in p.tree.children"
        :key="createGridKey(child, idx)"
        :tree="child"
      ></GridGenerator>
    </GroupLayout>
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

<script lang="ts">
import BlockWrapper from "./blocks/BlockWrapper.vue";
import GroupLayout from "./blocks/Group.vue";

export default {
  components: {
    BlockWrapper,
    GroupLayout,
  },
};
</script>
