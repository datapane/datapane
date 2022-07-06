import { EventType } from "../../../shared/types";

export const onAlpineReady = (fun: () => void) => {
    const funWrapper = () => {
        fun();
        window.removeEventListener("alpine:init", fun);
    };
    if ((window as any).Alpine) {
        fun();
    } else {
        window.addEventListener("alpine:init", funWrapper);
    }
};

export const noUndefinedVals = (obj: any): boolean => {
    return Object.entries(obj).every(([k, v]: any) => v !== undefined);
};

export const jsonParseIfStr = (fields: any): any => {
    try {
        return JSON.parse(fields);
    } catch (e) {
        return fields;
    }
};

export const dispatchDatapaneEvent = (
    eventType: EventType,
    payload: any
): void => {
    const event = new CustomEvent(eventType, { detail: payload });
    window.dispatchEvent(event);
};
