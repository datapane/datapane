<script setup lang="ts">
import { ref } from "vue";

const initialStep = parseInt(localStorage.getItem("datapane-tut-stage")) || 1;
const currentStep = ref(initialStep);
const steps = [
    {
        number: 1,
        id: "01",
        name: "Get the client library",
        description: "Install Datapane",
    },
    {
        number: 2,
        id: "02",
        name: "Login to Datapane",
        description: "Login with your API key",
    },
    {
        number: 3,
        id: "03",
        name: "Create a report",
        description: "Upload a report using Python",
    },
];

const changeStep = (step: number) => {
    localStorage.setItem("datapane-tut-stage", `${step}`);
    currentStep.value = step;
};

const resetStep = () => {
    localStorage.removeItem("datapane-tut-stage");
};
</script>

<template>
    <link rel="stylesheet" href="/static/base/style.css" />
    <div class="bg-white mt-2">
        <div>
            <div class="lg:border-t lg:border-b lg:border-gray-200">
                <nav class="mx-auto max-w-7xl" aria-label="Progress">
                    <ol
                        role="list"
                        class="rounded-md overflow-hidden lg:flex lg:border-l lg:border-r lg:border-gray-200 lg:rounded-none"
                    >
                        <template
                            v-for="(step, stepIdx) in steps"
                            :key="step.id"
                        >
                            <li class="relative overflow-hidden lg:flex-1">
                                <div
                                    :class="[
                                        stepIdx === 0
                                            ? 'border-b-0 rounded-t-md'
                                            : '',
                                        stepIdx === steps.length - 1
                                            ? 'border-t-0 rounded-b-md'
                                            : '',
                                        'border border-gray-200 overflow-hidden lg:border-0',
                                    ]"
                                >
                                    <template v-if="currentStep > step.number">
                                        <a
                                            href="#"
                                            @click="changeStep(step.number)"
                                            class="group"
                                        >
                                            <span
                                                class="absolute top-0 left-0 w-1 h-full bg-transparent group-hover:bg-gray-200 lg:w-full lg:h-1 lg:bottom-0 lg:top-auto"
                                                aria-hidden="true"
                                            ></span>
                                            <span
                                                :class="[
                                                    stepIdx !== 0
                                                        ? 'lg:pl-9'
                                                        : '',
                                                    'px-6 py-5 flex items-start text-sm font-medium',
                                                ]"
                                            >
                                                <span class="flex-shrink-0">
                                                    <span
                                                        class="w-10 h-10 flex items-center justify-center bg-indigo-600 rounded-full"
                                                    >
                                                        <svg
                                                            class="w-6 h-6 text-white"
                                                            x-description="Heroicon name: solid/check"
                                                            xmlns="http://www.w3.org/2000/svg"
                                                            viewBox="0 0 20 20"
                                                            fill="currentColor"
                                                            aria-hidden="true"
                                                        >
                                                            <path
                                                                fill-rule="evenodd"
                                                                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                                                clip-rule="evenodd"
                                                            ></path>
                                                        </svg>
                                                    </span>
                                                </span>
                                                <span
                                                    class="mt-0.5 ml-4 min-w-0 flex flex-col"
                                                >
                                                    <span
                                                        class="text-xs font-semibold tracking-wide uppercase"
                                                        v-text="step.name"
                                                    ></span>
                                                    <span
                                                        class="text-sm font-medium text-gray-500"
                                                        v-text="
                                                            step.description
                                                        "
                                                    ></span>
                                                </span>
                                            </span>
                                        </a>
                                    </template>
                                    <template
                                        v-if="currentStep === step.number"
                                    >
                                        <a
                                            href="#"
                                            @click="changeStep(step.number)"
                                            aria-current="step"
                                        >
                                            <span
                                                class="absolute top-0 left-0 w-1 h-full bg-indigo-600 lg:w-full lg:h-1 lg:bottom-0 lg:top-auto"
                                            ></span>

                                            <span
                                                :class="[
                                                    stepIdx !== 0
                                                        ? 'lg:pl-9'
                                                        : '',
                                                    'px-6 py-5 flex items-start text-sm font-medium',
                                                ]"
                                            >
                                                <span class="flex-shrink-0">
                                                    <span
                                                        class="w-10 h-10 flex items-center justify-center border-2 border-indigo-600 rounded-full"
                                                    >
                                                        <span
                                                            class="text-indigo-600"
                                                            v-text="step.id"
                                                        ></span>
                                                    </span>
                                                </span>
                                                <span
                                                    class="mt-0.5 ml-4 min-w-0 flex flex-col"
                                                >
                                                    <span
                                                        class="text-xs font-semibold text-indigo-600 tracking-wide uppercase"
                                                        v-text="step.name"
                                                    >
                                                    </span>
                                                    <span
                                                        class="text-sm font-medium text-gray-500"
                                                        v-text="
                                                            step.description
                                                        "
                                                    ></span>
                                                </span>
                                            </span>
                                        </a>
                                    </template>
                                    <template v-if="currentStep < step.number">
                                        <a
                                            href="#"
                                            @click="changeStep(step.number)"
                                            class="group"
                                        >
                                            <span
                                                class="absolute top-0 left-0 w-1 h-full bg-transparent group-hover:bg-gray-200 lg:w-full lg:h-1 lg:bottom-0 lg:top-auto"
                                                aria-hidden="true"
                                            ></span>
                                            <span
                                                :class="[
                                                    stepIdx !== 0
                                                        ? 'lg:pl-9'
                                                        : '',
                                                    'px-6 py-5 flex items-start text-sm font-medium',
                                                ]"
                                            >
                                                <span class="flex-shrink-0">
                                                    <span
                                                        class="w-10 h-10 flex items-center justify-center border-2 border-gray-300 rounded-full"
                                                    >
                                                        <span
                                                            class="text-gray-500"
                                                            v-text="step.id"
                                                        ></span>
                                                    </span>
                                                </span>
                                                <span
                                                    class="mt-0.5 ml-4 min-w-0 flex flex-col"
                                                >
                                                    <span
                                                        class="text-xs font-semibold text-gray-500 tracking-wide uppercase"
                                                        v-text="step.name"
                                                    ></span>
                                                    <span
                                                        class="text-sm font-medium text-gray-500"
                                                        v-text="
                                                            step.description
                                                        "
                                                    ></span>
                                                </span>
                                            </span>
                                        </a>
                                    </template>
                                    <template v-if="stepIdx !== 0">
                                        <!-- Separator -->
                                        <div
                                            class="hidden absolute top-0 left-0 w-3 inset-0 lg:block"
                                            aria-hidden="true"
                                        >
                                            <svg
                                                class="h-full w-full text-gray-300"
                                                viewBox="0 0 12 82"
                                                fill="none"
                                                preserveAspectRatio="none"
                                            >
                                                <path
                                                    d="M0.5 0V31L10.5 41L0.5 51V82"
                                                    stroke="currentcolor"
                                                    vector-effect="non-scaling-stroke"
                                                />
                                            </svg>
                                        </div>
                                    </template>
                                </div>
                            </li>
                        </template>
                    </ol>
                </nav>
            </div>
        </div>
        <template v-if="currentStep === 1">
            <div
                class="p-5 border-gray-200 border border-top-0 rounded-b-md shadow"
            >
                <slot name="step-1" />
                <div>
                    <div class="flex justify-end space-x-2 mt-6">
                        <a
                            target="_blank"
                            data-onboarding-docs="1"
                            href="https://docs.datapane.com/"
                            class="dp-btn dp-btn-info"
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                class="h-5 w-5 mr-1"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                            >
                                <path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    stroke-width="2"
                                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                                />
                            </svg>
                            Learn about installing
                        </a>

                        <button
                            type="button"
                            @click="changeStep(2)"
                            data-onboarding-next="1"
                            class="relative inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                class="h-5 w-5 mr-1"
                                viewBox="0 0 20 20"
                                fill="currentColor"
                            >
                                <path
                                    fill-rule="evenodd"
                                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                    clip-rule="evenodd"
                                />
                            </svg>
                            I've installed Datapane
                        </button>
                    </div>
                </div>
            </div>
        </template>
        <template v-if="currentStep === 2">
            <div
                class="p-5 border-gray-200 border border-top-0 rounded-b-md shadow"
            >
                <slot name="step-2" />
                <div class="flex justify-end space-x-2 mt-6">
                    <a
                        target="_blank"
                        data-onboarding-docs="2"
                        href="https://docs.datapane.com/"
                        class="dp-btn dp-btn-info"
                    >
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            class="h-5 w-5 mr-1"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                            />
                        </svg>
                        Learn about authentication
                    </a>

                    <button
                        type="button"
                        data-onboarding-next="2"
                        @click="changeStep(3)"
                        class="relative inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            class="h-5 w-5 mr-1"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                        >
                            <path
                                fill-rule="evenodd"
                                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                clip-rule="evenodd"
                            />
                        </svg>
                        I've logged in
                    </button>
                </div>
            </div>
        </template>

        <template v-if="currentStep === 3">
            <div
                class="p-5 border-gray-200 border border-top-0 rounded-b-md shadow"
            >
                <p
                    class="text-lg leading-7 text-gray-700 py-2 flex items-center"
                >
                    Run this code in your environment to create and upload a
                    Datapane report.
                </p>
                <div class="mt-2">
                    <slot name="step-3" />
                </div>
                <div class="flex justify-end space-x-2 mt-6">
                    <a
                        href="https://docs.datapane.com/"
                        target="_blank"
                        data-onboarding-docs="3"
                        class="dp-btn dp-btn-info"
                    >
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            class="h-5 w-5 mr-1"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                            />
                        </svg>
                        Learn about reports
                    </a>

                    <a
                        href="/reports"
                        data-onboarding-next="3"
                        @click="resetStep()"
                        class="relative inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            class="h-5 w-5 mr-1"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                        >
                            <path
                                fill-rule="evenodd"
                                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                clip-rule="evenodd"
                            />
                        </svg>
                        I've built my report
                    </a>
                </div>
            </div>
        </template>
    </div>
</template>
