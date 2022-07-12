<script setup lang="ts">
import { createInput } from "@formkit/vue";
import ListFieldView from "./ListFieldView.vue";
import { computed, ComputedRef, reactive, ref, toRef, watch } from "vue";

const p = defineProps<{
    value: string[];
    helpText?: string;
    name: string;
    required?: boolean;
    setValue: any;
}>();

const tags = reactive(p.value);
const el = ref<any>();

const required = (node: any) => {
    return node.props.tagCount > 0;
};

const validation: ComputedRef = computed(() =>
    p.required ? [["+required"]] : []
);

watch(
    () => tags,
    () => p.setValue(tags),
    { deep: true }
);

const listFieldInput = createInput(ListFieldView, {
    props: ["tags", "tagCount"],
});

const setListeners = (node: any) => {
    node.on("newTag", ({ payload }: any) => {
        tags.push(payload);
    });
};

const removeTag = (idx: number) => {
    tags.splice(idx, 1);
};
</script>

<template>
    <div :data-cy="`list-field-${p.name}`">
        <form-kit
            :type="listFieldInput"
            :label="p.name"
            :name="p.name"
            :help="p.helpText"
            :validation="validation"
            validation-visibility="live"
            :validation-rules="{ required }"
            :tag-count="tags.length"
            ref="el"
            @node="setListeners"
        />
        <div
            class="bg-indigo-100 inline-flex items-center text-sm rounded mb-4 mr-2"
            v-for="(tag, idx) in tags"
            :key="idx"
        >
            <span class="ml-2 mr-1 leading-relaxed truncate max-w-xs">{{
                tag
            }}</span>
            <button
                class="w-6 h-8 inline-block align-middle text-gray-500 hover:text-gray-600 focus:outline-none"
                @click="removeTag(idx)"
            >
                <svg
                    class="w-6 h-6 fill-current mx-auto"
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                >
                    <path
                        fill-rule="evenodd"
                        d="M15.78 14.36a1 1 0 0 1-1.42 1.42l-2.82-2.83-2.83 2.83a1 1 0 1 1-1.42-1.42l2.83-2.82L7.3 8.7a1 1 0 0 1 1.42-1.42l2.83 2.83 2.82-2.83a1 1 0 0 1 1.42 1.42l-2.83 2.83 2.83 2.82z"
                    />
                </svg>
            </button>
        </div>
    </div>
</template>
