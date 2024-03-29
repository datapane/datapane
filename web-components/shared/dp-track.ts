import environment from "../report/src/environment";
import urljoin from "url-join";
import posthog from "posthog-js";
import FastMutex from "fast-mutex";

type ReportViewPayload = {
    id: string;
    web_url: string;
    is_embed: boolean;
};

const API_HOST = "https://events.datapane.com";
// NOTE - this will use prod as the url for local reports
const KPIS_ENDPOINT = urljoin(
    environment.url ?? "https://cloud.datapane.com/",
    "dp-kpis/",
);
//const KPIS_ENDPOINT = "http://localhost:8090/dp-kpis/";
const LOCK_NAME = "ph_datapane_store";
const mutex = new FastMutex();

function getCookie(n: string): string | undefined {
    // https://developer.mozilla.org/en-US/docs/Web/API/Document/cookie
    const rawCookie = document.cookie
        .split("; ")
        .find((row) => row.startsWith(n))
        ?.split("=")[1];

    return rawCookie ? decodeURIComponent(rawCookie) : undefined;
}

export const setupPostHog = async (
    apiKey: string,
    userId?: string,
    groupId?: string,
): Promise<void> => {
    try {
        await mutex.lock(LOCK_NAME);
        posthog.init(apiKey, {
            api_host: API_HOST,
            loaded: async (posthog: any) => {
                /* We need to do this to use elsewhere in more dynamic ways, outside the scope of this file */
                window.posthog = posthog;
                userId && posthog.identify(userId);
                groupId && posthog.group("company", groupId);
                await mutex.release(LOCK_NAME);
            },
        });
    } catch (e) {
        console.error("Posthog setup error", e);
        await mutex.release(LOCK_NAME);
    }
};

/**
 * async safely get the global posthog instance, sleeping until ready
 * (posthog is initialised in the HTML HEAD, via inline JS)
 * Could be disabled if on an enterprise instance - i.e. POSTHOG_API_KEY is None
 * */
const getPostHog = async (): Promise<any> => {
    if (window.hasPosthog) {
        // async loop to get window.posthog
        let count = 0; // debugging info
        console.log(`PH loop - ${count}`);
        while (!window.posthog) {
            count++;
            console.log(`PH loop - ${count}`);
            if (count >= 10) {
                console.log("PH not initialised in time, skipping");
                break;
            }
            await new Promise((r) => setTimeout(r, 2000));
        }
        return window.posthog;
    }
    return null;
};

export const getDeviceId = async (): Promise<string> => {
    // await for posthog to ensure cookie is configured first
    await getPostHog();
    const device = getCookie(LOCK_NAME);

    if (!device) {
        throw new Error("Couldn't access device ID");
    }

    return JSON.parse(device).distinct_id;
};

const asyncPosthogCapture = async (event_name: string, properties: any) => {
    // "spawn" an async call to posthog
    const posthog = await getPostHog();
    if (posthog) {
        /* As this is called from React, we need to use the version on window. Putting this in try/catch in case
         * someone has a custom adblock or fingerprint breaks in the future, as we don't want to blow up the report component. */
        try {
            posthog.capture(event_name, properties);
        } catch {
            console.log(`Could not send ${event_name} event to PostHog`);
        }
    }
};

/** Generic event handling via dp-server kpis endpoint, e.g. billing events */
const asyncDPTrackEvent = async (
    event: string,
    properties: object,
    includeDeviceId: boolean = true,
) => {
    try {
        // create the payload
        const payload: {
            event: string;
            unique_id?: string;
            properties: object;
        } = { event: event, properties: properties };
        if (includeDeviceId) {
            payload.unique_id = await getDeviceId();
        }

        window.navigator.sendBeacon(KPIS_ENDPOINT, JSON.stringify(payload));
    } catch (e) {
        console.error("An event error occurred", e);
    }
};

/** Used for tracking usage for billing and for PostHog analytics */
export const trackReportView = (properties: ReportViewPayload) => {
    asyncPosthogCapture("Report View", properties);
};

export const trackLocalReportView = (
    event: "CLI_REPORT_VIEW" | "SERVED_REPORT_VIEW",
) => {
    if (!window.dpLocalViewEvent) {
        return;
    }
    asyncDPTrackEvent(
        event,
        {
            author_id: window.dpAuthorId,
            report_id: window.dpReportId,
        },
        false,
    );
};
