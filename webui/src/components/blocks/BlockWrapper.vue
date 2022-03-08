<script setup lang="ts">
/**
 * Centres block and adds caption below if necessary
 */
import { inject } from "vue";

const p = defineProps<{
  caption?: string;
  count?: number;
  captionType: string;
}>();

const singleBlockEmbed = inject("singleBlockEmbed");
</script>

<template>
  <div
    :class="[
      'w-full relative flex flex-col justify-center items-center overflow-x-auto',
      { 'h-iframe': singleBlockEmbed },
      { 'p-1': !singleBlockEmbed },
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
