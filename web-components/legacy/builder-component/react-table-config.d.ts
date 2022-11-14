import {
    UseExpandedRowProps,
    UseFiltersColumnOptions,
    UseFiltersColumnProps,
    UseGroupByCellProps,
    UseGroupByRowProps,
    UsePaginationInstanceProps,
    UsePaginationOptions,
    UsePaginationState,
    UseRowSelectRowProps,
    UseRowStateCellProps,
    UseRowStateRowProps,
    UseSortByColumnOptions,
    UseSortByColumnProps,
    UseSortByHooks,
    UseSortByInstanceProps,
    UseSortByOptions,
    UseSortByState,
} from "react-table";

/**
 * Type declarations for react-table
 * See https://github.com/DefinitelyTyped/DefinitelyTyped/blob/bab0a49d79fb3cd850db3174d0ed91a85be7f433/types/react-table/Readme.md
 */

/* ESlint doesn't permit empty interfaces by default, which is the method that react-table recommends. */
/* eslint-disable @typescript-eslint/no-empty-interface */

declare module "react-table" {
    export interface TableOptions<D extends Record<string, unknown>>
        extends UsePaginationOptions<D>,
            UseSortByOptions<D>,
            Record<string, any> {}

    export interface Hooks<
        D extends Record<string, unknown> = Record<string, unknown>,
    > extends UseSortByHooks<D> {}

    export interface TableInstance<
        D extends Record<string, unknown> = Record<string, unknown>,
    > extends UsePaginationInstanceProps<D>,
            UseSortByInstanceProps<D> {}

    export interface TableState<
        D extends Record<string, unknown> = Record<string, unknown>,
    > extends UsePaginationState<D>,
            UseSortByState<D> {}

    export interface ColumnInterface<
        D extends Record<string, unknown> = Record<string, unknown>,
    > extends UseFiltersColumnOptions<D>,
            UseSortByColumnOptions<D> {}

    export interface ColumnInstance<
        D extends Record<string, unknown> = Record<string, unknown>,
    > extends UseFiltersColumnProps<D>,
            UseSortByColumnProps<D> {}

    export interface Cell<
        D extends Record<string, unknown> = Record<string, unknown>,
        V = any,
    > extends UseGroupByCellProps<D>,
            UseRowStateCellProps<D> {}

    export interface Row<
        D extends Record<string, unknown> = Record<string, unknown>,
    > extends UseExpandedRowProps<D>,
            UseGroupByRowProps<D>,
            UseRowSelectRowProps<D>,
            UseRowStateRowProps<D> {}
}
