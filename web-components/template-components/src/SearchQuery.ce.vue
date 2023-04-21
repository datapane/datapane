<script setup lang="ts">
import { ref } from "vue";
import { serializeSlotJson } from "./template-utils";

type Choices = { value: string; text: string }[];

const p = defineProps<{
    searchPlaceholder: string;
}>();

const loadChoicesJson = (node: any) => {
    choices.value = serializeSlotJson<Choices>(node);
};

const getUrlParams = (name: string): string[] => {
    const params = [];
    for (const [k, v] of new URLSearchParams(location.search)) {
        name === k && params.push(v ? decodeURIComponent(v) : "");
    }
    return params;
};

const getUrlParam = (name: string): string => {
    const params = getUrlParams(name);
    return params.length > 0 ? params[0] : "";
};

const ownedByMe = ref<boolean>(getUrlParam("owned_by_me") === "on");
const project = ref<string>(getUrlParam("project"));
const name = ref<string>(getUrlParam("name"));
const showFilter = ref<boolean>(!!project.value || ownedByMe.value || false);
const choices = ref<Choices>();

const toggleFilter = () => (showFilter.value = !showFilter.value);
</script>

<template>
    <link rel="stylesheet" href="/static/base/style.css" />
    <slot name="choices-data" :ref="loadChoicesJson" />
    <form method="get" class="w-full" data-component-name="app_list_form">
        <div class="w-full">
            <div
                class="relative z-10 flex-shrink-0 h-16 bg-white border-b border-gray-200 shadow-sm flex"
            >
                <div class="flex-1 flex justify-between px-4 sm:px-6">
                    <div class="flex-1 flex">
                        <div class="w-full flex md:ml-0">
                            <div
                                class="relative w-full text-gray-400 focus-within:text-gray-600"
                            >
                                <div
                                    class="pointer-events-none absolute inset-y-0 left-0 flex items-center"
                                >
                                    <svg
                                        class="flex-shrink-0 h-5 w-5"
                                        x-description="Heroicon name: solid/search"
                                        xmlns="http://www.w3.org/2000/svg"
                                        viewBox="0 0 20 20"
                                        fill="currentColor"
                                        aria-hidden="true"
                                    >
                                        <path
                                            fill-rule="evenodd"
                                            d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
                                            clip-rule="evenodd"
                                        ></path>
                                    </svg>
                                </div>
                                <input
                                    name="name"
                                    :value="name"
                                    id="id_name"
                                    class="h-full w-full border-transparent py-2 pl-8 pr-3 text-base text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-0 focus:border-transparent focus:placeholder-gray-400 sm:block"
                                    :placeholder="p.searchPlaceholder"
                                    type="search"
                                />
                            </div>
                        </div>
                    </div>
                    <div
                        class="ml-2 flex items-center space-x-4 sm:ml-6 sm:space-x-6"
                    >
                        <button
                            type="button"
                            @click="toggleFilter"
                            class="justify-center px-3.5 py-2 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                        >
                            <svg
                                class="h-5 w-5 text-gray-400"
                                x-description="Heroicon name: solid/filter"
                                xmlns="http://www.w3.org/2000/svg"
                                viewBox="0 0 20 20"
                                fill="currentColor"
                                aria-hidden="true"
                            >
                                <path
                                    fill-rule="evenodd"
                                    d="M3 3a1 1 0 011-1h12a1 1 0 011 1v3a1 1 0 01-.293.707L12 11.414V15a1 1 0 01-.293.707l-2 2A1 1 0 018 17v-5.586L3.293 6.707A1 1 0 013 6V3z"
                                    clip-rule="evenodd"
                                ></path>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
            <div
                class="bg-gray-100 p-3 w-full flex items-center"
                v-show="showFilter"
            >
                <div class="flex items-center mr-4">
                    <input
                        type="checkbox"
                        name="owned_by_me"
                        class="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                        id="id_owned_by_me"
                        :checked="ownedByMe"
                        onchange="this.form.submit()"
                    />
                    <label
                        for="id_owned_by_me"
                        class="block text-gray-700 text-sm ml-1"
                    >
                        Created by me
                    </label>
                </div>
                <div class="flex items-center">
                    <select
                        :value="project"
                        onchange="this.form.submit()"
                        class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                        name="project"
                    >
                        <option
                            v-for="(choice, idx) in choices"
                            :key="idx"
                            :value="choice.value"
                        >
                            {{ choice.text }}
                        </option>
                    </select>
                </div>
            </div>
        </div>
    </form>
</template>
