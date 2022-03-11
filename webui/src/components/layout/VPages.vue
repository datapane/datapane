<script setup lang="ts">
import { defineEmits } from "vue";

const p = defineProps<{ labels: string[]; pageNumber: number }>();

const emit = defineEmits(["page-change"]);
</script>

<template>
  <nav
    class="min-h-screen space-y-1 flex-fixed p-4 pl-0 hidden sm:block"
    aria-label="Sidebar"
  >
    <a
      v-for="(label, idx) in p.labels"
      :key="idx"
      :data-cy="`page-${idx}`"
      :class="[
        'flex items-center px-3 py-2 text-sm font-medium rounded-md cursor-pointer',
        {
          'text-dp-accent bg-dp-accent-light': idx === p.pageNumber,
          'text-dp-light-gray hover:text-dp-dark-gray hover:border-gray-300':
            idx !== p.pageNumber,
        },
      ]"
      :aria-current="idx === p.pageNumber ? 'page' : undefined"
      @click="emit('page-change', idx)"
    >
      {{ label }}
    </a>
  </nav>
</template>
