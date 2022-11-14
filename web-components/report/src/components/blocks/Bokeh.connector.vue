<script setup lang="ts">
import { ref, defineAsyncComponent } from "vue";
import { BlockFigureProps } from "../../data-model/blocks";
import BlockWrapper from "../layout/BlockWrapper.vue";
const BokehBlock = defineAsyncComponent(() => import("./Bokeh.vue"));

const p = defineProps<{
    fetchAssetData: any;
    responsive: boolean;
    figure: BlockFigureProps;
    singleBlockEmbed?: boolean;
}>();
const plotJson = ref<any>(null);

(async () => {
    plotJson.value = await p.fetchAssetData();
})();
</script>

<template>
    <block-wrapper :figure="p.figure" :single-block-embed="singleBlockEmbed">
        <bokeh-block
            v-if="plotJson"
            :plot-json="plotJson"
            :responsive="p.responsive"
            :single-block-embed="singleBlockEmbed"
        ></bokeh-block>
    </block-wrapper>
</template>
