<script setup lang="ts">
import { ref, defineAsyncComponent } from "vue";
import { BlockFigureProps } from "../../data-model/blocks";
import BlockWrapper from "../layout/BlockWrapper.vue";
import { useRootStore } from "../../data-model/root-store";
import { storeToRefs } from "pinia";
const VegaBlock = defineAsyncComponent(() => import("./Vega.vue"));

const rootStore = useRootStore();
const { singleBlockEmbed } = storeToRefs(rootStore);

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
        <vega-block
            v-if="plotJson"
            :plot-json="plotJson"
            :responsive="p.responsive"
            :single-block-embed="singleBlockEmbed"
        ></vega-block>
    </block-wrapper>
</template>
