<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";
import { TriggerType } from "../../data-model/types";
import { ControlsField } from "../../data-model/blocks";

const p = defineProps<{
    onChange: (v: { name: string; value: any }) => void;
    update: () => void;
    children: ControlsField[];
    prompt: string;
    label: string;
    functionId: string;
    trigger: TriggerType;
    timer?: number;
    subtitle?: string;
}>();

const error = ref<string | undefined>();
const scheduleInterval = ref<ReturnType<typeof setInterval> | null>(null);

onMounted(() => {
    if (p.trigger === TriggerType.SCHEDULE && p.timer) {
        scheduleInterval.value = setInterval(p.update, p.timer * 1000);
    }
});

onUnmounted(() => {
    if (scheduleInterval.value) {
        clearInterval(scheduleInterval.value);
    }
});
</script>

<template>
    <div class="border shadow-sm bg-gray-50 rounded-md w-full max-w-3xl">
        <div class="px-4 py-5 sm:p-6">
            <div v-if="label">
                <h3 class="text-lg font-medium leading-6 text-gray-900">
                    {{ label }}
                </h3>
            </div>
            <div v-if="subtitle">
                <p class="mt-1 max-w-2xl text-sm text-gray-500">
                    {{ subtitle }}
                </p>
            </div>
            <component
                :is="child.component"
                v-for="child in children"
                v-bind="child.componentProps"
                :key="child.refId"
                @change="onChange"
            />
        </div>

        <div
            class="bg-gray-50 px-4 py-3 text-right sm:px-6"
            v-if="p.trigger === TriggerType.SUBMIT"
        >
            <button
                type="submit"
                @click="update"
                class="inline-flex justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:r ing-offset-2"
            >
                {{ p.prompt }}
            </button>
        </div>
        <div v-if="error" class="bg-red-100 p-4 mt-4">{{ error }}</div>
    </div>
</template>
