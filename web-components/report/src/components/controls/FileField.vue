<script setup lang="ts">
import { computed, ComputedRef, ref } from "vue";
import { CloudArrowUpIcon } from "@heroicons/vue/24/outline";

const emit = defineEmits(["change"]);

const p = defineProps<{
    name: string;
    label?: string;
    required?: boolean;
}>();

const validation: ComputedRef = computed(() =>
    p.required ? [["+required"]] : [],
);

const hasFile = ref(false);

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
                throw new Error(`File type not string (${reader.result})`);
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

            hasFile.value = true;
        } else {
            emit("change", { name: p.name, value: undefined });

            hasFile.value = false;
        }
    });
};

const id = `file_${p.name}`;
</script>

<template>
    <form-kit
        type="file"
        :id="id"
        :label="label || name"
        name="parameter_files"
        :validation="validation"
        file-item-icon="fileDoc"
        file-remove-icon="trash"
        no-files-icon="fileDoc"
        validation-visibility="live"
        form="params-form"
        data-cy="file-field"
        @node="setupListeners"
    >
        <template #noFiles>
            <label
                class="flex w-full h-full items-center space-x-4 text-gray-500 hover:text-gray-700 formkit-no-files px-4 pt-3 pb-4 cursor-pointer"
                v-if="!hasFile"
                :for="id"
            >
                <cloud-arrow-up-icon class="w-6 h-6" />
                <div class="flex flex-col">
                    <span class="font-semibold text-sm">Upload a file</span
                    ><span class="text-xs">Up to 25mb supported.</span>
                </div>
            </label>
        </template>
    </form-kit>
</template>
