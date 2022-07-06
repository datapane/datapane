<script setup lang="ts">
import { computed, ComputedRef } from "vue";

const p = defineProps<{
    value?: number;
    helpText?: string;
    name: string;
    required?: boolean;
    setValue: any;
}>();

const validation: ComputedRef = computed(() =>
    p.required ? [["required"]] : []
);

const onChange = (event: any) => {
    const { value } = event.target;
    p.setValue(value === "" ? undefined : value);
};
</script>

<template>
    <form-kit
        type="number"
        data-cy="float-field"
        :value="p.value"
        :help="p.helpText"
        :label="p.name"
        :name="p.name"
        :validation="validation"
        validation-visibility="live"
        @keyup="onChange"
        @change="onChange"
    />
</template>
