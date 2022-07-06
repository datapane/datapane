<script setup lang="ts">
import { computed, ComputedRef } from "vue";

const p = defineProps<{
    step: number;
    value?: number;
    helpText?: string;
    name: string;
    required?: boolean;
    setValue: any;
    min: number;
    max: number;
}>();

const onChange = (event: any) => {
    const { value } = event.target;
    p.setValue(value === "" ? undefined : value);
};

const validation: ComputedRef = computed(() => {
    const validation = [
        ["matches", /^[^.]*$/], // make sure user can't type a float value
        ["min", String(p.min)],
        ["max", String(p.max)],
    ];
    if (p.required) {
        // For some reason "required" needs to be the first element in the formkit validation array
        validation.unshift(["required"]);
    }
    return validation;
});
</script>

<template>
    <form-kit
        type="number"
        :help="p.helpText"
        :label="p.name"
        :name="p.name"
        :value="p.value"
        :step="p.step"
        :validation="validation"
        validation-visibility="live"
        @keyup="onChange"
        @change="onChange"
        data-cy="int-field-unbounded"
    />
</template>
