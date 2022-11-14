<script setup lang="ts">
const p = defineProps<{
    initial: boolean;
    name: string;
    label?: string;
}>();

const emit = defineEmits(["change"]);

const onChange = (value: boolean) => {
    emit("change", { name: p.name, value });
};
</script>

<template>
    <form-kit
        type="checkbox"
        :value="initial"
        :label="label || name"
        :name="name"
        @input="onChange"
        data-cy="boolean-field"
    />
</template>

<style>
:root {
    --fk-font-weight-option: bold !important;
}
</style>
