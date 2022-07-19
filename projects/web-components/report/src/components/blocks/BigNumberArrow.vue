<script setup lang="ts">
import { computed, ComputedRef } from "vue";

const p = defineProps<{
    isPositiveIntent: boolean;
    isUpwardChange: boolean;
    change?: string;
}>();

const bgColor: ComputedRef<string> = computed(() =>
    p.isPositiveIntent ? "bg-green-100" : "bg-red-100"
);

const textColor: ComputedRef<string> = computed(() =>
    p.isPositiveIntent ? "text-green-800" : "text-red-800"
);
</script>

<template>
    <div
        v-if="p.change"
        :class="[
            `items-baseline px-2.5 py-0.5 rounded-full text-sm font-medium leading-5 ${bgColor} ${textColor} md:mt-2 lg:mt-0`,
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
</template>
