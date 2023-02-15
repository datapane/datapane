<script setup lang="ts">
/**
 * Use a connector here so we can separate the data model from the Vue component in testing.
 * Also possible to pass the individual store properties from the data model class via `Function.componentProps`,
 * but this would remove re-rendering on `store.children` change.
 */
import { storeToRefs } from "pinia";
import { ref } from "vue";
import BlockWrapper from "../layout/BlockWrapper.vue";
import { TriggerType } from "../../data-model/types";
import { BlockFigureProps } from "../../data-model/blocks";
import FunctionBlock from "./Function.vue";
import { parseError } from "../../shared/shared";

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
const loading = ref<boolean>(false);

const onChange = (v: any) => {
    p.store.setField(v.name, v.value);
};

const update = async () => {
    try {
        error.value = undefined;
        loading.value = true;
        await p.store.update(p.functionId);
    } catch (e) {
        error.value = parseError(e);
        console.error(e);
    } finally {
        loading.value = false;
    }
};
</script>

<template>
    <block-wrapper :figure="p.figure" :show-overflow="true">
        <function-block
            :on-change="onChange"
            :update="update"
            :children="children"
            :function-id="p.functionId"
            :subtitle="p.subtitle"
            :label="p.label"
            :trigger="p.trigger"
            :timer="p.timer"
            :prompt="p.prompt"
            :error="error"
            :loading="loading"
        />
    </block-wrapper>
</template>
