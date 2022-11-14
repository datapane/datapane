<script setup lang="ts">
import { computed, ComputedRef } from "vue";

const emit = defineEmits(["change"]);

const p = defineProps<{
    name: string;
    type: string;
    initial?: string;
    label?: string;
    required?: boolean;
}>();

const onChange = (event: Event) => {
    const target = event.target as HTMLInputElement;
    if (target) {
        emit("change", { name: p.name, value: target.value });
    }
};

const validation: ComputedRef = computed(() =>
    p.required ? [["+required"]] : [],
);
</script>

<template>
    <form-kit
        :type="type"
        :data-cy="`${p.type}-field`"
        :value="initial"
        :name="name"
        :label="label || name"
        :validation="validation"
        validation-visibility="live"
        @change="onChange"
        step="1"
    />
</template>
