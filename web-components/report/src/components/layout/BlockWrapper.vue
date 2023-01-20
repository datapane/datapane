<script setup lang="ts">
/**
 * Centres block and adds caption below if necessary
 */
import { toRefs } from "vue";
import { BlockFigureProps } from "../../data-model/blocks";

const p = defineProps<{
    figure: BlockFigureProps;
    singleBlockEmbed?: boolean;
    showOverflow?: boolean;
}>();

const { caption, count, captionType } = toRefs(p.figure);
const singleBlockEmbed = false;
</script>

<template>
    <div
        :class="[
            'w-full relative flex flex-col justify-center items-center',
            { 'h-iframe': singleBlockEmbed },
            { 'py-3 px-1': !singleBlockEmbed },
            // TODO - why does overflow-x-auto create auto-y overflow in `Function` block?
            { 'overflow-x-auto': !p.showOverflow },
            { 'overflow-visible': p.showOverflow },
        ]"
    >
        <slot />
        <div
            v-if="caption"
            class="text-sm text-dp-light-gray italic text-justify"
        >
            <b>{{ captionType }} {{ count }}</b>
            {{ caption }}
        </div>
    </div>
</template>
