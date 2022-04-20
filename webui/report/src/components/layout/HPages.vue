<script setup lang="ts">
import { defineEmits } from "vue";

const p = defineProps<{ labels: string[]; pageNumber: number }>();

const emit = defineEmits(["page-change"]);
</script>

<template>
    <div class="border-b border-gray-200">
        <nav class="-mb-px flex justify-items-stretch" aria-label="Tabs">
            <a
                v-for="(label, idx) in p.labels"
                :key="idx"
                :data-cy="`page-${idx}`"
                :class="[
                    'flex-1 p-2 text-center border-b-2 font-medium text-sm cursor-pointer',
                    {
                        'text-dp-accent border-dp-accent': idx === p.pageNumber,
                        'border-transparent text-dp-light-gray hover:text-dp-dark-gray hover:border-gray-300':
                            idx !== p.pageNumber,
                    },
                ]"
                @click="emit('page-change', idx)"
            >
                {{ label }}
            </a>
        </nav>
    </div>
</template>
