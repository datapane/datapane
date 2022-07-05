<script setup lang="ts">
import BigNumberArrow from "./BigNumberArrow.vue";

const p = defineProps<{
    heading: string;
    value: string;
    isPositiveIntent: boolean;
    isUpwardChange: boolean;
    prevValue?: string;
    change?: string;
}>();
</script>

<template>
    <div
        data-cy="block-bignumber"
        class="rounded-lg bg-white overflow-hidden border border-gray-300 w-full"
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
                        class="flex items-baseline text-2xl leading-8 font-semibold text-dp-accent"
                    >
                        {{ p.value }}
                        <span
                            v-if="p.prevValue"
                            class="ml-2 text-sm leading-5 font-medium text-gray-500"
                        >
                            from {{ p.prevValue }}
                        </span>
                        <big-number-arrow
                            class="hidden lg:hidden sm:inline-flex ml-2"
                            :is-positive-intent="p.isPositiveIntent"
                            :is-upward-change="p.isUpwardChange"
                            :change="p.change"
                        />
                    </div>
                    <big-number-arrow
                        class="inline-flex lg:inline-flex sm:hidden"
                        :is-positive-intent="p.isPositiveIntent"
                        :is-upward-change="p.isUpwardChange"
                        :change="p.change"
                    />
                </dd>
            </dl>
        </div>
    </div>
</template>
