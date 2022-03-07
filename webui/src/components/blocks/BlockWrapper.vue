<script setup lang="ts">
/**
 * Centres block and adds caption below if necessary
 */

const p = defineProps<{
  singleBlockEmbed: boolean;
  caption?: string;
  count?: number;
  captionType: string;
}>();
</script>

<template>
  <div
    :class="[
      'w-full relative flex flex-col justify-center items-center overflow-x-auto',
      { 'h-iframe': p.singleBlockEmbed },
      { 'p-1': !p.singleBlockEmbed },
    ]"
  >
    <slot></slot>
    <div
      v-if="p.caption"
      class="text-sm text-dp-light-gray italic text-justify"
    >
      <b>{{ p.captionType }} {{ p.count }}</b>
      {{ p.caption }}
    </div>
  </div>
</template>
