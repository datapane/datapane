<script setup lang="ts">
import BlockWrapper from "../layout/BlockWrapper.vue";
import { BlockFigureProps } from "../../data-model/blocks";

const p = defineProps<{
    src: string;
    type: string;
    figure: BlockFigureProps;
    singleBlockEmbed?: boolean;
}>();
</script>

<template>
    <block-wrapper :figure="p.figure" :single-block-embed="singleBlockEmbed">
        <div
            class="w-full flex items-center justify-center"
            data-cy="block-media"
        >
            <video
                v-if="p.type.startsWith('video')"
                controls
                :src="p.src"
                width="800"
            ></video>
            <audio
                v-else-if="p.type.startsWith('audio')"
                controls
                :src="p.src"
                class="w-full"
            ></audio>
            <img v-else :src="p.src" loading="lazy" class="mx-auto" />
        </div>
    </block-wrapper>
</template>
