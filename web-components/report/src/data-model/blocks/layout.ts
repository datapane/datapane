import { useControlStore, useLayoutStore, useViewStore } from "../layout-store";
import { markRaw } from "vue";
import VGroup from "../../components/layout/Group.vue";
import VSelect from "../../components/layout/SelectBlock.vue";
import VToggle from "../../components/layout/Toggle.vue";
import { Block, BlockFigure } from "./leaf-blocks";
import VInteractive from "../../components/controls/Interactive.connector.vue";
import { ControlsField } from "./interactive";
import * as b from "./index";
import { SwapType } from "../types";

export abstract class LayoutBlock<T extends Block = Block> extends Block {
    public children: T[];
    public store: any;

    public constructor(elem: any, figure: BlockFigure) {
        super(elem, figure);
        const { children } = elem.attributes;
        this.children = children;
        this.store = useLayoutStore(this.children)();
        this.componentProps = { ...this.componentProps, store: this.store };
    }

    public update(target: string, group: b.Group, method: SwapType): boolean {
        /**
         * Update the block's children with the given group fragment at the
         * given target ID, if a matching child with ID is found.
         *
         * Returns `true` if the target child was found and updated.
         */
        if (
            this.id === target &&
            (method === SwapType.APPEND || method === SwapType.PREPEND)
        ) {
            this.insertAtEdge(group, method);
            return true;
        } else if (method === SwapType.REPLACE || method === SwapType.INNER) {
            return this.swap(group, target, method);
        }
        return false;
    }

    private swap(
        group: b.Group,
        target: string,
        method: SwapType.INNER | SwapType.REPLACE,
    ): boolean {
        /**
         * Replace the child of the given layout block (distinguished by `target`)
         * with the children of the given `View` fragment.
         *
         * Returns `true` if the target child was found and updated.
         *
         * Note: multiple fragment children can replace the single targeted block
         */
        for (const [idx, child] of this.children.entries()) {
            if (child.id === target) {
                if (method === SwapType.REPLACE) {
                    this.store.replace(idx, group);
                } else if (method === SwapType.INNER) {
                    this.store.inner(idx, group);
                } else {
                    throw `Method ${method} not recognised`;
                }
                return true;
            }
        }
        return false;
    }

    private insertAtEdge(group: b.Group, method: SwapType) {
        /**
         * Insert the children of a `View` fragment at the beginning or and of a layout block's children
         */
        if (method === SwapType.APPEND) {
            this.store.append(group);
        } else if (method === SwapType.PREPEND) {
            this.store.prepend(group);
        }
    }
}

export class Group extends LayoutBlock {
    public component = markRaw(VGroup);
    public columns: number;
    public name = "Group";

    public constructor(elem: any, figure: BlockFigure) {
        super(elem, figure);
        this.columns = +elem.attributes.columns;
        this.componentProps = { ...this.componentProps, columns: this.columns };
    }
}

export class Select extends LayoutBlock {
    public component = markRaw(VSelect);
    public type: string;
    public layout: string;
    public name = "Select";

    public constructor(elem: any, figure: BlockFigure) {
        super(elem, figure);
        const { label, type, layout } = elem.attributes;
        this.label = label;
        this.type = type;
        this.layout = layout;
        this.componentProps = { ...this.componentProps, type };
    }
}

export class Toggle extends LayoutBlock {
    public component = markRaw(VToggle);
    public name = "Toggle";

    public constructor(elem: any, figure: BlockFigure) {
        super(elem, figure);
        const { children, label } = elem.attributes;
        this.children = children;
        this.label = label;
        this.componentProps = { ...this.componentProps, label };
    }
}

export class Interactive extends LayoutBlock<ControlsField> {
    public component = markRaw(VInteractive);
    public name = "Interactive";

    public constructor(elem: any, figure: BlockFigure) {
        super(elem, figure);
        const {
            target,
            swap,
            submit_label,
            label,
            subtitle,
            function_id,
            trigger,
            timer,
        } = elem.attributes;
        this.store = useControlStore(this.children, target, swap)();

        this.componentProps = {
            ...this.componentProps,
            prompt: submit_label || "Submit",
            functionId: function_id,
            store: this.store,
            timer: +timer,
            label,
            subtitle,
            trigger,
        };
    }
}

export class View extends LayoutBlock {
    public id = "root";
    public name = "View";

    public constructor(elem: any, figure: BlockFigure) {
        super(elem, figure);
        const { layout, fragment } = elem.attributes;
        this.store = JSON.parse(fragment)
            ? undefined
            : useViewStore(this.children, layout)();
        this.componentProps = { ...this.componentProps, store: this.store };
    }
}

export const isView = (obj: any): obj is View => obj.name === "View";

export const isGroup = (obj: any): obj is Group => obj.name === "Group";

export const isSelect = (obj: any): obj is Select => obj.name === "Select";

export const isToggle = (obj: any): obj is Toggle => obj.name === "Toggle";

export const isInteractive = (obj: any): obj is Interactive =>
    obj.name === "Interactive";

export const isLayoutBlock = (obj: any): obj is LayoutBlock =>
    isView(obj) ||
    isSelect(obj) ||
    isToggle(obj) ||
    isView(obj) ||
    isGroup(obj) ||
    isInteractive(obj);
