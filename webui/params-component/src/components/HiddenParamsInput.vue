<script setup lang="ts">
/**
 * Stores the serialized params in a hidden form field that's POSTed to the server on run
 */
import { paramsStore } from "../data-model/params-store";
</script>

<template>
    <Observer>
        <input
            type="hidden"
            name="parameter_vals"
            form="params-form"
            :value="JSON.stringify(paramsStore.serialized) || ''"
        />
    </Observer>
</template>
