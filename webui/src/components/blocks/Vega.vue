<script setup lang="ts">
import { onUnmounted, inject, onMounted } from "vue";
import vegaEmbed from "vega-embed";
import { Result } from "vega-embed";
import { v4 as uuid4 } from "uuid";

const divId = `vega_${uuid4()}`;
let vegaView: Result | undefined;

const p = defineProps<{ plotJson: any; responsive: boolean }>();

const singleBlockEmbed = inject("singleBlockEmbed");

const makeResponsive = (json: any) => {
  json.width = "container";
  if (singleBlockEmbed) {
    json.height = "container";
  }
};

const adjustHeightFromBindings = () => {
  /**
   * Prevents the vega-bindings element from being cut off in single block embed mode
   */
  const plotEl: HTMLElement | null = document.getElementById(divId);
  const bindingEl: HTMLElement | null =
    plotEl && plotEl.querySelector<HTMLElement>(".vega-bindings");
  const canvasEl: HTMLElement | null = plotEl && plotEl.querySelector("canvas");
  if (canvasEl && bindingEl) {
    canvasEl.style.height = `${
      canvasEl.offsetHeight - bindingEl.offsetHeight
    }px`;
  }
};

const addPlotToDom = async () => {
  try {
    p.responsive && makeResponsive(p.plotJson);
    const view = await vegaEmbed(`#${divId}`, p.plotJson, {
      mode: "vega-lite",
      actions: false, // disable the altair action menu
    });
    vegaView = view;
    singleBlockEmbed && adjustHeightFromBindings();
  } catch (e) {
    console.error("An error occurred while rendering an Altair chart: ", e);
  }
};

onMounted(() => {
  addPlotToDom();
});

onUnmounted(() => void vegaView?.finalize());
</script>

<template>
  <div
    :class="[
      'm-auto justify-center bg-white flex',
      { 'w-full': p.responsive, 'h-iframe': singleBlockEmbed },
    ]"
  >
    <!-- Vega bindings don't display correctly when setting `flex` directly on the vega element,
            so wrap it in a flex container and apply `dimensionClasses` twice -->
    <div
      :id="divId"
      :class="{ 'w-full': p.responsive, 'h-iframe': singleBlockEmbed }"
      data-cy="block-vega"
    />
  </div>
</template>
