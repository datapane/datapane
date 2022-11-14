<script setup lang="ts">
/**
 * Use a connector here so we can separate the data model from the Vue component in testing.
 * Also possible to pass the individual store properties from the data model class via `Interactive.componentProps`,
 * but this would remove re-rendering on `store.children` change.
 */
import { storeToRefs } from "pinia";
import { onMounted, onUnmounted, ref } from "vue";
import BlockWrapper from "../layout/BlockWrapper.vue";
import { TriggerType } from "../../data-model/types";
import { BlockFigureProps } from "../../data-model/blocks";
import Interactive from "./Interactive.vue";

const p = defineProps<{
    store: any;
    prompt: string;
    label: string;
    functionId: string;
    trigger: TriggerType;
    figure: BlockFigureProps;
    timer?: number;
    subtitle?: string;
}>();

const { children } = storeToRefs(p.store);
const error = ref<string | undefined>();
const scheduleInterval = ref<ReturnType<typeof setInterval> | null>(null);

const onChange = (v: any) => {
    p.store.setField(v.name, v.value);
};

const update = async () => {
    try {
        await p.store.update(p.functionId);
    } catch (e: any) {
        if (e.name === "TargetNotFoundError") {
            error.value = e.message;
        } else {
            error.value = "Something went wrong while updating the app";
        }
        console.error(e);
    }
};

onMounted(() => {
    if (p.trigger === TriggerType.SCHEDULE && p.timer) {
        scheduleInterval.value = setInterval(update, p.timer * 1000);
    }
});

onUnmounted(() => {
    if (scheduleInterval.value) {
        clearInterval(scheduleInterval.value);
    }
});
</script>

<template>
    <block-wrapper :figure="p.figure" :show-overflow="true">
        <interactive
            :on-change="onChange"
            :update="update"
            :children="children"
            :function-id="p.functionId"
            :subtitle="p.subtitle"
            :label="p.label"
            :trigger="p.trigger"
            :prompt="p.prompt"
        />
    </block-wrapper>
</template>
