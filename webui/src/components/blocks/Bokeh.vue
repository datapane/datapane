<script setup lang="ts">
import { watch, onUnmounted, inject } from "vue";
import { v4 as uuid4 } from "uuid";
import * as Bokeh from "@bokeh/bokehjs";

const docIds: any[] = [];
const divId = uuid4();

// TODO - use enum
const singleBlockEmbed = inject("singleBlockEmbed");

const p = defineProps<{ plotJson: any; responsive: boolean }>();

const makeResponsive = (json: any) => {
  const plotJson = json.doc.roots.references.find(
    (r: any) => r.type === "Plot"
  );
  if (plotJson) {
    plotJson.attributes.sizing_mode = singleBlockEmbed
      ? "stretch_both"
      : "stretch_width";
  }
};

onUnmounted(() => {
  // cleanup -- https://github.com/bokeh/bokeh/issues/5355#issuecomment-423580351
  for (const doc of Bokeh.documents) {
    for (const docTimestamp of docIds) {
      // Remove any global Documents by checking their uuids
      if ((doc as any).uuid === docTimestamp) {
        doc.clear();
        const i = Bokeh.documents.indexOf(doc);
        if (i > -1) {
          Bokeh.documents.splice(i, 1);
        }
      }
    }
  }
});

watch(
  () => p.plotJson,
  () => {
    if (p.plotJson && p.plotJson !== {}) {
      try {
        p.responsive && makeResponsive(p.plotJson);
        Bokeh.embed
          .embed_item(p.plotJson as any, divId)
          .then((plotViews: any) => {
            // Generate uuids for Bokeh Documents so they can be referenced on dismount
            plotViews.forEach((pv: any) => {
              const docId = uuid4();
              (pv.model.document as any).uuid = docId;
              docIds.push(docId);
            });
          });
      } catch (e) {
        console.error("An error occurred while rendering a Bokeh chart");
      }
    }
  },
  { immediate: true }
);
</script>

<template>
  <div
    data-cy="block-bokeh"
    :id="divId"
    :class="[
      'bk-root m-auto flex justify-center items-center w-full',
      { 'w-full': p.responsive, 'h-iframe': singleBlockEmbed },
    ]"
  />
</template>
