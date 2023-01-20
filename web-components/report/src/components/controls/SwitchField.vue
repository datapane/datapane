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
    <!--
         TODO - formkit checkbox sets its validation to `required` regardless of validation settings,
         if it is the sole parent element of a component. Hacky solution for now is to wrap the component in `span`s.
     -->
    <span>
        <form-kit
            type="checkbox"
            :value="initial"
            :label="label || name"
            :name="name"
            @input="onChange"
            data-cy="boolean-field"
        />
    </span>
</template>

<style>
:root {
    --fk-font-weight-option: bold !important;
}
</style>
