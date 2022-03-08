<script setup lang="ts">
import { defineEmits } from "vue";

const p = defineProps<{ labels: string[]; pageNumber: number }>();

const emit = defineEmits(["page-change"]);

const handleChange = (evt: any) => void emit("page-change", +evt.target.value);
</script>

<template>
  <select
    id="tabs"
    name="tabs"
    class="flex-initial block w-full focus:ring-indigo-500 focus:border-indigo-500 border-gray-300 rounded-md"
    data-cy="pages-tabs"
    @change="handleChange"
  >
    <option v-for="(label, idx) in p.labels" :key="idx" :value="idx">
      {{ label }}
    </option>
  </select>
</template>
