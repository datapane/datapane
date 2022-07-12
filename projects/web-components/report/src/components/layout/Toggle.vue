<script setup lang="ts">
import { ref } from "vue";
const p = defineProps<{ label?: string }>();
const isOpen = ref(false);
</script>

<template>
    <div class="w-full bg-gray-100 p-2 rounded-md" data-cy="section-toggle">
        <div
            class="cursor-pointer px-2 w-full font-semibold flex items-center justify-start"
            @click="isOpen = !isOpen"
        >
            <div class="flex-1">
                {{ p.label || "Toggle Section" }}
            </div>
            <div class="flex-initial ml-auto">
                <i
                    :class="[
                        'opacity-50 fa',
                        { 'fa-chevron-up': isOpen, 'fa-chevron-down': !isOpen },
                    ]"
                />
            </div>
        </div>
        <div
            :class="['w-full pt-2 m-auto overflow-hidden', { hidden: !isOpen }]"
        >
            <slot />
        </div>
    </div>
</template>
