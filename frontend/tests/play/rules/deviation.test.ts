import { describe, expect, it } from "vitest";

import { deviationsOf, insideGroup, outsideGroup } from "../../../src/play/rules/deviation";
import { someRules } from "../../fixtures/positions";
import { RULES_CATALOG } from "../../fixtures/rules";

describe("deviationsOf", () => {
    it("holds nothing while the record matches its scheme", () => {
        expect(deviationsOf(someRules(), someRules(), RULES_CATALOG)).toEqual([]);
    });

    it("carries the control a deviating setting takes and the standard it left", () => {
        const record = someRules({ premoves: false });
        const [deviation] = deviationsOf(record, someRules(), RULES_CATALOG);
        expect(deviation?.setting).toBe("premoves");
        expect(deviation?.group).toBe("turns");
        expect(deviation?.control).toEqual({ kind: "toggle", setting: "premoves", value: false });
        expect(deviation?.standard).toEqual({ kind: "toggle", setting: "premoves", value: true });
    });

    it("splits the deviations by the group that holds them", () => {
        const record = someRules({ seats: 4, premoves: false, board: "scrabble" });
        const deviations = deviationsOf(record, someRules(), RULES_CATALOG);
        expect(deviations.map((deviation) => deviation.setting)).toEqual(["seats", "premoves", "board"]);
        expect(outsideGroup(deviations, "table").map((held) => held.setting)).toEqual(["premoves", "board"]);
        expect(insideGroup(deviations, "table").map((held) => held.setting)).toEqual(["seats"]);
    });

    it("passes over a setting the catalog does not describe", () => {
        const record = someRules({ blanks: 4 });
        expect(deviationsOf(record, someRules(), RULES_CATALOG)).toEqual([]);
    });
});
