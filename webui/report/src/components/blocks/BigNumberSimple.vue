<script setup lang="ts">
const p = defineProps<{
    heading: string;
    value: string;
}>();
</script>

<template>
    <div
        data-cy="block-bignumber"
        class="bg-white overflow-hidden border border-gray-300 rounded-lg w-full"
    >
        <div class="px-4 py-5 sm:p-6">
            <dl>
                <dt
                    class="text-sm leading-5 font-medium text-gray-500 truncate"
                >
                    {{ p.heading }}
                </dt>
                <dd class="mt-1 text-3xl leading-9 font-semibold text-gray-900">
                    {{ p.value }}
                </dd>
            </dl>
        </div>
    </div>
</template>
