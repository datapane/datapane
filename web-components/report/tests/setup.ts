import { afterAll, afterEach, beforeAll } from "vitest";
import { setupServer } from "msw/node";
import { rest } from "msw";
import fragmentJson from "./fixtures/fragment.json?raw";

const DISPATCH_FRAGMENT = JSON.parse(fragmentJson);

/*
 * Set up mock server for dispatch endpoint
 */

export const restHandlers = [
    rest.post("/app-rpc-call", (req: any, res: any, ctx: any) => {
        return res(ctx.status(200), ctx.json(DISPATCH_FRAGMENT));
    }),
];

const server = setupServer(...restHandlers);

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));

afterAll(() => server.close());

// Reset handlers after each test (important for test isolation)
afterEach(() => server.resetHandlers());
