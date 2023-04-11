<script setup lang="ts">
import { ref, watch } from "vue";

const emit = defineEmits(["change"]);

const p = defineProps<{
    name: string;
    min: number;
    max: number;
    step: number;
    initial?: number;
    required?: boolean;
    label?: string;
}>();

const onChange = (value?: string) => {
    emit("change", { name: p.name, value: value ? +value : undefined });
};

// Hold value in state so that it can be shown in input prefix
const inputValue = ref(p.initial);

// Cast inputValue to string to match the formkit type
watch(inputValue, () => void onChange(`${inputValue.value}`));
</script>

<template>
    <form-kit
        type="range"
        :label="label || name"
        :name="name"
        v-model="inputValue"
        :min="min"
        :max="max"
        :step="step"
        data-cy="range-field"
        outer-class="flex-1"
    >
        <template #prefix>
            <div class="pr-2">{{ inputValue }}</div>
        </template>
    </form-kit>
</template>
