<script setup lang="ts">
import { computed, ComputedRef } from "vue";

const p = defineProps<{
    value: string;
    helpText?: string;
    name: string;
    required?: boolean;
    setValue: any;
}>();

const onChange = (event: any) => {
    const { value } = event.target;
    p.setValue(value === "" ? undefined : value);
};

const validation: ComputedRef = computed(() =>
    p.required ? [["+required"]] : []
);
</script>

<template>
    <form-kit
        type="text"
        :help="p.helpText"
        :label="p.name"
        :name="p.name"
        :value="p.value"
        :validation="validation"
        validation-visibility="live"
        @keyup="onChange"
        data-cy="string-field"
    />
</template>
