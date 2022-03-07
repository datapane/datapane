<script setup lang="ts">
/**
 * Centres block and adds caption below if necessary
 */

const p = defineProps<{ singleBlockEmbed: boolean }>();
</script>

<template>
  <div
    :class="[
      'w-full relative flex flex-col justify-center items-center overflow-x-auto',
      { 'h-iframe': p.singleBlockEmbed },
      { 'p-1 h-full': !p.singleBlockEmbed },
    ]"
  >
    <slot></slot>
    <!-- TODO - caption -->
  </div>
</template>
