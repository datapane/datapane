<script setup lang="ts">
import { computed, ComputedRef } from "vue";

const emit = defineEmits(["change"]);

const p = defineProps<{
    name: string;
    label?: string;
    initial?: number;
    required?: boolean;
}>();

const onChange = (event: any) => {
    const { value } = event.target;
    emit("change", { name: p.name, value: +value });
};

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
        @keyup="onChange"
        data-cy="number-field"
        outer-class="flex-1"
    />
</template>
