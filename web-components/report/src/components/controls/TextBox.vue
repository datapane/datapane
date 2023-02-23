<script setup lang="ts">
import { computed, ComputedRef } from "vue";

const emit = defineEmits(["change"]);

const p = defineProps<{
    name: string;
    type: "text" | "number";
    label?: string;
    initial?: string;
    required?: boolean;
}>();

const onChange = (value: string) =>
    void emit("change", { name: p.name, value });

const validation: ComputedRef = computed(() =>
    p.required ? [["+required"]] : [],
);
</script>

<template>
    <form-kit
        type="text"
        :label="label || name"
        :name="name"
        :value="initial"
        :validation="validation"
        validation-visibility="live"
        @input="onChange"
        data-cy="text-field"
        outer-class="flex-1"
    />
</template>
