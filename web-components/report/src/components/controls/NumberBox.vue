<script setup lang="ts">
import { computed, ComputedRef } from "vue";

const emit = defineEmits(["change"]);

const p = defineProps<{
    name: string;
    label?: string;
    initial?: number;
    required?: boolean;
}>();

const onChange = (value: number) =>
    void emit("change", { name: p.name, value });

const validation: ComputedRef = computed(() =>
    p.required ? [["+required"]] : [],
);
</script>

<template>
    <form-kit
        type="number"
        :label="label || name"
        :name="name"
        :value="initial"
        :validation="validation"
        step="any"
        validation-visibility="live"
        @input="onChange"
        data-cy="number-field"
        outer-class="flex-1"
    />
</template>
