<script setup lang="ts">
import { withDefaults } from "vue";
import { DPClipboard } from "../../shared/DPClipboard";

const p = withDefaults(
    defineProps<{ inline: boolean; title: string; content: string }>(),
    { inline: true },
);

const copy = () => {
    DPClipboard.copyOnce(p.content);
};
</script>

<template>
    <link rel="stylesheet" href="/static/base/style.css" />
    <div class="text-gray-500 pt-2">{{ p.title }}</div>
    <div>
        <div class="mt-2 flex rounded-md shadow-sm">
            <div
                class="relative flex-grow max-w-full h-10 focus-within:z-10 border border-gray-300 pl-2 flex items-center rounded-md bg-white"
            >
                <pre
                    class="font-mono form-input block truncate w-full transition ease-in-out duration-150 sm:text-md sm:leading-5 border-0"
                >
              {{ p.content }}
          </pre
                >
                <span>
                    <button
                        @click="copy"
                        :class="[
                            'justify-center dp-btn dp-btn-info -ml-px relative inline-flex items-center',
                            {
                                'rounded-l-none border-none': p.inline,
                                'w-full': !p.inline,
                            },
                        ]"
                    >
                        <svg
                            class="h-5 w-5"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                        >
                            <title>Copy</title>
                            <path
                                d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z"
                            ></path>
                            <path
                                d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z"
                            ></path>
                        </svg>
                        <span class="pl-2" v-if="!p.inline">Copy</span>
                    </button>
                </span>
            </div>
        </div>
    </div>
</template>
