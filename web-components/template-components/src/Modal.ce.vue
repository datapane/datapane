<script setup lang="ts">
import { ref } from "vue";

const openInitial = new URLSearchParams(document.location.search).has("invite");
const open = ref<boolean>(openInitial);
</script>

<template>
    <link rel="stylesheet" href="/static/base/style.css" />
    <slot name="trigger" @click="open = true" />
    <div
        v-show="open"
        data-cy="modal-component"
        class="modal-component fixed bottom-0 inset-x-0 px-4 pb-4 sm:inset-0 sm:flex sm:items-center sm:justify-center z-50"
        style="display: none"
    >
        <div v-show="open" class="fixed inset-0 transition-opacity">
            <div
                @click="open = false"
                class="absolute inset-0 bg-gray-500 opacity-75"
            ></div>
        </div>

        <div
            v-show="open"
            style="max-height: 40em"
            class="text-left relative bg-white rounded-lg px-4 pt-5 pb-4 overflow-x-hidden overflow-y-auto shadow-xl transform transition-all sm:max-w-2xl sm:w-full sm:p-6"
        >
            <div class="hidden sm:block absolute top-0 right-0 pt-5 pr-4">
                <button
                    @click="open = false"
                    type="button"
                    class="text-gray-400 hover:text-gray-500 focus:outline-none focus:text-gray-500 transition ease-in-out duration-150"
                >
                    <svg
                        class="h-6 w-6"
                        stroke="currentColor"
                        fill="none"
                        viewBox="0 0 24 24"
                    >
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M6 18L18 6M6 6l12 12"
                        />
                    </svg>
                </button>
            </div>

            <div class="sm:flex sm:items-center mb-1">
                <div class="mt-3 sm:mt-0 sm:text-left">
                    <div class="flex items-center">
                        <h3
                            class="text-lg leading-6 font-medium text-gray-900 pb-1"
                        >
                            <slot name="title" />
                        </h3>
                    </div>
                </div>
            </div>
            <div class="mt-3 w-full">
                <div class="text-sm leading-5 text-gray-500">
                    <slot />
                </div>
            </div>
            <div class="mt-4 flex" style="flex-direction: row-reverse">
                <slot name="buttons">
                    <slot name="action" />
                    <div class="mt-3 sm:mt-0">
                        <button
                            @click="open = false"
                            type="button"
                            class="dp-btn dp-btn-info mr-3"
                        >
                            Close
                        </button>
                    </div>
                </slot>
            </div>
        </div>
    </div>
</template>
