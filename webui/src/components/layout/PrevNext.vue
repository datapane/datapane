<script setup lang="ts">
import { defineEmits } from "vue";
const p = defineProps<{ pageNumber: number; numPages: number }>();

const emit = defineEmits(["page-change"]);

const scrollToTop = () => {
  document.body.scrollTop = document.documentElement.scrollTop = 0;
  const baseEl = document.getElementById("base-content");
  if (baseEl) {
    // Org embeds scroll on `#base-content` rather than body
    // TODO - Make Org embeds scroll on body (same as public embeds)
    baseEl.scrollTop = 0;
  }
};

const onPageChange = (pageNumber: number) => {
  emit("page-change", pageNumber);
  scrollToTop();
};

const nextPage = () => {
  p.pageNumber !== p.numPages - 1 && onPageChange(p.pageNumber + 1);
};

const prevPage = () => {
  p.pageNumber !== 0 && onPageChange(p.pageNumber - 1);
};
</script>

<template>
  <nav
    class="flex-initial border-t h-12 border-gray-200 px-4 flex items-center justify-between sm:px-0 mt-4"
  >
    <div class="-mt-px h-12 w-0 flex-1 flex">
      <a
        :class="[
          'border-t-2 h-12 border-transparent pl-2 pr-1 inline-flex items-center text-sm font-medium text-dp-light-gray',
          {
            'cursor-default opacity-40': p.pageNumber === 0,
            'cursor-pointer hover:text-dp-dark-gray hover:border-gray-300':
              p.pageNumber !== 0,
          },
        ]"
        @click="prevPage"
      >
        <svg
          class="mr-3 h-5 w-5 text-dp-light-gray"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
          aria-hidden="true"
        >
          <path
            fillRule="evenodd"
            d="M7.707 14.707a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l2.293 2.293a1 1 0 010 1.414z"
            clipRule="evenodd"
          />
        </svg>
        <div>Previous</div>
      </a>
    </div>
    <div
      class="hidden md:-mt-px md:flex text-sm text-dp-light-gray cursor-pointer"
      @click="scrollToTop"
    >
      Back to Top
    </div>
    <div class="-mt-px h-12 w-0 flex-1 flex justify-end items-center">
      <a
        @click="nextPage"
        :class="[
          'border-t-2 h-12 border-transparent pr-2 pl-1 inline-flex items-center text-sm font-medium text-dp-light-gray',
          {
            'cursor-default opacity-40': p.pageNumber === p.numPages - 1,
            'cursor-pointer hover:text-dp-dark-gray hover:border-gray-300':
              p.pageNumber !== p.numPages - 1,
          },
        ]"
      >
        <div>Next</div>
        <svg
          class="ml-3 h-5 w-5 text-dp-light-gray"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
          aria-hidden="true"
        >
          <path
            fillRule="evenodd"
            d="M12.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-2.293-2.293a1 1 0 010-1.414z"
            clipRule="evenodd"
          />
        </svg>
      </a>
    </div>
  </nav>
</template>
