<script setup lang="ts">
const p = defineProps<{ error: string }>();
</script>

<template>
    <div class="bg-red-100 p-4 mt-4">
        <h3 class="flex justify-start items-center">
            <i class="fa fa-exclamation-circle mr-1" />
            <div>Something went wrong</div>
        </h3>
        <p>{{ p.error }}</p>
    </div>
</template>
