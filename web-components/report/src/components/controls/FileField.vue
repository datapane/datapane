<script setup lang="ts">
import { computed, ComputedRef } from "vue";

const emit = defineEmits(["change"]);

const p = defineProps<{
    name: string;
    label?: string;
    required?: boolean;
}>();

const validation: ComputedRef = computed(() =>
    p.required ? [["+required"]] : [],
);

const file2b64 = (file: File): Promise<string | null> =>
    /**
     * Convert DOM `File` object to base64 string that
     * can be stored as a JSON parameter
     */
    new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => {
            if (typeof reader.result !== "string") {
                throw `File type not string (${reader.result})`;
            }
            const [, b64String] = reader.result.split("base64,");
            resolve(b64String);
        };
        reader.onerror = (error) => reject(error);
    });

const setupListeners = (node: any) => {
    /**
     * Emit parameter change when file input changes
     */
    node.on("input", async () => {
        if (node._value.length) {
            emit("change", {
                name: p.name,
                value: await file2b64(node._value[0].file),
            });
        } else {
            emit("change", { name: p.name, value: undefined });
        }
    });
};
</script>

<template>
    <form-kit
        type="file"
        :label="label || name"
        name="parameter_files"
        :validation="validation"
        validation-visibility="live"
        form="params-form"
        data-cy="file-field"
        @node="setupListeners"
    />
</template>
