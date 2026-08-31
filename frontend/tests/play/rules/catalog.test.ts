import { describe, expect, it } from "vitest";

import { catalogOf, EMPTY_CATALOG, groupOf } from "../../../src/play/rules/catalog";
import { anAllowance } from "../../fixtures/positions";

const ALLOWANCES = [
    anAllowance({ setting: "seats", group: "table" }),
    anAllowance({ setting: "total_seconds", group: "table", kind: "seconds", offered: [60] }),
    anAllowance({ setting: "dictionary", group: "words", kind: "choice", choices: ["sjp"] }),
    anAllowance({ setting: "validate_on_play", group: "words", kind: "toggle" }),
];

describe("catalogOf", () => {
    it("keeps the served order of settings and groups", () => {
        const catalog = catalogOf(ALLOWANCES);
        expect(catalog.settings).toEqual(["seats", "total_seconds", "dictionary", "validate_on_play"]);
        expect(catalog.groups.map((rows) => rows.group)).toEqual(["table", "words"]);
    });

    it("gathers each group's settings", () => {
        const catalog = catalogOf(ALLOWANCES);
        expect(groupOf(catalog, "table")).toEqual(["seats", "total_seconds"]);
        expect(groupOf(catalog, "words")).toEqual(["dictionary", "validate_on_play"]);
        expect(groupOf(catalog, "letters")).toEqual([]);
    });

    it("looks an allowance up by its setting", () => {
        const catalog = catalogOf(ALLOWANCES);
        expect(catalog.bySetting.get("seats")?.group).toBe("table");
        expect(catalog.bySetting.get("blanks")).toBeUndefined();
    });

    it("holds nothing before the offerings arrive", () => {
        expect(EMPTY_CATALOG.settings).toEqual([]);
        expect(groupOf(EMPTY_CATALOG, "table")).toEqual([]);
    });
});
