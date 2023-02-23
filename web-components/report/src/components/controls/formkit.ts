import { createInput } from "@formkit/vue";
import MultiSelectBase from "./MultiSelectBase.vue";
import { generateClasses } from "@formkit/themes";

// Create some re-useable definitions because
// many input types are identical in how
// we want to style them.
const textClassification = {
    inner: "mt-1",
    outer: "w-full",
    input: `block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500
  focus:ring-indigo-500 sm:text-sm formkit-invalid:border-red-300 formkit-invalid:text-red-900
  formkit-invalid:placeholder-red-300`,
};

const boxClassification = {
    // fieldset: "w-full border border-gray-200 rounded-md px-2 pb-1",
    legend: "block text-sm font-medium text-gray-700 formkit-invalid:text-red-500",
    options: "space-y-2 mt-2",
    wrapper: "flex items-center mb-1 cursor-pointer",
    help: "text-sm text-gray-500 mt-0",
    input: "h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 ",
    inner: "mr-3 flex h-5 items-center",
    outer: "relative flex",
    label: "font-medium",
};

const buttonClassification = {
    wrapper: "mb-1",
    input: "bg-blue-500 hover:bg-blue-700 text-white text-sm font-normal py-3 px-5 rounded",
};

// export our definitions using our above
// templates and declare one-offs and
// overrides as needed.
export const formkitConfig = {
    inputs: {
        multiSelectField: createInput(MultiSelectBase, {
            props: ["tags", "options", "multiSelectProps"],
        }),
    },
    config: {
        classes: generateClasses({
            // the global key will apply to all inputs
            global: {
                label: "block text-sm font-medium text-gray-700 formkit-invalid:text-red-500",
                outer: "mb-6 formkit-disabled:opacity-50",
                help: "mt-2 text-sm text-gray-500",
                messages: "list-none p-0 mt-1 mb-0",
                message: "text-red-500 mb-1 text-xs",
            },
            button: buttonClassification,
            color: {
                label: "block mb-1 font-bold text-sm",
                input: "w-16 h-8 appearance-none cursor-pointer border border-gray-300 rounded-md mb-2 p-1",
            },
            date: textClassification,
            "datetime-local": textClassification,
            checkbox: boxClassification,
            email: textClassification,
            file: {
                label: "block mb-1 font-bold text-sm ",
                fileItem:
                    "flex items-center text-gray-800 mb-1 last:mb-0 text-sm px-4 pt-3 pb-4",
                fileItemIcon: "w-4 mr-2 shrink-0",
                fileList:
                    "shrink grow peer px-3 py-2 formkit-multiple:data-[has-multiple='true']:mb-6",
                fileName: "break-all grow text-ellipsis",
                fileRemove:
                    "flex items-center z-[2] ml-auto  hover:text-red-500 pl-2 peer-data-[has-multiple=true]:text-sm peer-data-[has-multiple=true]:text-blue-500 peer-data-[has-multiple=true]:ml-3 peer-data-[has-multiple=true]:mb-2 formkit-multiple:bottom-[0.15em] formkit-multiple:pl-0 formkit-multiple:ml-0 formkit-multiple:left-[1em] formkit-multiple:formkit-prefix-icon:left-[3.75em]",
                fileRemoveIcon: "block text-base w-3 relative z-[2] mr-2",
                inner: "mt-1 flex relative justify-center rounded-md border-2 border-dashed border-gray-300 ",
                input: "hidden",
            },
            month: textClassification,
            number: textClassification,
            password: textClassification,
            tagsField: {
                ...textClassification,
                input: `${textClassification.input}`,
                outer: `${textClassification.outer} mb-1`,
            },
            radio: {
                ...boxClassification,
                input: boxClassification.input.replace(
                    "rounded-sm",
                    "rounded-full",
                ),
            },
            range: {
                inner: "w-full flex items-center",
                input: "w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700",
            },
            search: textClassification,
            select: textClassification,
            submit: buttonClassification,
            tel: textClassification,
            text: textClassification,
            textarea: {
                ...textClassification,
                input: "block w-full h-32 px-3 border-none text-base text-gray-700 placeholder-gray-400 focus:shadow-outline",
            },
            time: textClassification,
            url: textClassification,
            week: textClassification,
            tags: textClassification,
        }),
    },
};
