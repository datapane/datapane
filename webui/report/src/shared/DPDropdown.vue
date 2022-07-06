<script setup lang="ts">
import { Section } from "./shared";
import { ref } from "vue";

const p = defineProps<{
    name: string;
    sections: Section[];
    orientation?: "left" | "right";
}>();

const open = ref(false);

const toggleOpen = () => void (open.value = !open.value);
const closeWithDelay = () => void setTimeout(() => (open.value = false), 200);
</script>

<template>
    <div
        :data-cy="`dropdown-${p.name.toLowerCase()}`"
        :style="{ zIndex: 5 }"
        class="relative inline-block text-left"
    >
        <div>
            <button
                type="button"
                class="dp-btn-sm px-1 sm:px-2 sm:px-2 py-0"
                id="options-menu"
                @click="toggleOpen"
                @blur="closeWithDelay"
            >
                {{ p.name }}
                <svg
                    class="-mr-1 ml-1 h-5 w-5"
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                    aria-hidden="true"
                >
                    <path
                        fillRule="evenodd"
                        d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                        clipRule="evenodd"
                    />
                </svg>
            </button>
        </div>

        <div
            :class="[
                'absolute  w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 divide-y divide-gray-100',
                {
                    hidden: !open,
                    'origin-top-left left-0': p.orientation === 'left',
                    'origin-top-right right-0': p.orientation !== 'left',
                },
            ]"
            role="menu"
            aria-orientation="vertical"
            aria-labelledby="options-menu"
        >
            <div
                v-for="(section, sectionIdx) in p.sections"
                class="py-1"
                :key="sectionIdx"
            >
                <div
                    v-if="section.title"
                    class="text-xs pl-2 py-2 font-semibold"
                >
                    {{ section.title }}
                </div>
                <a
                    v-for="(option, optionIdx) in section.options"
                    :key="`${sectionIdx}-${optionIdx}`"
                    :data-cy="`dropdown-option-${option.id}`"
                    :id="option.id"
                    @click="option.onClick"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900 cursor-pointer"
                    role="menuitem"
                >
                    {{ option.name }}
                </a>
            </div>
        </div>
    </div>
</template>
