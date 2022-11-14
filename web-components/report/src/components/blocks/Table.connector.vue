<script setup lang="ts">
import { ref } from "vue";
import BlockWrapper from "../layout/BlockWrapper.vue";
import { BlockFigureProps } from "../../data-model/blocks";

const p = defineProps<{
    fetchAssetData: any;
    figure: BlockFigureProps;
    singleBlockEmbed?: boolean;
}>();
const html = ref<string | null>(null);

(async () => {
    html.value = await p.fetchAssetData();
})();
</script>

<template>
    <block-wrapper :figure="p.figure" :single-block-embed="singleBlockEmbed">
        <x-table-block
            v-if="html"
            :html="html"
            :single-block-embed="singleBlockEmbed"
            class="w-full"
        />
    </block-wrapper>
</template>
