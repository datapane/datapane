<script setup lang="ts">
const p = defineProps<{ previewMode: boolean }>();

const showActions = !window.dpLocal && !p.previewMode;
</script>

<template>
  <div class="bg-gray-100 py-2" data-cy="block-datatable">
    <div class="flex justify-between items-center flex-wrap">
      <div
        v-if="showActions"
        class="min-w-0 flex items-center pr-2 sm:divide-x flex-wrap"
      >
        <div>Dropdown placeholder</div>
      </div>
    </div>
  </div>
</template>
