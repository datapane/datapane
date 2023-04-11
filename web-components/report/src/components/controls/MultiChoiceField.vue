<script setup lang="ts">
import { computed, ComputedRef, ref } from "vue";

const emit = defineEmits(["change"]);

const p = defineProps<{
    initial: string[];
    options: string[];
    label?: string;
    required?: boolean;
    name: string;
}>();

const el = ref<any>();

const validation: ComputedRef = computed(() =>
    p.required ? [["+required"]] : [],
);

const multiSelectProps = {
    closeOnSelect: false,
    clearOnSelect: false,
    preserveSearch: true,
    placeholder: "",
    preselectFirst: false,
    searchable: false,
};

const setListeners = (node: any) => {
    /**
     * Overwrite tags with updated value and send to parent `Compute` component
     */
    node.on("newTag", ({ payload }: { payload: string[] }) => {
        emit("change", { name: p.name, value: payload });
    });
};
</script>

<template>
    <div class="mb-6" data-cy="multi-select-field">
        <form-kit
            type="multiSelectField"
            :label="label || name"
            :multiSelectProps="multiSelectProps"
            :name="name"
            :validation="validation"
            validation-visibility="live"
            :tags="p.initial"
            :options="options"
            ref="el"
            @node="setListeners"
        />
    </div>
</template>
