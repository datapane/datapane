<script setup lang="ts">
const p = defineProps<{ icon?: string; dataCy?: string }>();
</script>

<template>
    <button
        type="button"
        :class="[`dp-btn-sm disabled:opacity-50`]"
        :data-cy="p.dataCy"
    >
        <i v-if="p.icon" :class="`mr-2 ${p.icon}`" />
        <slot />
    </button>
</template>
