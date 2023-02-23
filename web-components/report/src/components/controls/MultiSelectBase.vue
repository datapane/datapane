<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import MultiSelect from "vue-multiselect";

const p = defineProps<{ context: any }>();

const value = ref(p.context.tags.map((name: string) => ({ name })));
const options = ref(p.context.options.map((name: string) => ({ name })));

// Formkit validation only works on uncontrolled inputs using `p.context._value`, and vue-multiselect
// for Vue 3 seems to only support controlled input via `v-model`. So create a hidden input field
// which tracks the current multiselect state.
const hiddenRef = ref<any>();

onMounted(() => {
    /**
     * Initialize hidden input field with initial tags value
     */
    if (hiddenRef.value) {
        p.context.node.input(p.context.tags.join(","));
    } else {
        throw new Error("Tags field not properly initialized");
    }
});

watch(
    () => value,
    () => {
        const tags = value.value.map((v: any) => v.name);
        p.context.node.emit("newTag", tags);
        p.context.node.input(tags.join(","));
    },
    { deep: true },
);

const addTag = (name: string) => {
    const tag = { name };
    value.value.push(tag);
    options.value.push(tag);
};
</script>

<template>
    <input type="hidden" :value="p.context._value" ref="hiddenRef" />
    <multi-select
        v-model="value"
        tag-placeholder="Add this as new tag"
        placeholder="Search or add a tag"
        label="name"
        track-by="name"
        :multiple="true"
        :taggable="true"
        :options="options"
        @tag="addTag"
        v-bind="p.context.multiSelectProps"
    />
</template>
