import { defineStore } from "pinia";
import {
    Block,
    Group,
    isLayoutBlock,
    PageLayout,
    Select,
} from "./blocks/index";
import { v4 as uuid4 } from "uuid";
import { computed, reactive, ref } from "vue";
import { useRootStore } from "./root-store";
import { SwapType } from "./types";

const cleanParam = (v: string) => {
    if ((typeof v === "string" || Array.isArray(v)) && !v.length) {
        return undefined;
    }
    return v;
};

const mkInitialParams = (initialChildren: Block[]): any => {
    const params: any = {};
    for (const c of initialChildren) {
        params[c.componentProps.name] = cleanParam(c.componentProps.initial);
    }
    return params;
};

const useActions = (initialChildren: Block[]) => {
    const children = reactive(initialChildren);
    const tabNumber = ref(0);

    function prepend(this: any, group: Group) {
        this.$patch(() => {
            children.unshift(...group.children);
            tabNumber.value += group.children.length;
        });
    }

    function append(this: any, group: Group) {
        this.$patch(() => {
            children.push(...group.children);
            tabNumber.value -= Math.min(group.children.length, 0);
        });
    }

    function replace(this: any, idx: number, group: Group) {
        this.$patch(() => {
            if (!group.id) {
                // If the `Group` block to replace has no ID, set it to the target block's ID
                group.id = children[idx].id;
            }
            children.splice(idx, 1, group);
        });
    }

    function inner(this: any, idx: number, group: Group) {
        const targetChild = children[idx];

        if (!isLayoutBlock(targetChild)) {
            throw new Error("Can't perform inner replace on non layout block");
        }

        this.$patch(() => {
            targetChild.children.splice(
                0,
                targetChild.children.length,
                ...group.children,
            );
            tabNumber.value = 0;
        });
    }

    function setTab(this: any, n: number) {
        this.tabNumber = n;
    }

    function load(this: any, children: Block[]) {
        this.children = children;
    }

    return {
        children,
        tabNumber,
        prepend,
        append,
        replace,
        setTab,
        load,
        inner,
    };
};

export const useLayoutStore = (initialChildren: Block[]) =>
    defineStore(`layout-${uuid4()}`, () => {
        return useActions(initialChildren);
    });

export const useViewStore = (
    initialChildren: Block[],
    initialLayout?: PageLayout,
) =>
    defineStore(`view-${uuid4()}`, () => {
        const actions = useActions(initialChildren);
        const { children } = actions;
        const _layout = ref(initialLayout);

        const hasPages = computed(
            () => children.length === 1 && children[0] instanceof Select,
        );

        const layout = computed(
            () => _layout.value || (children.length > 5 ? "side" : "top"),
        );

        return { ...actions, hasPages, layout };
    });

export const useControlStore = (
    initialChildren: Block[],
    target: string,
    method: SwapType,
) =>
    defineStore(`controls-${uuid4()}`, () => {
        const initialParams = mkInitialParams(initialChildren);
        const children = reactive(initialChildren);
        const parameters = reactive(initialParams);
        const rootStore = useRootStore();

        const setField = (k: string, v: any) => {
            parameters[k] = cleanParam(v);
        };

        const update = async (functionId: string) =>
            await rootStore.update(target, method, parameters, functionId);

        return { children, setField, update };
    });
