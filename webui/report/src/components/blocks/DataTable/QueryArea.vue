<script setup lang="ts">
import { defineEmits, onMounted, ref } from "vue";
import DpButton from "../../../shared/DPButton.vue";
import "codemirror/mode/sql/sql.js";
import "codemirror/addon/display/autorefresh.js";
import CodeMirror from "codemirror";

const p = defineProps<{
    initialQuery: string;
    errors?: string;
}>();

const CM_OPTIONS = {
    theme: "eclipse",
    mode: "sql",
    lineNumbers: false,
    autoRefresh: true,
};

const emit = defineEmits(["query-change", "run-query", "clear-query"]);
const cmEl = ref<HTMLTextAreaElement>();
const cmInstance = ref<any>();

const emitQueryChange = (query: string) => void emit("query-change", query);

onMounted(() => {
    if (cmEl.value) {
        // Set up codemirror instance on mount
        cmInstance.value = CodeMirror.fromTextArea(cmEl.value, CM_OPTIONS);
        cmInstance.value.on("change", (doc: any) => {
            // Keep CM editor in sync with DataTable query ref
            emitQueryChange(doc.getValue());
        });
        emitQueryChange(cmInstance.value.getValue());
    } else {
        console.error("Couldn't find codemirror textarea element");
    }
});
</script>

<template>
    <div class="h-48 flex flex-col justify-start border-b border-gray-200">
        <div class="flex flex-col flex-fixed h-full query-container">
            <textarea ref="cmEl" :value="p.initialQuery" />
            <div class="flex justify-start flex-fixed my-2 px-2">
                <dp-button
                    @click="emit('run-query')"
                    icon="fa fa-play"
                    data-cy="btn-run-query"
                    class="w-28 dp-btn-primary"
                >
                    Run Query
                </dp-button>
                <dp-button
                    @click="emit('clear-query')"
                    icon="fa fa-undo"
                    class="ml-2 w-28 dp-btn-secondary-gray"
                    data-cy="btn-reset-data"
                >
                    Reset Data
                </dp-button>
            </div>
        </div>
    </div>
    <div v-if="p.errors" class="w-full bg-red-100" data-cy="alasql-error-msg">
        {{ p.errors }}
    </div>
</template>
