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
    if (e instanceof Error) {
        return e.toString();
    } else if (typeof e === "string") {
        return e;
    } else {
        return "Unable to parse error; check console for more information";
    }
};
