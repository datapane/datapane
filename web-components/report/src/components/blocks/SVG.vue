<script setup lang="ts">
const p = defineProps<{
    src: string;
    responsive: boolean;
    singleBlockEmbed?: boolean;
}>();
</script>

<template>
    <img
        :src="src"
        data-cy="block-svg"
        loading="lazy"
        :class="[
            'mx-auto p-1',
            {
                'w-full': p.responsive,
                'h-full': p.responsive && p.singleBlockEmbed,
                'max-w-none': !p.responsive, // Don't scale non-responsive SVGs like a normal image -- overwriting default browser `max-width: 100%`
                'absolute top-0 left-0': !p.responsive && p.singleBlockEmbed, // Prevent large embedded SVGs from being wrongly positioned in the iframe
            },
        ]"
    />
</template>
