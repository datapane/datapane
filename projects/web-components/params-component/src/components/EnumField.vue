<script setup lang="ts">
const p = defineProps<{
    value?: string;
    helpText?: string;
    name: string;
    required?: boolean;
    setValue: any;
    choices: string[];
}>();
</script>

<template>
    <span data-cy="enum-field">
        <form-kit
            type="radio"
            :label="p.name"
            :name="p.name"
            :options="p.choices"
            :help="p.helpText"
            :value="p.value"
            @input="p.setValue"
        />
    </span>
</template>
