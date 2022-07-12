<script setup lang="ts">
import { paramsStore } from "../data-model/params-store";
import { watch } from "vue";
import HiddenParamsInput from "./HiddenParamsInput.vue";

const p = defineProps<{
    parameters_def: any[];
    updated_fields?: any;
    is_schedule?: boolean;
}>();

watch(
    () => [p.parameters_def, p.updated_fields, p.is_schedule],
    () =>
        void paramsStore.load(
            p.parameters_def,
            p.updated_fields,
            p.is_schedule
        ),
    { immediate: true }
);
</script>

<template>
    <Observer>
        <component
            v-if="paramsStore.fields"
            v-for="(field, idx) in paramsStore.fields"
            v-bind="field.props"
            :key="idx"
            :is="field.component"
        />
        <hidden-params-input />
    </Observer>
</template>

<style>
.formkit-file-name {
    overflow: hidden !important;
    max-width: 11rem !important;
}

:root {
    --fk-max-width-input: 100% !important;
}
</style>
