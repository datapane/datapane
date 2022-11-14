/**
 * Resources previously in old react Report component that are still needed by other
 * parts of the codebase
 */

import numeral from "numeral";
import { AxiosError, AxiosResponse } from "axios";
import promiseRetry from "promise-retry";

export const formatNumber = (n: number): string => {
    return numeral(n).format("0[.][0]a");
};

export type ReportWidth = "full" | "medium" | "narrow";

export type IReportFile = {
    name: string;
    id: string;
    tag: string;
    in_report: boolean;
};

export type IReportMetaData = {
    published: boolean;
    title: string;
    description: string;
};

export type IReport = IReportMetaData & {
    name: string;
    id: string;
    document: string;
    web_url: string;
    username: string;
    num_blocks: number;
    width?: ReportWidth;
    output_is_light_prose: boolean;
    output_style_header: string;
    report_files: IReportFile[];
};

export type IReportDocuments = {
    document: string;
    editable_document: string;
    report_files: IReportFile[];
};

export type RetryApiFunction = (
    retry: (error: AxiosError) => never,
    number: number,
    err: AxiosError,
) => never;

export const isReportDocuments = (obj: any): obj is IReportDocuments =>
    !!obj.editable_document;

export const retryPromise = <T>(
    callApi: () => Promise<AxiosResponse<T>>,
    retryApiFunction: RetryApiFunction,
): Promise<AxiosResponse<T>> => {
    return promiseRetry(
        (retry, number) => {
            return callApi().catch((error) => {
                return retryApiFunction(retry, number, error);
            });
        },
        {
            retries: 1000,
            minTimeout: 200,
            maxTimeout: 5000,
            factor: 3,
        },
    );
};
