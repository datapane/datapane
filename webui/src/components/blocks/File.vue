<script setup lang="ts">
import DpButton from "../../shared/DPButton.vue";

const p = defineProps<{
    downloadFile: () => Promise<void>;
    filename: string;
}>();
</script>

<template>
    <div class="w-full p-4 bg-gray-50 shadow" data-cy="block-file">
        <div class="flex items-center">
            <svg
                class="flex-shrink-0 h-5 w-5 mr-2 text-gray-400"
                x-description="Heroicon name: solid/paper-clip"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
                aria-hidden="true"
            >
                <path
                    fill-rule="evenodd"
                    clip-rule="evenodd"
                    d="M8 4a3 3 0 00-3 3v4a5 5 0 0010 0V7a1 1 0 112 0v4a7 7 0 11-14 0V7a5 5 0 0110 0v4a3 3 0 11-6 0V7a1 1 0 012 0v4a1 1 0 102 0V7a3 3 0 00-3-3z"
                />
            </svg>
            <span class="text-base">{{ p.filename }}</span>
            <div class="ml-auto">
                <dp-button icon="fa fa-download" @click="p.downloadFile">
                    Download
                </dp-button>
            </div>
        </div>
    </div>
</template>
