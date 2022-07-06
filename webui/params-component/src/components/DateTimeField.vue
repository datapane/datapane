<script setup lang="ts">
const p = defineProps<{
    value?: string;
    helpText?: string;
    name: string;
    setValue: any;
    type: string;
}>();

const onChange = (event: Event) => {
    const target = event.target as HTMLInputElement;
    if (target) {
        p.setValue(target.value);
    }
};
</script>

<template>
    <form-kit
        :type="p.type"
        :data-cy="`${p.type}-field`"
        :value="p.value"
        :help="helpText"
        :name="name"
        :label="name"
        @change="onChange"
        step="1"
    />
</template>
