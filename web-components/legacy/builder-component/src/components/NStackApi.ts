import environment from "../environments/environments";
import axios, {
    AxiosError,
    AxiosInstance,
    AxiosResponse,
    AxiosRequestConfig,
} from "axios";
import { Semaphore } from "await-semaphore";
import { RetryApiFunction, retryPromise } from "./utils";

const semaphore = new Semaphore(1);

// TODO: Re-add user signed in / verified checks for non-firebase implementation.
const defaultRetryApiFunction: RetryApiFunction = (
    retry: any,
    number: any,
    err: any,
) => {
    // The default behaviour controlling when to retry an API request if it fails is
    // to retry only if a 401 error is returned.
    if (err.response && err.response.status === 401 && number < 2) {
        retry(err);
    }
    throw err;
};

export class NStackApi {
    protected apiClient: AxiosInstance;

    public constructor(
        options: { baseEndpoint: string } = { baseEndpoint: "api/" },
    ) {
        this.apiClient = axios.create({
            baseURL: environment["url"] + options.baseEndpoint,
            headers: {
                Accept: "application/json, text/html",
                "Content-Type": "application/json",
            },
            validateStatus: (status) => {
                return (status >= 200 && status < 300) || status === 412; // Handle schema mismatch as a resolution
            },
            // send all cookies in server requests
            withCredentials: true,
        });

        this.apiClient.interceptors.response.use(
            (response) => response,
            (error: AxiosError): Promise<AxiosError> => {
                return Promise.reject(error);
            },
        );
    }

    public get<T>(
        url: string,
        config?: AxiosRequestConfig,
        retryApiFunction = defaultRetryApiFunction,
    ): Promise<T> {
        return retryPromise(() => {
            return this.apiClient.get<T>(url, config);
        }, retryApiFunction).then((res: AxiosResponse<T>) => {
            return res.data;
        });
    }

    public delete<T>(
        url: string,
        retryApiFunction = defaultRetryApiFunction,
    ): Promise<T> {
        return retryPromise(() => {
            return this.apiClient.delete(url);
        }, retryApiFunction).then((res: AxiosResponse) => {
            return res.data;
        });
    }

    public post<T, U>(
        url: string,
        postObj: T,
        config?: any,
        retryApiFunction = defaultRetryApiFunction,
    ): Promise<U> {
        return retryPromise(() => {
            return this.apiClient.post<U>(url, postObj, config);
        }, retryApiFunction).then((res: any) => res.data);
    }

    public postReturnWholeResponse<T, U>(
        url: string,
        postObj: T,
        retryApiFunction = defaultRetryApiFunction,
    ): Promise<AxiosResponse<U>> {
        return retryPromise(() => {
            return this.apiClient.post<U>(url, postObj);
        }, retryApiFunction);
    }

    public patch<T extends { url: string }, TError = string | object>(
        patchObj: T,
        retryApiFunction = defaultRetryApiFunction,
    ): Promise<T> {
        return retryPromise(() => {
            return this.apiClient.patch<T>(patchObj.url, patchObj);
        }, retryApiFunction).then((d) => {
            return d.data;
        });
    }

    public put<T extends { url: string }>(
        putObj: T,
        retryApiFunction = defaultRetryApiFunction,
    ): Promise<T> {
        return retryPromise(() => {
            return this.apiClient.put<T>(putObj.url, putObj);
        }, retryApiFunction).then((d: any) => {
            return d.data;
        });
    }

    public blockingGet<T>(
        url: string,
        config?: AxiosRequestConfig,
    ): Promise<T> {
        return semaphore.acquire().then((release) => {
            return this.get<T>(url, config).finally(release);
        });
    }
}

export const NStackApiInstance = new NStackApi();
export const NStackWebApiInstance = new NStackApi({ baseEndpoint: "" });
