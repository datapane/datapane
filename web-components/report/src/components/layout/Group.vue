<script setup lang="ts">
import { storeToRefs } from "pinia";
import { useRootStore } from "../../data-model/root-store";

const p = defineProps<{ columns: number; store: any }>();

const rootStore = useRootStore();
const { singleBlockEmbed } = storeToRefs(rootStore);
const { children } = storeToRefs(p.store);

const gridLayoutStyle =
    +p.columns > 0
        ? { gridTemplateColumns: `repeat(${p.columns}, minmax(0, 1fr))` }
        : {};
</script>

<template>
    <div
        :class="[
            'w-full sm:grid sm:gap-4',
            {
                'grid-flow-col grid-cols-fit': !p.columns,
                'py-4': !singleBlockEmbed,
            },
        ]"
        :style="gridLayoutStyle"
    >
        <component
            :is="child.component"
            v-for="child in children"
            v-bind="child.componentProps"
            :key="child.refId"
        />
    </div>
</template>
