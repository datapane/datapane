<script setup lang="ts">
import { ref } from "vue";
import SvgBlock from "./SVG.vue";
import BlockWrapper from "../layout/BlockWrapper.vue";
import { BlockFigureProps } from "../../data-model/blocks";

const p = defineProps<{
    fetchAssetData: any;
    responsive: boolean;
    figure: BlockFigureProps;
    singleBlockEmbed?: boolean;
}>();

const plotSrc = ref<string | null>(null);

(async () => {
    plotSrc.value = await p.fetchAssetData();
})();
</script>

<template>
    <block-wrapper :figure="p.figure" :single-block-embed="singleBlockEmbed">
        <svg-block
            v-if="plotSrc"
            :src="plotSrc"
            :responsive="p.responsive"
            :single-block-embed="singleBlockEmbed"
        />
    </block-wrapper>
</template>
