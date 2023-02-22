import { useControlStore, useLayoutStore, useViewStore } from "../layout-store";
import { markRaw } from "vue";
import VGroup from "../../components/layout/Group.vue";
import VSelect from "../../components/layout/SelectBlock.vue";
import VToggle from "../../components/layout/Toggle.vue";
import { Block, BlockFigure } from "./leaf-blocks";
import VFunction from "../../components/controls/Function.connector.vue";
import { ControlsField } from "./interactive";
import * as b from "./index";
import { SwapType } from "../types";
import { EmptyObject } from "../root-store";

export abstract class ParentBlock<T extends Block = Block> extends Block {
    /**
     * A non-atomic block that has children
     */
    public children: T[];

    public constructor(elem: any, figure: BlockFigure) {
        super(elem, figure);
        const { children } = elem.attributes;
        this.children = children;
    }
}

export abstract class LayoutBlock<
    T extends Block = Block,
> extends ParentBlock<T> {
    /**
     * A non-atomic block which uses children to control layout, e.g. in columns, selects, pages
     */
    public store: any;

    public constructor(elem: any, figure: BlockFigure) {
        super(elem, figure);
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
                    throw new Error(`Method ${method} not recognised`);
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
    public name = "Group";

    public constructor(elem: any, figure: BlockFigure) {
        super(elem, figure);
        const { columns, widths, valign } = elem.attributes;
        this.componentProps = {
            ...this.componentProps,
            widths: widths ? JSON.parse(widths) : undefined,
            columns: +columns,
            valign,
        };
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

export class FunctionBlock extends ParentBlock<ControlsField> {
    public store: any;

    public component = markRaw(VFunction);
    public name = "Function";

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

/* Block/element type guards and checks */

export const isFunctionElem = (elem: Block | b.Elem): boolean =>
    elem.name === "Function";

export const isGroupElem = (elem: Block | b.Elem): boolean =>
    elem.name === "Group";

export const isSelectElem = (elem: Block | b.Elem): boolean =>
    elem.name === "Select";

export const isToggleElem = (elem: Block | b.Elem): boolean =>
    elem.name === "Toggle";

export const isViewElem = (elem: Block | b.Elem | EmptyObject): boolean =>
    elem.name === "View";

export const isParentElem = (elem: Block | b.Elem): boolean =>
    isSelectElem(elem) ||
    isToggleElem(elem) ||
    isViewElem(elem) ||
    isGroupElem(elem) ||
    isFunctionElem(elem);

export const isLayoutBlock = (block: Block): block is LayoutBlock =>
    block instanceof LayoutBlock;

export const isView = (block: Block | EmptyObject): block is View =>
    block instanceof View;
