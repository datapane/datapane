/**
 * Tests app swap operations (replace, inner, append, prepend)
 */
import { it, expect, describe, beforeEach } from "vitest";
import { createApp } from "vue";
import { createPinia } from "pinia";
import Report from "../src/components/ReportContainer.vue";
import { useRootStore } from "../src/data-model/root-store";
import replaceJson from "./fixtures/test-app.json?raw";
import { SwapType } from "../src/data-model/types";

const META = {
    isLightProse: false,
    mode: "VIEW" as "VIEW" | "EMBED",
    isOrg: false,
};

/*
 * Set up report app and pinia store. Note app is never mounted
 */

const app = createApp(Report, {});
const pinia = createPinia();
app.use(pinia);

const rootStore = useRootStore();
const appData = JSON.parse(replaceJson);

beforeEach(async () => {
    await rootStore.setReport(META, appData);
});

/*
 * Tests
 */

describe("App patch tests", () => {
    it("Performs a replace swap", async () => {
        const { report } = rootStore;

        await rootStore.update(
            "to-replace",
            SwapType.REPLACE,
            { msg: "foo" },
            "app.not_used",
        );

        // Replaced block should be a `Group` with ID inherited from target
        expect(report).toHaveProperty("children[1].name", "Group");
        expect(report).toHaveProperty("children[1].id", "to-replace");

        // New `Group` block should have a child with ID "replaced", i.e. the fragment response `View` content
        expect(report).toHaveProperty("children[1].children[0].id", "replaced");
    });

    it("Performs an inner swap", async () => {
        const { report } = rootStore;

        await rootStore.update(
            "group",
            SwapType.INNER,
            { msg: "foo" },
            "app.not_used",
        );

        // Initial target block should still exist
        expect(report).toHaveProperty("children[2].id", "group");

        // Existing `Group` block should have a child with ID "replaced", i.e. the fragment response `View` content
        expect(report).toHaveProperty("children[2].children[0].id", "replaced");
    });

    it("Performs an append swap", async () => {
        const { report } = rootStore;

        await rootStore.update(
            "group",
            SwapType.APPEND,
            { msg: "foo" },
            "app.not_used",
        );

        // Initial target block should still exist
        expect(report).toHaveProperty("children[2].id", "group");

        // Original `Group` child should still exist
        expect(report).toHaveProperty(
            "children[2].children[0].id",
            "inner-text",
        );

        // New `Group` block should have a new child with ID "replaced", i.e. the fragment response `View` content
        expect(report).toHaveProperty("children[2].children[1].id", "replaced");
    });

    it("Performs a prepend swap", async () => {
        const { report } = rootStore;

        await rootStore.update(
            "group",
            SwapType.PREPEND,
            { msg: "foo" },
            "app.not_used",
        );

        // Initial target block should still exist
        expect(report).toHaveProperty("children[2].id", "group");

        // Original `Group` child should still exist
        expect(report).toHaveProperty(
            "children[2].children[1].id",
            "inner-text",
        );

        // New `Group` block should have a new child with ID "replaced", i.e. the fragment response `View` content
        expect(report).toHaveProperty("children[2].children[0].id", "replaced");
    });
});
