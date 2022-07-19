<script setup lang="ts">
import { computed, ComputedRef } from "vue";

const p = defineProps<{
    value?: string[];
    helpText?: string;
    name: string;
    required?: boolean;
    setValue: any;
}>();

const validation: ComputedRef = computed(() =>
    p.required ? [["+required"]] : []
);

const setupListeners = (node: any) => {
    node.on("input", () => {
        if (node._value.length) {
            p.setValue(node._value[0].name);
        } else {
            p.setValue(undefined);
        }
    });
};
</script>

<template>
    <form-kit
        type="file"
        :label="p.name"
        name="parameter_files"
        :help="helpText"
        :validation="validation"
        validation-visibility="live"
        form="params-form"
        data-cy="file-field"
        @node="setupListeners"
    />
</template>
