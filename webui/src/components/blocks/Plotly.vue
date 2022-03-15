<script setup lang="ts">
import { inject, onMounted } from "vue";
import Plotly from "plotly.js-dist";
import { v4 as uuid4 } from "uuid";

const divId = `vega_${uuid4()}`;
const p = defineProps<{ plotJson: any; responsive: boolean }>();

const singleBlockEmbed = inject("singleBlockEmbed");

const PLOTLY_CONFIG: any = {
  displaylogo: false,
  responsive: true,
};

const PLOTLY_LAYOUT_DEFAULTS = {
  modebar: {
    orientation: "v",
  },
};

const makeResponsive = (json: any) => {
  const { layout } = json;
  if (layout) {
    delete layout.autosize;
    delete layout.width;
    if (singleBlockEmbed) {
      delete layout.height;
    }
  }
};

onMounted(() => {
  p.responsive && makeResponsive(p.plotJson);
  Plotly.newPlot(divId, {
    data: p.plotJson.data,
    layout: {
      ...PLOTLY_LAYOUT_DEFAULTS,
      ...p.plotJson.layout,
      autosize: p.responsive,
    },
    config: PLOTLY_CONFIG,
    frames: p.plotJson.frames || undefined,
  });
});
</script>

<template>
  <div
    data-cy="block-plotly"
    :class="[
      'bg-white m-auto flex justify-center',
      { 'w-full': p.responsive, 'h-iframe': singleBlockEmbed },
    ]"
  >
    <div :id="divId" class="w-full" />
  </div>
</template>
