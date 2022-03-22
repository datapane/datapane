<script setup lang="ts">
import { computed, ComputedRef } from "vue";

const p = defineProps<{
    heading: string;
    value: string;
    isPositiveIntent: boolean;
    isUpwardChange: boolean;
    prevValue?: string;
    change?: string;
}>();

const bgColor: ComputedRef<string> = computed(() =>
    p.isPositiveIntent ? "green" : "red"
);
</script>

<template>
    <div
        data-cy="block-bignumber"
        class="rounded-lg bg-white overflow-hidden border border-gray-300 md:grid-cols-3 w-full"
    >
        <div class="px-4 py-5 sm:p-6">
            <dl>
                <dt class="text-base leading-6 font-normal text-gray-900">
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
                    </div>
                    <div
                        v-if="p.change"
                        :class="[
                            `inline-flex items-baseline px-2.5 py-0.5 rounded-full text-sm font-medium leading-5 bg-${bgColor}-100 text-${bgColor}-800 md:mt-2 lg:mt-0`,
                        ]"
                    >
                        <i
                            :class="[
                                'mr-1 fa',
                                {
                                    'fa-arrow-up': p.isUpwardChange,
                                    'fa-arrow-down': !p.isUpwardChange,
                                },
                            ]"
                        />
                        {{ p.change }}
                    </div>
                </dd>
            </dl>
        </div>
    </div>
</template>
