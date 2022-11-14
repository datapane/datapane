<script setup lang="ts">
import { ref } from "vue";
import Folium from "./Folium.vue";
import { BlockFigureProps } from "../../data-model/blocks";

const p = defineProps<{
    fetchAssetData: any;
    figure: BlockFigureProps;
    singleBlockEmbed?: boolean;
}>();
const iframeContent = ref<string | null>(null);

(async () => {
    iframeContent.value = await p.fetchAssetData();
})();
</script>

<template>
    <block-wrapper :figure="p.figure" :single-block-embed="singleBlockEmbed">
        <folium
            v-if="iframeContent"
            :iframe-content="iframeContent"
            :single-block-embed="singleBlockEmbed"
        />
    </block-wrapper>
</template>
