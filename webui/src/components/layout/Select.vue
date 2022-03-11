<script setup lang="ts">
import { ref } from "vue";
import { BlockTree, Select } from "../../data-model/blocks";
import GridGenerator from "../GridGenerator.vue";
import "vue-multiselect/dist/dist/vue-multiselect.esm.css";

const p = defineProps<{ select: Select }>();

const tabNumber = ref(0);

const labels: string[] = p.select.children.map(
  (child: BlockTree, idx) => child.label || `Section ${idx + 1}`
);

const getSectionType = (): string => {
  const { type, children } = p.select;
  if (type) return type;
  return children.length < 5 ? "tabs" : "dropdown";
};

const setTabNumber = (val: number) => (tabNumber.value = val);

const sectionType = getSectionType();
const selectSearchOptions = labels.map((label, idx) => ({
  text: label,
  value: idx,
}));

const tabNumbers = labels.map((_, idx) => idx);
</script>

<template>
  <div class="w-full" data-cy="section-tabs">
    <div :class="['w-full mb-2', { 'sm:hidden': sectionType === 'tabs' }]">
      <select
        v-if="p.select.children.length < 10"
        id="tabs"
        name="tabs"
        class="block mb-1 w-auto focus:ring-indigo-500 focus:border-indigo-500 border-gray-300 rounded-md"
        :value="tabNumber"
        @change="(ev) => setTabNumber(+ev.target.value)"
      >
        <option v-for="(label, idx) in labels" :key="idx" :value="idx">
          {{ label }}
        </option>
      </select>
      <MultiSelect
        v-else
        v-model="tabNumber"
        :options="tabNumbers"
        :preselect-first="true"
        :clear-on-select="false"
        :allow-empty="false"
        :custom-label="(tabNumber) => labels[tabNumber]"
      />
    </div>
    <div :class="['hidden', { 'sm:block': sectionType === 'tabs' }]">
      <nav class="flex space-x-4 mb-2">
        <a
          v-for="(child, idx) in p.select.children"
          role="button"
          :key="idx"
          :data-cy="`tab-${idx}`"
          :class="[
            'px-3 py-2 font-medium text-sm rounded-md',
            {
              'text-dp-accent bg-dp-accent-light': tabNumber === idx,
              'text-dp-light-gray hover:text-dp-dark-gray': tabNumber !== idx,
            },
          ]"
          @click="() => setTabNumber(idx)"
        >
          {{ labels[idx] }}
        </a>
      </nav>
    </div>
    <div>
      <GridGenerator :tree="p.select.children[tabNumber]" />
    </div>
  </div>
</template>

<script lang="ts">
import MultiSelect from "vue-multiselect";

export default {
  components: {
    GridGenerator,
    MultiSelect,
  },
};
</script>

<style>
.multiselect__option--highlight {
  background: var(--dp-accent-color);
  color: var(--dp-accent-text);
}

.multiselect__option--selected.multiselect__option--highlight {
  background: white;
  color: black;
}

.multiselect__option--highlight:after {
  display: none;
}

.multiselect__option--highlight.multiselect__option--selected {
  background: var(--dp-accent-color);
  color: var(--dp-accent-text);
}
</style>
