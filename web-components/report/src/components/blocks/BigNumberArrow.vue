<script setup lang="ts">
import { computed, ComputedRef } from "vue";

const p = defineProps<{
    isPositiveIntent: boolean;
    isUpwardChange: boolean;
    change?: string;
    prevValue?: string;
}>();

const bgColor: ComputedRef<string> = computed(() =>
    p.isPositiveIntent ? "bg-green-100" : "bg-red-100",
);

const textColor: ComputedRef<string> = computed(() =>
    p.isPositiveIntent ? "text-green-800" : "text-red-800",
);
</script>

<template>
    <div v-if="p.change" class="flex justify-start align-center">
        <div
            v-if="p.change"
            :class="[
                `items-baseline px-2.5 py-0.5 rounded-lg text-sm font-medium leading-5 ${bgColor} ${textColor}`,
            ]"
        >
            {{ p.isUpwardChange ? "+" : "-" }}{{ p.change }}
        </div>
        <div v-if="p.prevValue" class="pl-1 text-gray-500">
            from {{ p.prevValue }}
        </div>
    </div>
</template>
