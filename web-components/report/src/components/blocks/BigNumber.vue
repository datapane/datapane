<script setup lang="ts">
import BigNumberArrow from "./BigNumberArrow.vue";
import BlockWrapper from "../layout/BlockWrapper.vue";
import { BlockFigureProps } from "../../data-model/blocks";

const p = defineProps<{
    heading: string;
    value: string;
    isPositiveIntent: boolean;
    isUpwardChange: boolean;
    figure: BlockFigureProps;
    singleBlockEmbed?: boolean;
    prevValue?: string;
    change?: string;
}>();
</script>

<template>
    <block-wrapper :figure="p.figure" :single-block-embed="singleBlockEmbed">
        <div
            data-cy="block-bignumber"
            class="rounded-md bg-white overflow-hidden border border-gray-300 w-full"
        >
            <div class="px-4 py-5 sm:p-6">
                <dl>
                    <dt
                        class="text-base leading-6 font-normal text-gray-900 truncate"
                    >
                        {{ p.heading }}
                    </dt>
                    <dd
                        class="mt-1 flex justify-between items-baseline md:block lg:flex"
                    >
                        <div
                            class="flex items-baseline text-4xl leading-8 font-semibold text-dp-accent"
                        >
                            {{ p.value }}
                        </div>
                        <big-number-arrow
                            class="inline-flex lg:inline-flex sm:hidden"
                            :is-positive-intent="p.isPositiveIntent"
                            :is-upward-change="p.isUpwardChange"
                            :prev-value="p.prevValue"
                            :change="p.change"
                        />
                    </dd>
                </dl>
            </div>
        </div>
    </block-wrapper>
</template>
