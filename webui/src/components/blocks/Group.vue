<script setup lang="ts">
const objOrEmpty = (obj: any, n: number) => (n > 0 ? obj : {});

const p = defineProps<{ columns: number }>();

const gridLayoutStyle = {
  ...objOrEmpty(
    {
      gridTemplateColumns: `repeat(${p.columns}, minmax(0, 1fr))`,
    },
    +p.columns
  ),
};
</script>

<template>
  <div
    :class="[
      'sm:grid sm:gap-4 py-4',
      { 'grid-flow-col grid-cols-fit': !p.columns },
    ]"
    :style="gridLayoutStyle"
  >
    <slot />
  </div>
</template>
