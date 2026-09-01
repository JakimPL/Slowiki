import { describe, expect, it } from "vitest";

import type { OfferingsResponse, TableDescription } from "../../../src/api/tables";
import { inspecting } from "../../../src/play/rules/inspecting";
import { aDescription, anOffering, someRules } from "../../fixtures/positions";
import { ALLOWANCES } from "../../fixtures/rules";

const ARRIVALS: OfferingsResponse = {
    offerings: [anOffering({ name: "literaki" })],
    code: { length: 6, alphabet: "ABCDEFGHIJKLMNOPRSTUWYZ" },
    allowances: ALLOWANCES,
};

function described(rules: TableDescription["rules"]): TableDescription {
    return aDescription({ rules });
}

describe("inspecting", () => {
    it("holds nothing before the offerings or the invitation answer", () => {
        expect(inspecting(null, described(someRules()))).toBeNull();
        expect(inspecting(ARRIVALS, null)).toBeNull();
    });

    it("holds nothing for a table whose scheme is no longer offered", () => {
        const foreign = aDescription({ scheme: "retired", rules: someRules() });
        expect(inspecting(ARRIVALS, foreign)).toBeNull();
    });

    it("reads the settled rules against the scheme they came from", () => {
        const held = inspecting(ARRIVALS, described(someRules({ premoves: false, seats: 3 })));
        expect(held?.scheme).toBe("literaki");
        expect(held?.record?.premoves).toBe(false);
        expect(held?.deviations.map((deviation) => deviation.setting)).toEqual(["seats", "premoves"]);
    });

    it("offers no way to change what it reads", () => {
        const held = inspecting(ARRIVALS, described(someRules()));
        expect(held?.presets).toEqual([]);
        expect(held?.entries).toEqual([]);
        expect(held?.unsaved).toBe(false);
    });
});
