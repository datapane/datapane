<script setup lang="ts">
const emit = defineEmits(["change"]);

const p = defineProps<{
    name: string;
    choices: string[];
    initial?: string;
    label?: string;
    required?: boolean;
}>();

const onChange = (value: string) => {
    emit("change", { name: p.name, value });
};
</script>

<template>
    <span data-cy="select-field">
        <form-kit
            type="select"
            :label="label || name"
            :name="name"
            :options="choices"
            :value="initial"
            @input="onChange"
        />
    </span>
</template>
