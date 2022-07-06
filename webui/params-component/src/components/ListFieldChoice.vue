<script setup lang="ts">
import { computed, ComputedRef } from "vue";

const p = defineProps<{
    value?: string[];
    helpText?: string;
    name: string;
    required?: boolean;
    setValue: any;
    choices: string[];
}>();

const validation: ComputedRef = computed(() =>
    p.required ? [["+required"]] : []
);

const onChange = (items: string[]) => void p.setValue(items);
</script>

<template>
    <span data-cy="list-field-choices">
        <form-kit
            type="checkbox"
            :label="p.name"
            :name="p.name"
            :options="p.choices"
            :help="p.helpText"
            :validation="validation"
            :value="p.value"
            @input="onChange"
        />
    </span>
</template>
