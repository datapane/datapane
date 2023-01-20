<script setup lang="ts">
const p = defineProps<{ large?: boolean }>();
</script>

<template>
    <i
        :class="['fa fa-gear fa-spin opacity-70', { 'fa-6x': p.large }]"
        aria-hidden="true"
    ></i>
</template>
