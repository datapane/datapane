<script setup lang="ts">
import { ref, watch } from "vue";

const p = defineProps<{
    step: number;
    value?: number;
    helpText?: string;
    name: string;
    required?: boolean;
    setValue: any;
}>();

// Hold value in state so that it can be shown in input prefix
const inputValue = ref(p.value);
watch(inputValue, () => void p.setValue(inputValue.value));
</script>

<template>
    <form-kit
        type="range"
        :help="p.helpText"
        :label="p.name"
        :name="p.name"
        v-model="inputValue"
        :step="p.step"
        data-cy="int-field-bounded"
    >
        <template #prefix>
            <div class="pr-2">{{ inputValue }}</div>
        </template>
    </form-kit>
</template>
