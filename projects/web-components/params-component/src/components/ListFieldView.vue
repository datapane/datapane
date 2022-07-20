<script setup lang="ts">
const p = defineProps<{ context: any }>();

const onChange = (event: any) => {
    p.context.node.input(event.target.value);
};

const onKeyDown = (event: any) => {
    if (event.key === "Enter" || event.key === ",") {
        const { value } = event.target;
        if (value.length > 0) {
            p.context.node.emit("newTag", event.target.value);
        }
        p.context.node.input("");
        event.preventDefault();
    }
};
</script>

<template>
    <input
        @input="onChange"
        @keydown="onKeyDown"
        :value="p.context._value"
        :class="p.context.classes.input"
        data-cy="list-field"
    />
</template>
