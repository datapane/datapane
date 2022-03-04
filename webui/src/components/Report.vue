<script setup lang="ts">
import { ReportStore } from "../data-model/report-store";
// import GridGenerator from "./GridGenerator.vue";
import { ref, reactive, toRaw } from "vue";

const p = defineProps<{ report: any }>();
const store = new ReportStore(p.report);
</script>

<script lang="ts">
// export default {
//   components: {
//     GridGenerator,
//   }
// }
</script>

<template>
  <div>
    {{ JSON.stringify(store.state.report) }}
  </div>
</template>
