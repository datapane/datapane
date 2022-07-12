<script setup lang="ts">
import { inject } from "vue";
const p = defineProps<{ src: string; responsive: boolean }>();
const singleBlockEmbed = inject("singleBlockEmbed");
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
                'h-full': p.responsive && singleBlockEmbed,
                'max-w-none': !p.responsive, // Don't scale non-responsive SVGs like a normal image -- overwriting default browser `max-width: 100%`
                'absolute top-0 left-0': !p.responsive && singleBlockEmbed, // Prevent large embedded SVGs from being wrongly positioned in the iframe
            },
        ]"
    />
</template>
