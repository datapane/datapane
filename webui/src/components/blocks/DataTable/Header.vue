<script setup lang="ts">
const p = defineProps<{
  previewMode: boolean;
  rows: number;
  columns: number;
  cells: number;
}>();

const showActions = !window.dpLocal && !p.previewMode;
</script>

<script lang="ts">
import DataTag from "./DataTag.vue";

export default {
  components: {
    DataTag,
  },
};
</script>

<template>
  <div class="bg-gray-100 py-2" data-cy="block-datatable">
    <div class="flex justify-between items-center flex-wrap">
      <div class="flex justify-end md:space-x-2 ml-2">
        <DataTag :value="p.rows" icon="fa-bars" unit="rows" />
        <DataTag :value="p.columns" icon="fa-columns" unit="columns" />
        <DataTag :value="p.cells" icon="fa-th-large" unit="cells" />
      </div>
      <div
        v-if="showActions"
        class="min-w-0 flex items-center pr-2 sm:divide-x flex-wrap"
      >
        <div>Dropdown placeholder</div>
      </div>
    </div>
  </div>
</template>
