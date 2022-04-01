<script setup lang="ts">
import { defineEmits } from "vue";
import dpbutton from "../../../shared/DPButton.vue";
import codemirror from "codemirror-editor-vue3";
import "codemirror/lib/codemirror.css";
import "codemirror/mode/sql/sql.js";
import "codemirror/theme/eclipse.css";

const p = defineProps<{
    query: string;
}>();

const emit = defineEmits(["query-change", "run-query", "clear-query"]);

const cmOptions = {
    theme: "eclipse",
    mode: "sql",
    lineNumbers: false,
};

const onQueryChange = (query: string) => emit("query-change", query);
</script>

<template>
    <div class="h-48 flex flex-col justify-start border-b border-gray-200">
        <div class="flex flex-col flex-fixed h-full query-container">
            <codemirror
                :value="p.query"
                :options="cmOptions"
                @change="onQueryChange"
            />
            <div class="flex justify-start flex-fixed my-2 px-2">
                <dpbutton
                    @click="emit('run-query')"
                    :disabled="!p.query"
                    icon="fa fa-play"
                    data-cy="btn-run-query"
                    class="w-28 dp-btn-primary"
                >
                    Run Query
                </dpbutton>
                <dpbutton
                    @click="emit('clear-query')"
                    icon="fa fa-undo"
                    class="ml-2 w-28 dp-btn-secondary-gray"
                    data-cy="btn-reset-data"
                >
                    Reset Data
                </dpbutton>
            </div>
        </div>
    </div>
</template>

<style>
.query-container .CodeMirror {
    font-size: 18px;
    font-family: monospace !important;
}
</style>
