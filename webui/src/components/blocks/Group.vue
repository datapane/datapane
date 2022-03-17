<script setup lang="ts">
const p = defineProps<{ columns: number; singleBlockEmbed: boolean }>();
const gridLayoutStyle =
    +p.columns > 0
        ? { gridTemplateColumns: `repeat(${p.columns}, minmax(0, 1fr))` }
        : {};
</script>

<template>
    <div
        :class="[
            'sm:grid sm:gap-4',
            {
                'grid-flow-col grid-cols-fit': !p.columns,
                'py-4': !singleBlockEmbed,
            },
        ]"
        :style="gridLayoutStyle"
    >
        <slot />
    </div>
</template>
