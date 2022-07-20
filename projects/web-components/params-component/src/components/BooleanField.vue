<script setup lang="ts">
const p = defineProps<{
    value: boolean;
    helpText?: string;
    name: string;
    setValue: any;
}>();
</script>

<template>
    <form-kit
        type="checkbox"
        :label="p.name"
        :name="p.name"
        :help="p.helpText"
        @input="p.setValue"
        data-cy="boolean-field"
    />
</template>

<style>
:root {
    --fk-font-weight-option: bold !important;
}
</style>
