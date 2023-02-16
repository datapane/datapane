import { AxiosError } from "axios";

export type Option = {
    name: string;
    id: string;
    onClick: () => void;
};

export type Section = {
    title?: string;
    options: Option[];
};

export const parseError = (e: unknown): string => {
    /**
     * Parse error object to be human-readable in app UI
     */
    if (e instanceof AxiosError) {
        const errHeader: string | undefined =
            e.response?.headers["datapane-error"];
        if (errHeader === "unknown-session") {
            return "Session validation failed: refreshing the browser may resolve this";
        }
        return e.toString();
    } else if (e instanceof Error) {
        return e.toString();
    } else if (typeof e === "string") {
        return e;
    } else {
        return "Unable to parse error; check console for more information";
    }
};
