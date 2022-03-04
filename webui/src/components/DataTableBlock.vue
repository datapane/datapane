<script setup lang="ts">
import { defineCustomElements } from "@revolist/revogrid/custom-element";
defineCustomElements();

const rows = [
  {
    name: "New item",
    details: "Item description",
  },
];

const columns = [
  {
    prop: "name",
    name: "First",
  },
  {
    prop: "details",
    name: "Second",
  },
];
</script>

<template>
  <revo-grid
    :source.prop="rows"
    :columns.prop="columns"
    style="height: 200px"
  />
</template>
