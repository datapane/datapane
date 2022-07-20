<script setup lang="ts">
const p = defineProps<{ src: string; type: string }>();
</script>

<template>
    <div class="w-full flex items-center justify-center" data-cy="block-media">
        <video
            v-if="p.type.startsWith('video')"
            controls
            :src="p.src"
            width="800"
        ></video>
        <audio
            v-else-if="p.type.startsWith('audio')"
            controls
            :src="p.src"
            class="w-full"
        ></audio>
        <img
            v-else-if="p.type.startsWith('image')"
            :src="p.src"
            loading="lazy"
            class="mx-auto"
        />
        <div v-else>Media type not supported</div>
    </div>
</template>
